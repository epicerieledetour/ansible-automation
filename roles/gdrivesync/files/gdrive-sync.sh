#!/usr/bin/bash

rclone --config "/usr/local/etc/rclone/rclone.conf" --drive-shared-with-me sync remote: /srv/rclone/gdrive-sync

# Launch backup
/bin/bash /usr/bin/backup/backup.sh  # TODO: should be linked by a systemd timer
