# ansible-automation
Automation of IT related tasks

## The vault password file

This playbook uses [Ansible Vaults](https://docs.ansible.com/ansible/latest/user_guide/vault.html). The password file, GPG encryped and shared amongst Le Détour admins by an out-of-band mean of communication, is expected to be named `.vault_password.gpg` in this cloned repo root folder.

## Install required roles

```sh
ansible-galaxy collection install -r requirements.yml
ansible-galaxy role install -r requirements.yml

# TODO: When Ansible 2.10 is released, this should be enough
# ansible-galaxy install -r requirements.yml
```

## Production mode

```sh
ansible-playbook playbook.yml
```

## First setup of a production machine

1. Install debian 10 (buster)
2. Full disk encryption
3. Add a single user `debian`
4. Ensure openssh server is running
5. `ssh-copy-id` for the user / machine ansible will be ran from
6. Configure user `debian` for passwordless sudo. Create a new file `/etc/sudoers.d/admin` with this content: `debian ALL = NOPASSWD: ALL`
7. Run ansible against a first time with the LAN IP of the machine. This will bootstrap the Wireguard connection that will be used by default next time: `ansible-playbook -e "ansible_host=[LAN IP]" playbook.yml --limit [hostname]`, for example `ansible-playbook -e "ansible_host=192.168.1.42" playbook.yml --limit laptopserver`
8. The machine is likely to reboot on first ansible run: be ready to enter disk decryption keys

## Encrypt Sensitive Files

```sh
# Encrypt the secret file
ansible-vault encrypt --vault-id @prompt secret.yml

# View the content of the secret file, will ask for password
ansible-vault view secret.yml

# Decrypt the content of the secret file, will ask for password
ansible-vault decrypt secret.yml
```

## Developement mode

A [Vagrant](https://vagrantup.com) virtual machine can be used during development to safely test new configurations without modifying the production servers.

```sh
# Creates and run the virtual machines
vagrant up

# Run the Ansible playbook on the Vagrant virtual machine
vagrant provision
```

### Get ssh logging info

```sh
sudo grep sshd /var/log/auth.log
```

```sh
w
 12:42:14 up 1 min,  1 user,  load average: 0.06, 0.04, 0.01
USER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT
vagrant  pts/0    10.0.2.2         12:41    1.00s  0.07s  0.00s w
```

### Wordpress backup info

The plugin used for backups of the wordpress documents and databases is
[UpDraftPlus](https://wordpress.org/plugins/updraftplus/). To change the google drive recipient
account of the wordpress backups. You may go to the
[settings](https://epicerieledetour.org/wp-admin/options-general.php?page=updraftplus) page.

Go to the `settings` tab showed below

![](pictures/settings_tab.png)

Scroll down until you reach the `Google Drive` section

![](pictures/gdrive_options.png)
