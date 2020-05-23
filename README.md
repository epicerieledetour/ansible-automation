# ansible-automation
Automation of IT related tasks

## Production mode

```sh
ansible-playbook playbook.yml
```

## Developement mode

A [Vagrant](https://vagrantup.com) virtual machine can be used during development to safely test new configurations without modifying the production servers.

```sh
# Creates and run the virtual machine
vagrant up

# Export the ssh configuration to the development virtual machine
vagrant ssh-config --host vagrant > .ssh.config

# Test the ssh connection
ssh -F .ssh.config vagrant lsb_release -a

# Run the Ansible playbook on the Vagrant virtual machine
ansible-playbook --inventory hosts-dev --ssh-extra-args='-F .ssh.config' playbook.yml
```
