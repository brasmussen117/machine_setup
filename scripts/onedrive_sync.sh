#!/bin/bash

set -e

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

# Sync personal files
echo -e "${LTBLUE}Syncing personal files...${NC}"
onedrive --synchronize --confdir="~/.config/onedrive"

# Sync IT Requests files
echo -e "${LTBLUE}Syncing IT Request files...${NC}"
onedrive --confdir="~/.config/onedrive__IT_Requests" --synchronize

echo -e "${LTGREEN}Done!${NC}"
