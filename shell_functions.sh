#!/bin/bash

# Constants for colors
BLACK='\033[0;30m'
RED='\033[0;31m'
GREEN='\033[0;32m'
ORANGE='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
LTGRAY='\033[0;37m'
GRAY='\033[1;30m'
LTRED='\033[1;31m'
LTGREEN='\033[1;32m'
YELLOW='\033[1;33m'
LTBLUE='\033[1;34m'
LTPURPLE='\033[1;35m'
LTCYAN='\033[1;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# shortcut to use sha256 checksum
# $1: hash
# $2: file to check
checksha256 () {
	echo "$1 $2" | sha256sum --check
}

# shortcut to use md5 checksum
# $1: hash
# $2: file to check
checkmd5 () {
	echo "$1 $2" | md5sum --check
}

# shortcut to grep from alias
# $1: search string
agl () {
    alias | grep $1 $2 --color=auto --exclude-dir={.bzr,CVS,.git,.hg,.svn,.idea,.tox} | less
}

# shortcut to do a git fixup with fzf (fuzzy finder) as a TUI
# $1: number of commits to look back
gfu () {
    ! git log -n "$1" --pretty=format:'%h %s' --no-merges | fzf | cut -c -7 | xargs -o git commit --fixup
}

# shoutcut to install a deb file downloaded to the Downloads directory
# $1: name of the deb file to install
install_deb_from_downloads() {
    local deb_src="$1"

    if [[ -z "$deb_src" ]]; then
        echo "${LTBLUE}Usage: install_deb_from_downloads <path-to-deb-file>${NC}"
        return 1
    fi

    if [[ ! -f "$deb_src" ]]; then
        echo "${RED}Error: File '$deb_src' does not exist.${NC}"
        return 1
    fi

    local deb_name
    deb_name="$(basename "$deb_src")"

    local target_dir="/var/cache/apt/archives/partial"
    local deb_dest="$target_dir/$deb_name"

    echo "${LTGRAY}Moving $deb_src to $deb_dest...${NC}"
    sudo mv "$deb_src" "$deb_dest"

    echo "${LTGRAY}Installing $deb_name...${NC}"
    sudo apt install "$deb_dest"

    echo "${LTGREEN}Installation of $deb_name completed.${NC}"
}

# clean pycache files and folders inside current dir
# from SO - https://stackoverflow.com/a/41386937/2918074
#pycrm () {
#  find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete
#}

# region cd modification script by Brandon
###
 # Modified "cd" command to automatically load/unload local Python ".venv" environments.
 # :$1: The standard path to pass into the "cd" command.
 ##
#function cd() {
#  local cd_string=$@
#  local cd_path=""
#  local checked_current=false
#
#
#  # Check all sections of provided path.
#  for index in $(echo ${cd_string} | tr "/" "\n")
#  do
#
#    # Check if we've looked at any paths yet.
#    if [[ "${cd_path}" ]]
#    then
#      # Not first part of path. Simply concat index and prev path info.
#      cd_path="${cd_path}/${index}"
#    else
#      # First part of path. Check current folder, before anything else.
#      cd_path="${index}"
#
#      # Deactivate if backing out and .venv folder exists in current folder.
#      if [[ "${index}" == ".." ]]
#      then
#        if [[ -d .venv ]]
#        then
#          cd_venv_deactivate
#        fi
#      fi
#    fi
#
#
#    # Check if current path equals home folder. If so, assume fresh start and deactivate.
#    if [[ "/${cd_path}" == "${HOME}" ]]
#    then
#      cd_venv_deactivate
#    fi
#
#
#    # If backing up, check for .venv in parent folder.
#    if [[ "${index}" == ".." ]]
#    then
#      # Check for venv folder.
#      if [[ -d "${cd_path}/.venv" ]]
#      then
#        cd_venv_deactivate
#      fi
#    else
#      # Otherwise, check if we're going into an environment folder.
#      if [[ -d "${cd_path}/.venv" ]]
#      then
#        cd_venv_activate "./${cd_path}/.venv"
#      fi
#    fi
#
#  done
#
#
#  # Execute normal cd command.
#  builtin cd "${cd_string}"
#
#
#  # Check for .venv folder in new directory.
#  if [[ -d ./.venv ]]
#  then
#    cd_venv_activate "./.venv"
#  fi
#}


###
 # Attempts to activate Python virtual environment.
 # :$1: Path of folder for virtual environment (excluding the "/bin/activate" part).
 ##
#cd_venv_activate() {
#
#  # First make sure no other environment is loaded.
#  cd_venv_deactivate
#
#  # Ensure that folder is a Python environment.
#  if [[ -f "${1}/bin/activate" ]]
#  then
#    # Load environment.
#    . "${1}/bin/activate"
#  fi
#}


###
 # Deactivates current Python virtual environment, if present.
 ##
#cd_venv_deactivate() {
#  # Check if environment is currently active.
#  if [[ -n "${VIRTUAL_ENV}" ]]
#  then
#    deactivate
#  fi
#}

# endregion cd modification script by Brandon
