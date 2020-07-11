#!/usr/bin/bash

rclone --config "/usr/local/etc/rclone/rclone.conf" --drive-shared-with-me sync remote: /srv/rclone/gdrive-sync
