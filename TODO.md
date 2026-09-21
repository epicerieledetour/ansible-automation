# TODO

## dev

- molecule/vps2: site:wordpress test manual restore from prod

- molecule/srv1: initialize config
- molecule/srv1: move grafana/loki/alloy/prometheus/node_exporter roles from vps2 to srv1, with caddy reverse proxy
- molecule/srv1: becomes backup store for websites
- molecule/srv1: for prod mount /dev/sdb1 -> /srv/borgmatic

- molecule/pi1: comment pi1 temporarily

## migration

- prod/charles-lp: generate and install NetworkManager vpn config
- prod/charles-ws: generate and install networkd vpn config

- prod/srv1: run playbook

- prod/vps2: reinstall trixie
- prod/vps2: run playbook
- prod/vps2: restore vouchers
- prod/vps2: restore wordpress
- prod: update DNS
- prod/vps: destroy vps

