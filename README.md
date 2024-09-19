# README #

Some personally useful aliases, scripts, and miscellaneous setups for a new machine.

## Setup
### Install Basics
```bash
sudo apt update
sudo apt upgrade -y
sudo apt install zsh git curl tmux software-properties-common
sudo apt autoremove -y
```
### Generate SSH Key
```bash
cd ~/.ssh/; ssh-keygen -t ed25519 -f "github" -N "" -C "brasmussen117"
cat github.pub
```
* Go to [Key Settings](https://github.com/settings/keys) to add the new key.
### Clone Repo
```bash
git clone git@github.com:brasmussen117/machine_setup.git
```
### Setup Links
To make my life easier, I make symlinks from the home dir to this repo. That way, they can be sourced in zshrc without fixing paths.
To create a symbolic link in the home directory that points to this repo, you can use the following command:
**Commands intended to be run from this repos root dir**
```bash
ln -s $(pwd)/aliases ~/.aliases
ln -s $(pwd)/shell_functions.sh ~/.shell_functions.sh
ln -s $(pwd)/zshconfig ~/.zshrc
mkdir ~/.config/nvim
ln -s $(pwd)/init.lua ~/.config/nvim/init.lua
```

## Packages/Apps
### Chrome
https://www.google.com/chrome/
### zsh
* [Install instructions from OMZ](https://github.com/ohmyzsh/ohmyzsh/wiki/Installing-ZSH#install-and-set-up-zsh-as-default)
```bash
chsh -s $(which zsh)
```
* Log out and log back in to check if the default shell was changed
### Oh My Zsh
* [Install instructions from their GitHub](https://github.com/ohmyzsh/ohmyzsh#basic-installation)
```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```
* [Cousine Nerd Font](https://github.com/ryanoasis/nerd-fonts/releases/download/v3.2.1/Cousine.zip)
* [Powerlevel10k theme](https://github.com/romkatv/powerlevel10k?tab=readme-ov-file#oh-my-zsh)
```bash
git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k
```
* Plugins
  * [zsh-zutosuggestions](https://github.com/zsh-users/zsh-autosuggestions/blob/master/INSTALL.md#oh-my-zsh)
    * ```bash
      git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
      ```
  * [zsh-syntax-highlighting](https://github.com/zsh-users/zsh-syntax-highlighting/blob/master/INSTALL.md#oh-my-zsh)
    * ```bash
      git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
      ```
  * [you-should-use](https://github.com/MichaelAquilina/zsh-you-should-use?tab=readme-ov-file#installation)
    * ```bash
      git clone https://github.com/MichaelAquilina/zsh-you-should-use.git $ZSH_CUSTOM/plugins/you-should-use
      ```
### AppImageLauncher
Makes it easy to treat AppImages like any other application on Ubuntu, automatically adding it to the GUI app launcher.
* [Install instructions on their wiki](https://github.com/TheAssassin/AppImageLauncher/wiki/Install-on-Ubuntu-or-Debian#use-the-ppas)
```bash
sudo add-apt-repository ppa:appimagelauncher-team/stable
sudo apt update
sudo apt install appimagelauncher
```
### Neovim
* Remove prior install if it exists
```bash
sudo apt remove neovim
```
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
