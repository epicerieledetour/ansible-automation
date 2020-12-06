#!/bin/sh

gpg --batch --use-agent --decrypt .vault_password.d/$USER.gpg

