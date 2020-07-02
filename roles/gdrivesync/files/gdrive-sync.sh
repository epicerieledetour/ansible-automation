rclone --config "/home/gdrive/rclone.conf" --drive-shared-with-me sync remote: /home/gdrive/data/

# Launch backup
/bin/bash /usr/bin/backup/backup.sh  # TODO: should be linked by a systemd timer
