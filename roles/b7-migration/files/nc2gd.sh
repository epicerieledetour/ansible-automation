#!/bin/sh

NC2DG_CSV_URL="https://docs.google.com/spreadsheets/d/e/2PACX-1vQNfoD8Y0N0KU1IJtu1BFqDdC9RcH7fFDrFiLUvTs29ZDYcv4aUGAhyVmbD6oElwwyw-q9wdzygJpJ8/pub?output=csv"

_bin=/home/pi/nc2gd/bin/nc2gd.py
_tmpdir=/srv/tmp/nc2gd
_tmpncdir="$_tmpdir/nc"
_csv="$_tmpdir"/dest.csv
_ncdata="/srv/rsync/nc.batiment7.org/srv/nc-data"
_gdroot="/srv/rclone/B7"
_migratesh="$_tmpdir"/migrate.sh
_migratelog="$_tmpdir"/migrate.log

rsync --archive --progress --human-readable romeo@nc.batiment7.org:/srv/nc-data /srv/rsync/nc.batiment7.org/srv
sudo rm -r "$_tmpncdir"
mkdir -p "$_tmpncdir"
wget "$NC2DG_CSV_URL" -O "$_csv"
"$_bin" "$_csv" "$_ncdata" "$_tmpncdir" "$_gdroot" > "$_migratesh"
sudo rm -r "$_gdroot"/*/*
sudo sh "$_migratesh"

