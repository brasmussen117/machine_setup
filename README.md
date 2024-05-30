# README #

Some personally useful aliases, scripts, and miscellaneous setup for a new machine.

## Setup

To make my life easier, I make symlinks from the home dir to this repo—that way they can be sourced in zshrc without having to fix paths.
To create a symbolic link in the home directory that points to this repo, you can use the following command:

```bash
ln -s <path/to-repo> ~/foo_symlink
```

## Packages/Apps
### AppImageLauncher
Makes it easy to treat AppImages like any other application on Ubuntu, automatically adding it to the GUI app launcher.
* [Install instructions on their wiki](https://github.com/TheAssassin/AppImageLauncher/wiki/Install-on-Ubuntu-or-Debian#use-the-ppas)
```bash
sudo apt install software-properties-common
sudo add-apt-repository ppa:appimagelauncher-team/stable
sudo apt update
sudo apt install appimagelauncher
```
### Neovim
* [Install instructions on their wiki](https://github.com/neovim/neovim/blob/master/INSTALL.md#appimage-universal-linux-package)
```bash
cd ~/Downloads
curl -LO https://github.com/neovim/neovim/releases/latest/download/nvim.appimage
chmod u+x nvim.appimage
./nvim.appimage
```
* To expose nvim globally:
```bash
mkdir -p /opt/nvim
mv nvim.appimage /opt/nvim/nvim
```
* And the following line to ~/.bashrc:
```bash
export PATH="$PATH:/opt/nvim/"
```
### VSCode
[Download the latest `.deb`](https://code.visualstudio.com/download) and install it.
