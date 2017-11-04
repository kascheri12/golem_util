# Deployment Notes

1. Spin up Linux Ubuntu 16.04 Enviornment
  * 2vCPU's
  * 7.5GB RAM

2. If Oracle VM, desire to install Guest Additions
  * Start the virtual machine
  * Click Devices menu
  * Select Insert Guest Additions CD image
  * Change to the directory where your CD-ROM drive is mounted (typically /media/<user>/VBOXADDITIONS_x.x.x/)
  * Install it sudo sh ./VBoxLinuxAdditions.run

3. Follow installation instructions for Docker here:
  * https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-16-04

```sh

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install -y docker-ce

```


4. Install Golem
  * https://github.com/golemfactory/golem/wiki/Installation-on-Ubuntu

```sh

wget https://raw.githubusercontent.com/golemfactory/golem/develop/Installer/Installer_Linux/install.sh
chmod +x install.sh
sudo ./install.sh -dev

```

5. Reboot System

```sh

sudo shutdown -r now

```

6. Rollback Geth version to 1.6.7
  * Geth download page: https://geth.ethereum.org/downloads/
  * At time of writing this, it was required for Golem 0.8.0 to run.

```sh

wget https://gethstore.blob.core.windows.net/builds/geth-alltools-linux-amd64-1.6.7-ab5646c5.tar.gz
tar xvzf geth-alltools-linux-amd64-1.6.7-ab5646c5.tar.gz
sudo cp geth-alltools-linux-amd64-1.6.7-ab5646c5/geth /usr/bin

```


7. Run Golem
  * setsid sudo golemapp --nogui
  * tmux
    * sudo golemapp --nogui
    * Ctrl + b , d

* Notes:
  * Nvidia driver installation: https://askubuntu.com/questions/760934/graphics-issues-after-while-installing-ubuntu-16-04-16-10-with-nvidia-graphics

* Uninstall

```sh

sudo killall golemapp
rm install.sh
wget https://raw.githubusercontent.com/golemfactory/golem/develop/Installer/Installer_Linux/install.sh
chmod +x install.sh
sudo ./install.sh -dev

```

8. Testing Golem

  * Download golem-header blend file
    * http://golem.timjones.id.au/golem-header.zip
  * Unzip Contents
    
```sh
    
sudo apt-get install unzip
unzip golem-header.zip -d golem-header
cd golem-header
    
```
    
  * Prepare task.task file

```json

{
  "name": "Golem Task",
  "type": "Blender",
  "subtasks": 10,
  "options": {
      "frame_count": 1,
      "output_path": "",
      "format": "PNG",
      "resolution": [
          3000,
          2000
      ],
      "frames": "1",
      "compositing": false
  },
  "timeout": "10:00:00",
  "subtask_timeout": "0:20:00",
  "bid": 10.0,
  "resources": [
      "/Users/<username>/Downloads/golem-header/golem-header.blend"
  ]
}  

```
    
    



## Deployment on fresh Ubuntu 16.04 10/30/2017

```sh

#### Download Golem RC, Decompress, & Install ####
wget https://github.com/golemfactory/golem/releases/download/0.9.0/golem-linux_x64-0.9.0.tar.gz
tar xvzf golem-linux_x64-0.9.0.tar.gz
sudo cp -r golem-0.9.0/* /usr/local/bin
#### Download and install Docker ####
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install -y docker-ce
sudo usermod -aG docker ${USER}
#### Download and install HyperDrive ####
wget https://github.com/mfranciszkiewicz/golem-hyperdrive/releases/download/v0.2.3/hyperg_0.2.3_linux-x64.tar.gz
tar xvzf hyperg_0.2.3_linux-x64.tar.gz
sudo cp -r hyperg/* /usr/local/bin
#### Check python ####
which python3
sudo ln -s /usr/bin/python3 /usr/local/bin/python
#### Restart ####
sudo shutdown -r now
#### Execute Golemapp ####
tmux
golemapp
#### ctrl+b,d #### tmux ls #### tmux a -t 0 ####

```

## Testing

```sh

sudo apt-get install unzip
wget http://golem.timjones.id.au/golem-header.zip
unzip golem-header.zip
mkdir -p ~/Git
cd ~/Git
git clone https://github.com/kascheri12/golem_util.git
sudo apt-get install -y python3-pip
pip3 install --upgrade pip
sudo pip3 install twisted



```
