#!/usr/bin/python3
"""Publish the most recent completed APT transaction that upgraded packages."""

import gzip
import glob
import os
import re
import tempfile
from datetime import datetime


HISTORY_GLOB = "/var/log/apt/history.log*"
METRIC_PATH = "/var/lib/prometheus/node-exporter/apt-upgrade.prom"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def transactions(path):
    opener = gzip.open if path.endswith(".gz") else open
    try:
        with opener(path, "rt", encoding="utf-8", errors="replace") as stream:
            contents = stream.read()
    except (OSError, EOFError):
        return

    for block in re.split(r"\n\s*\n", contents):
        fields = {}
        for line in block.splitlines():
            if ": " in line:
                key, value = line.split(": ", 1)
                fields[key] = value
        if "Upgrade" not in fields or "End-Date" not in fields or "Error" in fields:
            continue
        try:
            yield datetime.strptime(fields["End-Date"], DATE_FORMAT).timestamp()
        except ValueError:
            continue


def main():
    timestamps = [timestamp for path in glob.glob(HISTORY_GLOB) for timestamp in transactions(path)]
    last_upgrade = max(timestamps, default=0)
    content = (
        "# HELP maintenance_apt_last_upgrade_timestamp_seconds Unix timestamp of the last completed APT transaction that upgraded packages.\n"
        "# TYPE maintenance_apt_last_upgrade_timestamp_seconds gauge\n"
        f"maintenance_apt_last_upgrade_timestamp_seconds {last_upgrade}\n"
    )

    directory = os.path.dirname(METRIC_PATH)
    os.makedirs(directory, exist_ok=True)
    fd, temporary_path = tempfile.mkstemp(prefix=".apt-upgrade-", dir=directory, text=True)
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
