# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
  config.vm.define "vps", primary: true do |vps|
    vps.vm.hostname = "vps"
    # The most common configuration options are documented and commented below.
    # For a complete reference, please see the online documentation at
    # https://docs.vagrantup.com.

    # Every Vagrant development environment requires a box. You can search for
    # boxes at https://vagrantcloud.com/search.
    vps.vm.box = "debian/buster64"

    # Disable automatic box update checking. If you disable this, then
    # boxes will only be checked for updates when the user runs
    # `vagrant box outdated`. This is not recommended.
    # config.vm.box_check_update = false

    # Create a forwarded port mapping which allows access to a specific port
    # within the machine from a port on the host machine. In the example below,
    # accessing "localhost:8080" will access port 80 on the guest machine.
    # NOTE: This will enable public access to the opened port
    # vps.vm.network "forwarded_port", guest: 80, host: 8000
    # vps.vm.network "forwarded_port", guest: 443, host: 4430

    # Create a forwarded port mapping which allows access to a specific port
    # within the machine from a port on the host machine and only allow access
    # via 127.0.0.1 to disable public access
    # config.vm.network "forwarded_port", guest: 80, host: 8080, host_ip: "127.0.0.1"

    # Create a private network, which allows host-only access to the machine
    # using a specific IP.
    # config.vm.network "private_network", ip: "192.168.33.10"

    vps.vm.network "private_network", ip: "192.168.56.10"

    # Create a public network, which generally matched to bridged network.
    # Bridged networks make the machine appear as another physical device on
    # your network.
    # config.vm.network "public_network"

    # Share an additional folder to the guest VM. The first argument is
    # the path on the host to the actual folder. The second argument is
    # the path on the guest to mount the folder. And the optional third
    # argument is a set of non-required options.
    # config.vm.synced_folder "../data", "/vagrant_data"
    vps.vm.synced_folder ".", "/vagrant", disabled: true

    # Provider-specific configuration so you can fine-tune various
    # backing providers for Vagrant. These expose provider-specific options.
    # Example for VirtualBox:
    #
    # config.vm.provider "virtualbox" do |vb|
    #   # Display the VirtualBox GUI when booting the machine
    #   vb.gui = true
    #
    #   # Customize the amount of memory on the VM:
    #   vb.memory = "1024"
    # end
    #
    # View the documentation for the provider you are using for more
    # information on available options.

    # Enable provisioning with a shell script. Additional provisioners such as
    # Puppet, Chef, Ansible, Salt, and Docker are also available. Please see the
    # documentation for more information about their specific syntax and use.
    # config.vm.provision "shell", inline: <<-SHELL
    #   apt-get update
    #   apt-get install -y apache2
    # SHELL
    # vps.vm.provision "ansible" do |ansible|
      # ansible.playbook = "playbook.yml"
    # end
  end

  config.vm.define "vps2", primary: true do |vps2|
    vps2.vm.hostname = "vps2"
    vps2.vm.box = "debian/bookworm64"
    vps2.vm.network "private_network", ip: "192.168.56.11"
    vps2.vm.network "forwarded_port", guest: 80, host: 8000
    vps2.vm.network "forwarded_port", guest: 443, host: 4430
    vps2.vm.synced_folder ".", "/vagrant", disabled: true
  end

  config.vm.define "pi1" do |pi1|
    pi1.vm.hostname = "pi1"
    pi1.vm.box = "debian/bookworm64"
    pi1.vm.network "private_network", ip: "192.168.56.12"
    pi1.vm.synced_folder ".", "/vagrant", disabled: true
  end

  config.vm.define "srv1" do |srv1|
    srv1.vm.hostname = "srv1"
    srv1.vm.box = "debian/bookworm64"
    srv1.vm.network "private_network", ip: "192.168.56.13"
    srv1.vm.synced_folder ".", "/vagrant", disabled: true
  end

  config.vm.define "kiosk1" do |kiosk1|
    kiosk1.vm.hostname = "kiosk1"
    kiosk1.vm.box = "debian/bookworm64"
    kiosk1.vm.network "private_network", ip: "192.168.56.14"
    kiosk1.vm.synced_folder ".", "/vagrant", disabled: true

    # Provision is defined in last machine so Ansible runs once
    # all machines are defined
    # https://www.vagrantup.com/docs/provisioning/ansible.html#ansible-parallel-execution
    kiosk1.vm.provision "ansible" do |ansible|
      ansible.limit = "all"
      ansible.playbook = "playbook.yml"
      ansible.groups = {
        "workstations": [
          "charles-xps15",
          "charles-ws",
          "mauriandres-workstation"],
        "servers": [
          "vps",
          "vps2",
          "pi1",
          "srv1",
          "kiosk1"
        ],
        "vouchers": [
          "vps2"
        ],
        "webservers": [
          "vps"
        ],
        "borgstores": [
          "pi1"
        ],
        "dataproxies": [
          "pi1"
        ],
        "backuphead": [
          "vps",
          "vps2",
          "pi1"
        ],
        "kiosks": [
          "kiosk1"
        ],
      }
      ansible.host_vars = {
        "vps2" => {
          "wireguard_endpoint_address" => "192.168.56.11",
        }
      }
      ansible.extra_vars = {
        "deployment_is_vagrant": true
      }
    end
  end
end
