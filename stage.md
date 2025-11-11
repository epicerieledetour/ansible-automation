- Vision
  - Document network services with Ansible
    - Corrolary: no final setup should be done by clicking on user interface, everything config should be in the ansible scripts
  - Few of use that can run the Ansible scripts
  - Follow the chaton.org vision
  - backup / restore scripts
  - Minimize dependencies to third-party services
  - All auth comes from an @epicerieledetour.org account
  - Encryption required
  - Internal doc is in French (the Détour is a French speaking organization), but external doc (notably, everything on the GitHub) is in English because it is public
  - Monthly report of IT usage
  - All network ports closed by default
    - We open them only when required by a service, from ansible

- describe network topology and what services are hosted on each machine
  - We don't punch holes in domestic routers: all machines connect within a wireguard star network, with an unique, public machine as the main router

- Current problems
  - Developer setup is broken
    - Remove dependencies, move to systemd-nspawn ?
    - Move ansible-vault key management from gpg to ssh pub keys
  - We run old versions of everything
    - OS (Debian Buster)
    - Versions (Wordpress, Grafana)
    - We might have desynch'ed from Google Auth for some services
      - Needs to ensure account creation / logging through gmail.com (anyone with @epicerieledetour should edit the website by default)
  - No more updates on vps
    - This breaks the ansible setup
    - Needs to make the backup / restore commands
    - Migrate all services to vps2
      - Influx / Grafana et al. -> B7 srv / No need to keep existing data
      - Nginx -> vps2, no need to keep existing logs
      - nginx-membres -> vps2, no data to migrate
      - nginx-vouchers -> vps2, no data to migrate
      - wordpress -> vps2, needs ansible backup / restore tags, needs to migrate data
  - Needs to migrate some services out of my own raspberry pi
    - But we need to make sure that we can still simply deploy backup pods to Le Detour members
    - Migrate dataproxies -> b7 srv
      - dataproxies needs to be on an encrypted partition
      - OK to decrypt the partition by hand with ansible + tag after a reboot
      - service should fail and we should be notified if the partition is not de-encrypted
    - Migrate borgstores -> b7 srv, keep existing data
  - Hard to restore gdrive backups
    - How do we want to expose backuped files ?
    - How can we know the files that are not backuped ?
  - We don't know exactly what is going on our servers
    - Better observability / alerting
    - Monitor and alert on resources
      - Logs on Slack when a backup finishes for example, with a report
      - Alert when server resources reach a threshold (server fs not full)
      - Needs to know certificates validity, both servers and clients
    - Log web server
    - Log access
  - reinstall web kiosk in the épicerie
  - Two sets of ansible scripts, one for batiment7
    - We need to merge both to simplify admin and share resources
    - Host mattermost and backup mattermost media on b7 server
  - Video meetings are expensive with Zoom
    - We should try our setup our own instance of jitsi
  - Fill RFCs for each service
  - Backup all @epicerieledetour.org email accounts
  - Add simple web dashboard in Grafana service
  - Backup / restore B7 Router configuration

- Lister les contraintes du stage
  - Tous volontaires: horaires qui peuvent sortir des heures de bureau standard
  - Setup must work on Debian Trixie
- État final souhaité
- Stretch goals: observability, alerting
- lister compétence requises
- compétences qui vont être acquéries
- backup
  - one command backup
  - one command restore
- RFC:
  - How to test it works ?
  - Monthly usage report
- what needs to be manually migrated from old vps ?

# Communication

- Via le Slack du Détour
- MR de scrum tous les matins

# Plan de travail

- Prototype, small Vagrant network

# Skills

- required
  - Gout pour la bidouille Linux, savoir installer linux from scratch, à l'aise avec la ligne de command

