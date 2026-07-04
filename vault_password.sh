#!/bin/bash
_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
gpg --batch --use-agent --decrypt "$_dir/.vault_password.d/$USER.gpg"

