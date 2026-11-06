#!/usr/bin/python3
"""Publish expiry data for TLS certificates served by local Caddy."""

import json
import os
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


TARGETS_PATH = Path("/etc/certificate-monitor/targets.json")
METRIC_PATH = Path("/var/lib/prometheus/node-exporter/caddy-certificates.prom")
OPENSSL_TIMEOUT_SECONDS = 10
CERTIFICATE_PATTERN = re.compile(
    rb"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----", re.DOTALL
)


def escape_label(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def read_expiry_timestamp(hostname: str) -> float:
    result = subprocess.run(
        [
            "openssl",
            "s_client",
            "-connect",
            "127.0.0.1:443",
            "-servername",
            hostname,
            "-showcerts",
        ],
        input=b"",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=OPENSSL_TIMEOUT_SECONDS,
    )
    match = CERTIFICATE_PATTERN.search(result.stdout)
    if match is None:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(detail or "TLS endpoint did not return a certificate")

    certificate = subprocess.run(
        ["openssl", "x509", "-noout", "-enddate"],
        input=match.group(0),
        capture_output=True,
        check=True,
        timeout=OPENSSL_TIMEOUT_SECONDS,
    )
    end_date = certificate.stdout.decode("ascii").strip().removeprefix("notAfter=")
    expires_at = datetime.strptime(end_date, "%b %d %H:%M:%S %Y %Z").replace(
        tzinfo=timezone.utc
    )
    return expires_at.timestamp()


def render_metrics(targets: list[dict[str, str]]) -> str:
    lines = [
        "# HELP maintenance_tls_certificate_expiry_timestamp_seconds Certificate expiry timestamp from the local Caddy TLS endpoint.",
        "# TYPE maintenance_tls_certificate_expiry_timestamp_seconds gauge",
        "# HELP maintenance_tls_certificate_probe_success Whether the local Caddy TLS endpoint returned a certificate.",
        "# TYPE maintenance_tls_certificate_probe_success gauge",
    ]

    for target in targets:
        service = escape_label(target["service"])
        hostname = escape_label(target["hostname"])
        try:
            expiry_timestamp = read_expiry_timestamp(target["hostname"])
            probe_success = 1
        except (OSError, RuntimeError, subprocess.SubprocessError, ValueError):
            expiry_timestamp = float("nan")
            probe_success = 0

        labels = f'service="{service}",hostname="{hostname}"'
        lines.append(
            f"maintenance_tls_certificate_expiry_timestamp_seconds{{{labels}}} {expiry_timestamp}"
        )
        lines.append(
            "maintenance_tls_certificate_probe_success"
            f'{{service="{service}",hostname="{hostname}"}} {probe_success}'
        )

    return "\n".join(lines) + "\n"


def main() -> None:
    targets = json.loads(TARGETS_PATH.read_text(encoding="utf-8"))
    content = render_metrics(targets)
    METRIC_PATH.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_path = tempfile.mkstemp(
        prefix=".caddy-certificates-", dir=METRIC_PATH.parent, text=True
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as output:
            output.write(content)
        os.chmod(temporary_path, 0o644)
        os.replace(temporary_path, METRIC_PATH)
    finally:
        if os.path.exists(temporary_path):
            os.unlink(temporary_path)


if __name__ == "__main__":
    main()
