#!/bin/sh

# 1. Allow the VM to talk to the host (DHCP & DNS)
sudo nft add rule inet filter input iifname "molecule-*" accept

# 2. Allow the host to talk back to the VM
sudo nft add rule inet filter output oifname "molecule-*" accept

# 3. Allow the VM to route traffic out to your Mullvad VPN interface
sudo nft add rule inet filter forward iifname "molecule-*" oifname "wg-mullvad-ca" accept

# 4. Allow established traffic back into the VM
sudo nft add rule inet filter forward iifname "wg-mullvad-ca" oifname "molecule-*" ct state established,related accept

