#! /bin/bash

#
# Test EQ Alert Parsing
#
#
#    * Ensure EQ Alert is running against the default character before testing
#


# Variables

## Things worth changing
EQ_LOGS=$(jq '.settings.paths.char_log' config.json)
DEFAULT_CHAR=$(jq '.characters.default' config.json | tr -d '"')
CHAR_LOG="${EQ_LOGS//\"}eqlog_${DEFAULT_CHAR^}_project1999.txt"

## Colors
BLACK='\e[0;30m'
BLUE='\e[0;34m'
GREEN='\e[0;32m'
CYAN='\e[0;36m'
RED='\e[0;31m'
PURPLE='\e[0;35m'
BROWN='\e[0;33m'
LIGHT_GRAY='\e[0;37m'
DARK_GRAY='\e[1;30m'
LIGHT_BLUE='\e[1;34m'
LIGHT_GREEN='\e[1;32m'
LIGHT_CYAN='\e[1;36m'
LIGHT_RED='\e[1;31m'
LIGHT_PURPLE='\e[1;35m'
YELLOW='\e[1;33m'
WHITE='\e[1;37m'
NC='\e[0m'
BOLD='\e[1m'

## Runtime
skip=0
run=0


# Ctrl+C Safety
function stop_tests() {
  echo -e "\n${CYAN}Stopping tests${NC} ..."
  exit 0
}
trap stop_tests SIGINT


# Ensure EQ Alert is running
ACTIVE=$(pgrep -f eqalert.py)
if [ -z $ACTIVE ]; then
  echo -e "\n${CYAN}Usage:${NC}"
  echo -e "\n${WHITE}$ ${RED}Ensure EQ Alert is running${NC}"
  echo -e "${WHITE}$ ${YELLOW}./parse_test.sh${NC}"
  exit 0
fi


# Begin the Trials

## you_tell
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}you_tell${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## you_say
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}you_say${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## you_shout
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}you_shout${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## you_group
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}you_group${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## you_ooc
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}you_ooc${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## you_guild
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}you_guild${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## you_auction
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}you_auction${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## you_auction_wts:wtb
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}you_auction_wts:wtb${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## you_auction_wts
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}you_auction_wts${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## you_auction_wtb
iecho -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}you_auction_wtb${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## you_new_zone
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}you_new_zone${NC}"
msg="[Sat Dec 29 21:56:56 2018] You have entered The Wakening Lands."
echo -e "  ${LIGHT_GRAY}»${NC} ${LIGHT_GRAY}msg${NC}"
echo $msg >> "$CHAR_LOG"
sleep 0.02
msg="[Sat Dec 29 21:58:18 2018] You have entered Kael Drakkel."
echo -e "  ${LIGHT_GRAY}»${NC} ${LIGHT_GRAY}msg${NC}"
echo $msg >> "$CHAR_LOG"
sleep 0.02
msg="[Sun Dec 30 10:28:06 2018] You have entered Butcherblock Mountains."
echo -e "  ${LIGHT_GRAY}»${NC} ${LIGHT_GRAY}msg${NC}"
echo $msg >> "$CHAR_LOG"
echo -e "  ${LIGHT_GRAY}»${NC} ${LIGHT_GRAY}run${NC} ${LIGHT_GREEN}✔${NC}"
((run++))

## you_healed
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}you_healed${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## you_hungry
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}you_hungry${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## you_afk_on
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}you_afk_on${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## you_lfg_on
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}you_lfg_on${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## you_afk_off
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}you_afk_off${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## you_lfg_off
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}you_lfg_off${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## you_outfood
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}you_outfood${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## you_outdrink
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}you_outdrink${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## you_outfooddrink
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}you_outfooddrink${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## you_outfoodlowdrink
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}you_outfoodlowdrink${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## you_outdrinklowfood
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}you_outdrinklowfood${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## you_thirsty
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}you_thirsty${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## you_hungry
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}you_hungry${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## you_spell_forget
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}you_spell_forgot${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## spell_break_charm
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}spell_break_charm${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## spell_break_ensare
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}spell_break_ensare${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## spell_break
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}spell_break${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## faction_line
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}faction_line${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## target_cured
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}target_cured${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## who_line
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}who_line${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## mysterious_oner
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}mysterious_oner${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## tell
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}tell${NC}"
msg="[Sat Dec 29 21:41:44 2018] Parser tells you, 'tell'"
echo -e "  ${LIGHT_GRAY}»${NC} ${LIGHT_GRAY}msg${NC}"
echo $msg >> "$CHAR_LOG"
sleep 0.01
echo -e "  ${LIGHT_GRAY}»${NC} ${LIGHT_GRAY}run${NC} ${LIGHT_GREEN}✔${NC}"
((run++))

## guild
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}guild${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## group
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}group${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## say
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}say${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## shout
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}shout${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## ooc
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}ooc${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## auction
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}auction${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## auction_wts
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}auction_wts${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## auction_wtb
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}auction_wtb${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## spell_something
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}spell_something${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## spell_fizzle
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}spell_fizzle${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## spell_interrupted
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}spell_interrupted${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## dot_damage
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}dot_damage${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## spell_damage
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}spell_damage${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## engage
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}engage${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## zoning
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}zoning${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## random
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}random${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## loc
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}loc${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## group_invite
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}group_invite${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## who_total
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}who_total${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## who_player
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}who_player${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## who_player_afk
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}who_player_afk${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## who_player_linkdead
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}who_player_linkdead${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## who_top
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}who_top${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## target
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}target${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## emote_bow
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}emote_bow${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## emote_thank
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}emote_thank${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## emote_wave
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}emote_wave${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## emote_dance
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}emote_dance${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## emote_bonk
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}emote_bonk${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## emote_smile
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}emote_smile${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## emote_cheer
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}emote_cheer${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## weather_start_rain
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}weather_start_rain${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## weather_start_snow
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}weather_start_snow${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## weather_stop_rain
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}weather_stop_rain${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## weather_stop_snow
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}weather_stop_snow${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))

## you_camping
echo -e "${PURPLE}Type${NC} ${BLUE}:${NC} ${LIGHT_PURPLE}you_camping${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
((skip++))


# Tests completed
echo -e " --- COMPLETED ---"
echo -e "  ${LIGHT_GRAY}»${NC} ${CYAN}Skipped${NC} ${BLUE}:${NC} ${LIGHT_GRAY}$skip${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${CYAN}Run${NC} ${BLUE}:${NC} ${LIGHT_GRAY}$run${NC}"
