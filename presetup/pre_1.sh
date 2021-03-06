# Using this AMI: ami-08f40561 (Instance)
# ubuntu-maverick-10.10-amd64-server-20101225
### Script provided by DataStax.


sudo apt-get update && sudo apt-get -y dist-upgrade

# RESTART

gpg --keyserver pgp.mit.edu --recv-keys 2B5C1B00
gpg --export --armor 2B5C1B00 | sudo apt-key add -
gpg --keyserver keyserver.ubuntu.com --recv-keys F758CE318D77295D
gpg --export --armor F758CE318D77295D | sudo apt-key add -
wget -O - http://opscenter.datastax.com/debian/repo_key | sudo apt-key add -
wget -O - http://debian.datastax.com/debian/repo_key | sudo apt-key add -

sudo echo "sun-java6-bin shared/accepted-sun-dlj-v1-1 boolean true" | sudo debconf-set-selections
sudo apt-get -y --force-yes update
sudo apt-get -y --force-yes install git

# Git these files on to the server's home directory
git config --global color.ui auto
git config --global color.diff auto
git config --global color.status auto
git clone git://github.com/riptano/ComboAMI.git datastax_ami
cd datastax_ami
git checkout $(head -n 1 presetup/VERSION)

history -c
sudo python presetup/pre_2.py && sudo chown -R ubuntu:ubuntu . && rm -rf ~/.bash_history && history -c


# git pull && rm -rf ~/.bash_history && history -c
