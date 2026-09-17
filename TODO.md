# TODO

- prod/vps: manual backup wordpress
- molecule/vps2: site:wordpress backup role
- molecule/vps2: site:wordpress manual restore
- molecule/vps2: site:wordpress restore role
- molecule/vps2: site:wordpress test ansible backup/restore

- prod/vps2: site:vouchers manual vouchers backup
- molecule/vps2: site:vouchers backup role
- molecule/vps2: site:vouchers manual restore
- molecule/vps2: site:vouchers restore role
- molecule/vps2: site:vouchers test ansible backup/restore

- prod/charles-ws: generate and install networkd vpn config
- prod/charles-lp: generate and install NetworkManager vpn config

- molecule/srv1: mount /dev/sdb1 -> /srv/borgmatic
- prod/srv1: run ansible

- molecule/srv1: move grafana/loki/alloy/prometheus/node_exporter roles from vps2 to srv1
- prod/srv1: move grafana/loki/alloy/prometheus/node_exporter roles from vps2 to srv1
- prod/vps2: keep only grafana reverse proxy (roles/grafana/files/grafana.caddy) once srv1 serves grafana

- prod/vps2: reinstall trixie
- prod/vps2: run playbook
- prod/vps2: restore vouchers
- prod/vps2: restore wordpress
- prod: update DNS
- prod/vps: destroy vps
- molecule/vps2: rename vps2->vps
- prod/vps2: rename vps2->vps
- prod/vps2: change si/.ssh/config

- wordpress: auto update cli / site / plugin

