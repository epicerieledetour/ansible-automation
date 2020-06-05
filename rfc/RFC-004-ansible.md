# RFC-004 Service Ansible

## Résumé

Cette RFC décrit les critères nécessaires pour l'utilisation et la navigations des documents nécessaires d'[Ansible](
https://www.ansible.com/)

## Description du service

- Instance du Détour pour le service?
- Dépot de code: https://github.com/epicerieledetour/ansible-automation
- Vulnérabilités: https://www.cvedetails.com/product/48886/Redhat-Ansible.html?vendor_id=25
- Pour tester que le service marche:

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

- Les instructions d'installation et de mise à jour sont documenté a travers les playbook Ansible sur le [Dépot de
  code](https://github.com/epicerieledetour/ansible-automation/blob/master/playbook.yml)
