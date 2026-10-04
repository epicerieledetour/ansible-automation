# TODO

## migration

Move everything from `vps` (Debian 10: nginx + certbot, wordpress, membres, old
grafana/influxdb) and `vps2` (Debian 12: vouchers) to a reinstalled `vps2`
(Debian 13), configured by this playbook.

### What gets migrated

| data | from | how |
|---|---|---|
| vouchers database `ldt-vouchers.sqlite3` | vps2 `/srv/www/vouchers.epicerieledetour.org` | `sqlite3 -readonly .dump`, restored by `tmp_migration/restore.sh` |
| vouchers `files/` (emission report.ods) | same folder | tar, restored by `restore.sh` |
| wordpress database `wordpress` | vps MariaDB 10.3 | `mysqldump wordpress`, restored by `restore.sh` |
| wordpress `wp-content` (uploads, themes `ledetour` and `twentytwentyone-child`, plugins, languages) | vps `/srv/www/wordpress-5.7/wordpress/wp-content` | tar, restored by `restore.sh` |

Not migrated, on purpose:

- membres: the JSON files are regenerated every hour from the Google script,
  and the client CA in `roles/membres/files/client-ca.crt` is the same one vps
  uses (same sha256 fingerprint)
- old grafana, influxdb, loki, promtail, telegraf on vps: dropped, replaced by
  the srv1 stack
- TLS certificates: certbot's certificates are not reused, caddy gets new ones
- old `backup@pi1` borg backups of vps and vps2: stay on pi1
- vps2 ssh host key: already in the vault (`host_vars/vps2`), the playbook
  reinstalls it
- vouchers code: prod runs branch `v2` at `c565791`; the playbook runs `main`,
  which is `c565791` plus 2 commits that only add the `ldtvouchers` script entry
  and a template file. Same database schema, and `db init` is idempotent

Notes from the molecule dry run:

- The vouchers database `.dump` rebuilds with identical row counts
  (8930 vouchers, 61490 actions on 2026-10-03) and passes `integrity_check`
- WordPress home/siteurl are `https://wordpress.epicerieledetour.org` in the
  database. `restore.sh` rewrites them to `https://epicerieledetour.org`
  (~350 replacements; `guid` columns are deliberately left unchanged)
- WordPress core is downloaded fresh (newer than prod): `restore.sh` runs
  `wp core update-db`
- The wordpress role's "Enable plugins auto-updates" task fails when only some
  of its plugins already have auto-updates on, which is the case after the
  restore. `restore.sh` turns all auto-updates off first as a workaround. To fix
  in the role later.
- `/` answers 302 to `/fr/` (Polylang), same as prod today. `molecule verify`
  expects 200 on `/` so it will fail on wordpress with migrated content: it's
  expected
- Both Google login plugins end up active: the old
  `miniorange-login-with-eve-online-google-facebook` (from the prod database)
  and `login-with-google` (from the playbook). miniorange is removed once
  Google login is confirmed working, see the checklist. Tested on molecule:
  the login page then only shows `login-with-google`, and the playbook stays
  clean.
- In development, the vouchers report no longer emails: the unit has no SMTP
  settings and no `emailreport` step, and its timer is disabled and stopped.
  Production is unchanged.
- The molecule vps2 VM holds production data: destroy it
  (`uv run molecule destroy`) when done.

### Decisions

- `vouchers2.epicerieledetour.org` is dropped: not in the caddy config, its
  DNS record gets deleted
- `epicerieledetour.org` serves wordpress; `wordpress.epicerieledetour.org`
  and `www.epicerieledetour.org` redirect to it permanently, keeping the path
  (`roles/wordpress/templates/wordpress.caddy.j2`)
- miniorange gets removed, `login-with-google` is the only Google login

### TLS with caddy

Caddy gets Let's Encrypt certificates by itself (HTTP-01/TLS-ALPN on ports 80
and 443, opened by `roles/caddy`, account email `contact@epicerieledetour.org`)
for every public name in `/etc/caddy/sites.d/*.caddy`: `epicerieledetour.org`,
`www.`, `wordpress.`, `vouchers.`, `membres.`, `grafana.`. `*.localhost` names get
caddy's internal CA. For this to work:

- Every name must resolve to vps2, **for A and AAAA**. Let's Encrypt prefers
  IPv6: today `epicerieledetour.org`, `www.`, `wordpress.`, `membres.` and
  `grafana.` have an AAAA record `2607:5300:205:200::245d`, which nothing
  answers (vps has no IPv6 configured). They must point at vps2's IPv6
  (`2607:5300:205:200::4553` before the reinstall, check it after) or be
  deleted
- No CAA record exists on the domain, so nothing restricts the CA
- Let's Encrypt allows 5 failed validations per hostname per account per hour:
  switch the DNS **before** the playbook installs caddy. If caddy started too
  early, it retries on its own with backoff; `sudo systemctl restart caddy`
  retries immediately

### Checklist

DNS is at GoDaddy (`ns11/ns12.domaincontrol.com`). vps2's public addresses:
IPv4 `148.113.197.26`, IPv6 `2607:5300:205:200::4553` (to confirm after the
reinstall).

Before (can be done now):

- [ ] Lower the TTL of `epicerieledetour.org` from 3600 to 300 (the subdomains
      are already at 600 or less)
- [ ] Tell wordpress editors not to edit tonight
- [ ] Remember `tmp_migration` holds production data **in clear**: never
      commit it (`git status` shows it as untracked, it isn't in `.gitignore`)

Freeze and copy the data, from the workstation, in the repo root:

- [ ] Stop vouchers on old vps2, the last write wins from here on:
      `ssh vps2 sudo systemctl stop ldt-vouchers.service ldt-vouchers-report.timer ldt-vouchers-backup.timer`
- [ ] Copy the data:

      cd tmp_migration
      rm -rf bundle bundle.tar.gz && mkdir -p bundle/vouchers bundle/wordpress
      cp restore.sh bundle/
      ssh vps2 'sqlite3 -readonly /srv/www/vouchers.epicerieledetour.org/ldt-vouchers.sqlite3 .dump' > bundle/vouchers/ldt-vouchers.sql
      ssh vps2 'tar -C /srv/www/vouchers.epicerieledetour.org -czf - files' > bundle/vouchers/files.tar.gz
      ssh vps 'sudo mysqldump --single-transaction --default-character-set=utf8mb4 wordpress | gzip' > bundle/wordpress/wordpress.sql.gz
      ssh vps 'sudo tar -C /srv/www/wordpress-5.7/wordpress -czf - wp-content' > bundle/wordpress/wp-content.tar.gz
      tar -czf bundle.tar.gz bundle

- [ ] Check the copy: `tail -1 bundle/vouchers/ldt-vouchers.sql` is `COMMIT;`,
      `zcat bundle/wordpress/wordpress.sql.gz | tail -1` is `-- Dump completed on ...`,
      and the counts match:

      sqlite3 /tmp/check.sqlite3 < bundle/vouchers/ldt-vouchers.sql && sqlite3 /tmp/check.sqlite3 'select count(*) from vouchers; select count(*) from actions' && rm /tmp/check.sqlite3
      ssh vps2 'sqlite3 -readonly /srv/www/vouchers.epicerieledetour.org/ldt-vouchers.sqlite3 "select count(*) from vouchers; select count(*) from actions"'

DNS, at GoDaddy:

- [ ] A `@` (epicerieledetour.org) → `148.113.197.26`
- [ ] A `wordpress` → `148.113.197.26`
- [ ] A `vouchers` → `148.113.197.26`
- [ ] A `membres` → `148.113.197.26`
- [ ] A `grafana` → `148.113.197.26`
- [ ] Delete the A record `vouchers2` (dropped)
- [ ] AAAA `@`, `wordpress`, `membres`, `grafana` → `2607:5300:205:200::4553`,
      or delete them if vps2 has no IPv6 after the reinstall
- [ ] `www` stays a CNAME to `@`: it follows the apex's A and AAAA, and caddy
      redirects it to the apex
- [ ] Leave `vps.epicerieledetour.org` alone until vps is destroyed

Reinstall vps2:

- [ ] OVH panel: reinstall vps2 with Debian 13, with my ssh key for `debian`
- [ ] Check `debian` has passwordless sudo: `ssh vps2 sudo -n true`. If not,
      follow README "First setup of a production machine"
- [ ] The reinstall generates a new ssh host key, so known_hosts no longer
      matches until the `sshd` role puts the vaulted one back. Run the ssh play
      alone without host key checking (public key auth still works):
      `ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook playbook.yml --limit vps2 --tags ssh`
- [ ] `ssh vps2 true` works again without a host key warning
- [ ] `ssh vps2 ip -br addr`: confirm the IPv6, fix the AAAA records if it changed

Run the playbook:

- [ ] DNS has propagated: `dig +short A epicerieledetour.org @8.8.8.8` and
      `dig +short AAAA epicerieledetour.org @8.8.8.8` (same for the other names)
      return vps2's addresses
- [ ] `ansible-playbook playbook.yml --limit vps2`. vps2 first: srv1 is only
      reachable through vps2's Wireguard endpoint, which doesn't exist yet. This
      wasn't exercised by molecule, where the VMs reach each other directly.
- [ ] Wireguard is back: `ping 192.168.211.60` (srv1) from the workstation
- [ ] `ansible-playbook playbook.yml` (everything, srv1 included)

Restore:

- [ ] `scp tmp_migration/bundle.tar.gz vps2:`
- [ ] `ssh vps2 'tar xzf bundle.tar.gz && sudo ./bundle/restore.sh https://epicerieledetour.org'`
- [ ] `ansible-playbook playbook.yml --limit vps2 --tags wordpress`
- [ ] Take a first backup: `ssh vps2 'sudo borgmatic --config /etc/borgmatic.d/vouchers.yaml --config /etc/borgmatic.d/wordpress.yaml --config /etc/borgmatic.d/system.yaml create --stats'`
- [ ] `ssh vps2 rm -rf bundle bundle.tar.gz`

Verify:

- [ ] Certificates were issued: `ssh vps2 journalctl -u caddy | grep -i "certificate obtained"`, 6 names
- [ ] For each name, a Let's Encrypt certificate is served over IPv4 and IPv6:

      for n in epicerieledetour.org www.epicerieledetour.org wordpress.epicerieledetour.org vouchers.epicerieledetour.org membres.epicerieledetour.org grafana.epicerieledetour.org; do
        for ip in 4 6; do printf "%s v%s " $n $ip; curl -$ip -s -o /dev/null -w "%{http_code} %{ssl_verify_result}\n" https://$n/; done
      done
      echo | openssl s_client -connect epicerieledetour.org:443 -servername epicerieledetour.org 2>/dev/null | openssl x509 -noout -issuer -dates

- [ ] `http://` redirects to `https://`: `curl -sI http://epicerieledetour.org | grep -i location`
- [ ] Wordpress: https://epicerieledetour.org redirects to `/fr/`, the home page
      looks like before (title "Épicerie Le Détour – BienvenuEs dans votre épicerie !"),
      images load, English version works
- [ ] Wordpress: `www.` and `wordpress.` redirect to the apex, path included:

      for n in www.epicerieledetour.org wordpress.epicerieledetour.org; do curl -s -o /dev/null -w "$n %{http_code} %{redirect_url}\n" https://$n/fr/; done

      both print `301 https://epicerieledetour.org/fr/`
- [ ] Wordpress: log in with Google at https://epicerieledetour.org/wp-login.php
- [ ] Wordpress: once Google login works, remove miniorange:
      `ssh vps2 'cd /srv/www/wordpress.epicerieledetour.org && sudo -u www-data php8.5 /usr/local/bin/wp plugin deactivate miniorange-login-with-eve-online-google-facebook --uninstall'`,
      then the login page only shows "Login with Google"
- [ ] Vouchers: https://vouchers.epicerieledetour.org works, the data is there
      (check a recent cash-in), scanning a voucher works
- [ ] Vouchers: `ssh vps2 systemctl list-timers ldt-vouchers-report.timer` is
      scheduled for 20:30, and the next day's report email arrives
- [ ] Membres: `curl -s https://membres.epicerieledetour.org/members.json | jq length`,
      and with the client certificate it returns non-anonymized data
- [ ] Grafana: https://grafana.epicerieledetour.org, logs and metrics of the new
      vps2 show up
- [ ] Backups: `ssh vps2 sudo borgmatic --config /etc/borgmatic.d/vouchers.yaml repo-list`
      shows the archive, and `systemctl is-enabled borgmatic.timer` is enabled

After:

- [ ] Drop vouchers2: check the record `vouchers2` is gone from GoDaddy and
      `dig +short vouchers2.epicerieledetour.org` returns nothing. Tell anyone
      still using `vouchers2.` links to use `vouchers.`
- [ ] A few days later: destroy vps (OVH), delete the DNS record `vps`
- [ ] Remove `host_vars/vps` and the `vps` mention in README
- [ ] Fix the wordpress role's "Enable plugins auto-updates" `failed_when` for
      partially enabled plugins
- [ ] Delete `tmp_migration` (production data in clear) and destroy the molecule VMs
- [ ] Raise the `epicerieledetour.org` TTL back to 3600
