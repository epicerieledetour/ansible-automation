#!/usr/bin/python3
"""Publish Borg repository freshness and reachability metrics."""

import json
import os
import signal
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path


TARGETS_DIR = Path("/etc/borg-backup-monitor/repositories.d")
STATE_PATH = Path("/var/lib/borg-backup-monitor/state.json")
METRIC_PATH = Path("/var/lib/prometheus/node-exporter/borg-backups.prom")
COMMAND_TIMEOUT_SECONDS = 30


def escape_label(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def load_state() -> dict[str, dict[str, float | bool]]:
    try:
        content = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}
    return content if isinstance(content, dict) else {}


def parse_archives(payload: object) -> list[dict[str, object]]:
    if isinstance(payload, list):
        archives: list[dict[str, object]] = []
        for item in payload:
            archives.extend(parse_archives(item))
        return archives
    if isinstance(payload, dict):
        archives = payload.get("archives")
        if isinstance(archives, list):
            return [item for item in archives if isinstance(item, dict)]
        if any(key in payload for key in ("end", "start", "time")):
            return [payload]
    raise ValueError("Borgmatic returned JSON without an archive list")


def archive_timestamp(archive: dict[str, object]) -> float:
    value = archive.get("end") or archive.get("time") or archive.get("start")
    if not isinstance(value, str):
        raise ValueError("Borg archive has no recognized timestamp")
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    timestamp = datetime.fromisoformat(value)
    if timestamp.tzinfo is None:
        # Borg 1.x JSON timestamps use local time without an offset.
        # Interpret them in this host's configured timezone, not as UTC.
        timestamp = timestamp.astimezone()
    return timestamp.timestamp()


def query_repository(target: dict[str, object]) -> list[dict[str, object]]:
    command = [
        "/usr/bin/borgmatic",
        "--config",
        str(target["config"]),
        "list",
        "--json",
        "--last",
        "1",
        "--repository",
        str(target["repository_label"]),
    ]
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
        text=True,
    )
    try:
        stdout, _stderr = process.communicate(timeout=COMMAND_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.communicate()
        raise TimeoutError("Borg repository query timed out")
    if process.returncode != 0:
        raise RuntimeError(f"Borgmatic exited with status {process.returncode}")
    return parse_archives(json.loads(stdout))


def atomic_write(path: Path, content: str, mode: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_path = tempfile.mkstemp(
        prefix=f".{path.name}-", dir=path.parent, text=True
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as output:
            output.write(content)
        os.chmod(temporary_path, mode)
        os.replace(temporary_path, path)
    finally:
        if os.path.exists(temporary_path):
            os.unlink(temporary_path)


def render_metrics(
    targets: list[dict[str, object]], state: dict[str, dict[str, float | bool]]
) -> tuple[str, dict[str, dict[str, float | bool]]]:
    lines = [
        "# HELP maintenance_borg_repository_last_archive_timestamp_seconds End timestamp of the latest known successful archive in a Borg repository.",
        "# TYPE maintenance_borg_repository_last_archive_timestamp_seconds gauge",
        "# HELP maintenance_borg_repository_probe_success Whether the Borg repository was reachable and queried successfully.",
        "# TYPE maintenance_borg_repository_probe_success gauge",
        "# HELP maintenance_borg_repository_has_archive Whether a latest archive is known to exist in the repository.",
        "# TYPE maintenance_borg_repository_has_archive gauge",
        "# HELP maintenance_borg_repository_stale_after_seconds Configured age after which a Borg repository backup is stale.",
        "# TYPE maintenance_borg_repository_stale_after_seconds gauge",
    ]

    for target in targets:
        repository = str(target["repository"])
        labels = ",".join(
            f'{name}="{escape_label(str(target[name]))}"'
            for name in ("store", "source", "backup_set", "repository")
        )
        previous = state.get(repository, {})
        last_archive = float(previous.get("last_archive_timestamp", 0.0))
        has_archive = bool(previous.get("has_archive", False))
        probe_success = 0

        try:
            archives = query_repository(target)
            probe_success = 1
            if archives:
                last_archive = max(archive_timestamp(archive) for archive in archives)
                has_archive = True
            else:
                has_archive = False
            state[repository] = {
                "last_archive_timestamp": last_archive,
                "has_archive": has_archive,
            }
        except (
            OSError,
            RuntimeError,
            TimeoutError,
            ValueError,
            subprocess.SubprocessError,
        ):
            # Retain the last known archive timestamp, while reporting the
            # current failed probe separately so Grafana can show ERROR.
            pass

        lines.extend(
            [
                f"maintenance_borg_repository_last_archive_timestamp_seconds{{{labels}}} {last_archive}",
                f"maintenance_borg_repository_probe_success{{{labels}}} {probe_success}",
                f"maintenance_borg_repository_has_archive{{{labels}}} {int(has_archive)}",
                f"maintenance_borg_repository_stale_after_seconds{{{labels}}} {int(target['stale_after_seconds'])}",
            ]
        )

    return "\n".join(lines) + "\n", state


def main() -> None:
    targets = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(TARGETS_DIR.glob("*.json"))
    ]
    state = load_state()
    metrics, state = render_metrics(targets, state)
    atomic_write(STATE_PATH, json.dumps(state, sort_keys=True) + "\n", 0o600)
    atomic_write(METRIC_PATH, metrics, 0o644)


if __name__ == "__main__":
    main()
