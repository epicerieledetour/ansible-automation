#!/bin/bash
_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

_secret="$_dir/.vault_password.d/encrypted-vault-password-for-$USER"

# Finding the user ssh pub key
# .../keys/username-id_keytype.pub
_pubkey=`realpath "$_dir/keys/$USER-*.pub"`

# Extracting the pub key name
# username-id_keytype.pub 
_privkey=`basename $_pubkey`

# Stripping the user username
# id_keytype.pub
_privkey="${_privkey##*-}"

# Stripping the .pub extension
# This gives the private ssh key basename
# id_keytype.pub
_privkey="${_privkey%.pub}"

# Make the path to the ssh private key
# matching the public ssh key that was used
# to encrypt the vault passwordy
# /home/username/.ssh/id_keytype
_privkey="$HOME/.ssh/$_privkey"

# Now we can decrypt the vault password
age -d -i $_privkey "$_secret"

