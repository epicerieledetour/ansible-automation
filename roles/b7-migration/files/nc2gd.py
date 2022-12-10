#!/usr/bin/python3

import argparse
import csv
import os
from pathlib import Path

parser = argparse.ArgumentParser(
                    prog = 'nc2gd.py',
                    description = 'Generate script to migrate B7 NextCloud documents to B7-DRIVES')

parser.add_argument('db', help='The CSV storing the migration infos')
parser.add_argument('ncroot', help='The root of the NextCloud drive folder')
parser.add_argument('tmproot', help="Before migration, nexcloud file will be hard linked into this folder")
parser.add_argument('gdroot', help='The root of the Google Drives folder')
parser.add_argument('--script-dir', default="/tmp/nc2gd", help='The destination folder to store the generated scripts to')

args = parser.parse_args()

template_header = """#!/bin/bash

mkdir -vp "{linkroot}"
rm -rf "{linkroot}/*"

for _ncfiles in `ls -d {ncroot}/*/files`
do
  _n=`dirname $_ncfiles`
  _user=`basename $_n`
  mkdir -vp "{linkroot}/$_user"
  cp -lR $_ncfiles "{linkroot}/$_user/files"
done
"""

template_row = """
mkdir -vp "{dstdir}"
mv "{linkpath}" "{dstpath}"
"""

template_doc_not_exist = r"""echo -e "\e[31m{relsrcpath} should go to {dstdir}, but does not exist\e[0m" >&2

"""

template_footer = """
echo "rsync'ing {tmpgdroot}/ to {gdroot}"
rsync --archive --progress --human-readable --delete "{tmpgdroot}/" "{gdroot}"

echo "If files are listed below, they have not been migrated:"
echo -e "\e[31m"
find "{linkroot}" -type f
echo -e "\e[0m"
"""

def s(d):
  return dict((k, str(v)) for k, v in d.items())

def make_args(args):
  ncroot = Path(args.ncroot)
  gdroot = Path(args.gdroot)
  tmproot = Path(args.tmproot)
  linkroot = tmproot / "link"

  return {
    "ncroot": ncroot,
    "gdroot": gdroot,
    "tmproot": tmproot,

    "tmpgdroot": tmproot / "B7",
    "linkroot": linkroot,
    "nomigratedir": tmproot / "nomigrate",
    "unknownmigratedir": tmproot / "unknownmigrate",
  }


def make_row(args, row):
  ncroot = args["ncroot"]
  tmpgdroot = args["tmpgdroot"]
  tmproot = args["tmproot"]
  linkroot = tmproot / "link"
  relsrcpath = Path(row["Full path"])

  ret = {
    "relsrcpath": relsrcpath,
    "relsrcdir": relsrcpath.parent,

    "srcpath": ncroot / relsrcpath,
    "linkpath": linkroot / relsrcpath,
  }

  ret["dstpath"] = tmpgdroot / row["Destination"] / "nextcloud-migration"
  if row["Destination"] == "":
    ret["dstpath"] = args["unknownmigratedir"]
  if row["Destination"] == "Pas de migration":
    ret["dstpath"] = args["nomigratedir"]
  
  ret["dstpath"] = ret["dstpath"] / relsrcpath
  ret["dstdir"] = ret["dstpath"].parent

  return ret


def process_row(row):
    file_exists = os.path.exists(row["srcpath"])
    template = template_row if file_exists else template_doc_not_exist
    print(template.format(**s(row)))


with open(args.db, newline='') as fp:
    args = make_args(args)
    print(template_header.format(**s(args)))
    reader = csv.DictReader(fp)
    for row in reader:
        row.update(args)
        process_row(make_row(args, row))
    print(template_footer.format(**s(args)))

#with open("dir.txt") as fp:
#    for l in fp:
#        print('mkdir -p "/tmp/nc2gd/ncdrives/{}"'.format(l.replace("\n","")))
#for name in ("B7-COMPTA", "B7-CONFLITS", "B7NEXTCLOUD", "B7-RH", "B7-5"):
#    print("mkdir -p /tmp/nc2gd/gdrives/{}".format(name))
#with open("fil.txt") as fp:
#    for l in fp:
#        print('touch "/tmp/nc2gd/ncdrives/{}"'.format(l.replace("\n", "")))

