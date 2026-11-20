#!/usr/bin/python3
"""Update Borg backup freshness metrics when borgmatic hooks fire."""

import fcntl
import json
import os
import tempfile
import time
from pathlib import Path


TARGETS_DIR = Path("/etc/borg-backup-monitor/repositories.d")
STATE_PATH = Path("/var/lib/borg-backup-monitor/state.json")
LOCK_PATH = Path("/var/lib/borg-backup-monitor/metrics.lock")
METRIC_PATH = Path("/var/lib/prometheus/node-exporter/borg-backups.prom")


def escape_label(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def load_state() -> dict[str, dict[str, float | bool]]:
    try:
        content = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}
    if not isinstance(content, dict):
        return {}

    # Preserve successful-backup timestamps written by the previous poller.
    state: dict[str, dict[str, float | bool]] = {}
    for repository, value in content.items():
        if not isinstance(value, dict):
            continue
        timestamp = value.get("last_success_timestamp", value.get("last_archive_timestamp", 0.0))
        has_archive = value.get("has_archive", timestamp > 0)
        state[str(repository)] = {
            "last_success_timestamp": float(timestamp),
            "has_archive": bool(has_archive),
            "last_attempt_timestamp": float(value.get("last_attempt_timestamp", 0.0)),
            "last_attempt_success": bool(value.get("last_attempt_success", True)),
        }
    return state


def load_targets() -> list[dict[str, object]]:
    targets = []
    for path in sorted(TARGETS_DIR.glob("*.json")):
        target = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(target, dict):
            raise ValueError(f"Invalid Borg metrics target in {path}")
        targets.append(target)
    return targets


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
) -> str:
    lines = [
        "# HELP maintenance_borg_repository_last_archive_timestamp_seconds Unix timestamp of the last successful Borg backup.",
        "# TYPE maintenance_borg_repository_last_archive_timestamp_seconds gauge",
        "# HELP maintenance_borg_repository_has_archive Whether a successful Borg backup is known to exist.",
        "# TYPE maintenance_borg_repository_has_archive gauge",
        "# HELP maintenance_borg_repository_stale_after_seconds Configured age after which a Borg repository backup is stale.",
        "# TYPE maintenance_borg_repository_stale_after_seconds gauge",
        "# HELP maintenance_borg_repository_last_attempt_timestamp_seconds Unix timestamp of the last borgmatic run outcome recorded by a hook.",
        "# TYPE maintenance_borg_repository_last_attempt_timestamp_seconds gauge",
        "# HELP maintenance_borg_repository_last_attempt_success Whether the last borgmatic run outcome recorded by a hook succeeded.",
        "# TYPE maintenance_borg_repository_last_attempt_success gauge",
    ]

    for target in targets:
        repository = str(target["repository"])
        labels = ",".join(
            f'{name}="{escape_label(str(target[name]))}"'
            for name in ("store", "source", "backup_set", "repository")
        )
        previous = state.get(repository, {})
        last_success = float(previous.get("last_success_timestamp", 0.0))
        has_archive = bool(previous.get("has_archive", last_success > 0))
        last_attempt = float(previous.get("last_attempt_timestamp", 0.0))
        attempt_success = int(bool(previous.get("last_attempt_success", True)))
        lines.extend(
            [
                f"maintenance_borg_repository_last_archive_timestamp_seconds{{{labels}}} {last_success}",
                f"maintenance_borg_repository_has_archive{{{labels}}} {int(has_archive)}",
                f"maintenance_borg_repository_stale_after_seconds{{{labels}}} {int(target['stale_after_seconds'])}",
                f"maintenance_borg_repository_last_attempt_timestamp_seconds{{{labels}}} {last_attempt}",
                f"maintenance_borg_repository_last_attempt_success{{{labels}}} {attempt_success}",
            ]
        )

    return "\n".join(lines) + "\n"


def update_metrics(action: str, repository_path: str | None = None) -> None:
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOCK_PATH.open("a", encoding="utf-8") as lock_file:
        fcntl.flock(lock_file, fcntl.LOCK_EX)
        targets = load_targets()
        state = load_state()

        if action != "initialize":
            if repository_path is None:
                raise ValueError("A repository path is required for hook updates")
            target = next(
                (
                    target
                    for target in targets
                    if str(target.get("repository_path")) == repository_path
                ),
                None,
            )
            if target is None:
                raise ValueError(f"No Borg metrics target matches repository {repository_path!r}")

            repository = str(target["repository"])
            previous = state.get(repository, {})
            now = time.time()
            has_archive = bool(previous.get("has_archive", False))
            last_success = float(previous.get("last_success_timestamp", 0.0))
            if action == "success":
                has_archive = True
                last_success = now
            state[repository] = {
                "last_success_timestamp": last_success,
                "has_archive": has_archive,
                "last_attempt_timestamp": now,
                "last_attempt_success": action == "success",
            }

        atomic_write(STATE_PATH, json.dumps(state, sort_keys=True) + "\n", 0o600)
        atomic_write(METRIC_PATH, render_metrics(targets, state), 0o644)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("initialize", "success", "failure"))
    parser.add_argument("repository_path", nargs="?")
    arguments = parser.parse_args()
    update_metrics(arguments.action, arguments.repository_path)


if __name__ == "__main__":
    main()
