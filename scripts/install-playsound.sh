#! /bin/bash

# Install Playsound - https://github.com/TaylorSMarks/playsound/releases/tag/v1.3.0
#   (which for some reason requires these special steps)

set -e

# Colors
CYAN='\e[0;36m'
LIGHT_GREEN='\e[1;32m'
PURPLE='\e[0;35m'
YELLOW='\e[1;33m'
NC='\e[0m'

echo -e "  ${CYAN}Running '${PURPLE}poetry run pip install --upgrade pip${CYAN}'${NC} ..."
poetry run pip install --upgrade pip
echo -e "  ${YELLOW}DONE${NC}\n"
echo -e "  ${CYAN}Running '${PURPLE}poetry run pip install --upgrade wheel${CYAN}'${NC} ..."
poetry run pip install --upgrade wheel
echo -e "  ${YELLOW}DONE${NC}\n"
echo -e "  ${CYAN}Running '${PURPLE}poetry run pip install playsound${CYAN}'${NC} ..."
poetry run pip install playsound
echo -e "  ${LIGHT_GREEN}Playsound Installed!${NC}\n"
