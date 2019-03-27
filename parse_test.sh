#! /bin/bash

#
# Test EQ Alert Parsing
#
#
#    * Ensure EQ Alert is running against the default character before testing
#    * Presently needs to be run from the same directory as `config.json`
#


# Functions

## Default Test: Append Message To Character Log
function run_test() {
  echo -e "\n  ${PURPLE}Type${NC} ${BLUE}:${NC} ${CYAN}$1${NC}"
  echo -e "  ${LIGHT_GRAY}»${NC} ${LIGHT_GRAY}$2${NC}"
  echo $2 >> "$CHAR_LOG"
  sleep 0.018
}

## (Display) Skip Test
function skip_test() {
  echo -e "\n  ${PURPLE}Type${NC} ${BLUE}:${NC} ${CYAN}$1${NC}"
  echo -e "  ${LIGHT_GRAY}»${NC} ${YELLOW}skip${NC}"
}

## Display Usage
function test_usage() {
  echo -e "\n${CYAN}Usage:${NC}"
  echo -e "\n${WHITE}$ ${RED}Ensure EQ Alert is running${NC}"
  echo -e "${WHITE}$ ${YELLOW}./parse_test.sh${NC}"
}


# Checks

## Ensure EQ Alert is running
ACTIVE=$(pgrep -f eqalert.py)
if [ -z $ACTIVE ]; then
  test_usage
  exit 0
fi


# Settings

## Things worth changing
EQ_LOGS=$(jq '.settings.paths.char_log' config.json)
DEFAULT_CHAR=$(jq '.characters.default' config.json | tr -d '"')
CHAR_LOG="${EQ_LOGS//\"}eqlog_${DEFAULT_CHAR^}_project1999.txt"


# Constants

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


# Ctrl+C Safety (Bash Trap)

## Stop everything
function stop_tests() {
  echo -e "\n${CYAN}Stopping tests${NC} ${RED}.${WHITE}.${BLUE}.${NC}"
  exit 0
}
trap stop_tests SIGINT


# Runtime Variables

## Don't change these
skip=0
run=0



# Begin the Trials

## You

### you_tell
msg="[Tue Jan 08 22:52:24 2019] You told Parser, 'Get off your merchant and raid!'"
run_test "you_tell" "$msg"
((run++))

### you_say
skip_test "you_say"
((skip++))

### you_shout
skip_test "you_shout"
((skip++))

### you_group
msg="[Tue Jan 08 22:58:40 2019] You tell your party, 'incoming'"
run_test "you_group" "$msg"
((run++))

### you_ooc
skip_test "you_ooc"
((skip++))

### you_guild
skip_test "you_guild"
((skip++))

### you_auction
skip_test "you_auction"
((skip++))

### you_auction_wts:wtb
skip_test "you_auction_wts:wtb"
((skip++))

### you_auction_wts
skip_test "you_auction_wts"
((skip++))

### you_auction_wtb
skip_test "you_auction_wtb"
((skip++))

### you_new_zone
msg="[Sat Dec 29 21:56:56 2018] You have entered The Wakening Lands."
run_test "you_new_zone" "$msg"
msg="[Sat Dec 29 21:58:18 2018] You have entered Kael Drakkel."
run_test "you_new_zone" "$msg"
msg="[Sun Dec 30 10:28:06 2018] You have entered Butcherblock Mountains."
run_test "you_new_zone" "$msg"
((run++))

### you_healed
msg="[Sat Feb 02 15:39:26 2019] You have healed Parser for 470 points of damage."
run_test "you_healed" "$msg"
((run++))

### you_afk_on
skip_test "you_afk_on"
((skip++))

### you_lfg_on
msg="[Sun Jan 06 10:18:00 2019] You are now Looking For a Group."
run_test "you_lfg_on" "$msg"
((run++))

### you_afk_off
skip_test "you_afk_off"
((skip++))

### you_lfg_off
msg="[Thu Nov 01 10:07:49 2018] You are no longer Looking For a Group."
run_test "you_lfg_off" "$msg"
((run++))

### you_outfood
msg="[Tue Apr 19 20:54:46 2016] You are out of food."
run_test "you_outfood" "$msg"
((run++))

### you_outdrink
msg="[Tue May 17 17:23:10 2016] You are out of drink."
run_test "you_outdrink" "$msg"
((run++))

### you_outfooddrink
msg="[Thu Feb 08 20:59:13 2018] You are out of food and drink."
run_test "you_outfooddrink" "$msg"
((run++))

### you_outfoodlowdrink
msg="[Thu Mar 31 19:12:41 2016] You are out of food and low on drink."
run_test "you_outfoodlowdrink" "$msg"
((run++))

### you_outdrinklowfood
msg="[Thu Mar 31 19:12:41 2016] You are out of drink and low on food."
run_test "you_outdrinklowfood" "$msg"
((run++))

### you_thirsty
msg="[Thu Feb 08 19:00:19 2018] You are thirsty."
run_test "you_thirsty" "$msg"
((run++))

### you_hungry
msg="[Sat Apr 23 01:24:39 2016] You are hungry."
run_test "you_hungry" "$msg"
((run++))

### you_spell_forget
skip_test "you_spell_forgot"
((skip++))


## Spell

### spell_something
skip_test "spell_something"
((skip++))

### spell_fizzle
skip_test "spell_fizzle"
((skip++))

### spell_interrupted
skip_test "spell_interrupted"
((skip++))

### spell_damage
skip_test "spell_damage"
((skip++))

### spell_break_charm
skip_test "spell_break_charm"
((skip++))

### spell_break_ensare
skip_test "spell_break_ensare"
((skip++))

### spell_break
skip_test "spell_break"
((skip++))

### dot_damage
skip_test "dot_damage"
((skip++))


## Auction

### auction
skip_test "auction"
((skip++))

### auction_wts
skip_test "auction_wts"
((skip++))

### auction_wtb
skip_test "auction_wtb"
((skip++))


## Emotes

### emote_bow
skip_test "emote_bow"
((skip++))

### emote_thank
skip_test "emote_thank"
((skip++))

### emote_wave
skip_test "emote_wave"
((skip++))

### emote_dance
skip_test "emote_dance"
((skip++))

### emote_bonk
skip_test "emote_bonk"
((skip++))

### emote_smile
skip_test "emote_smile"
((skip++))

### emote_cheer
skip_test "emote_cheer"
((skip++))


## Weather

### weather_start_rain
msg="[Sat Feb 10 20:31:41 2018] It begins to rain."
run_test "weather_start_rain" "$msg"
((run++))

### weather_start_snow
msg="[Sun Feb 11 14:42:56 2018] It begins to snow."
run_test "weather_start_snow" "$msg"
((run++))

### weather_stop_rain
skip_test "weather_stop_rain"
((skip++))

### weather_stop_snow
skip_test "weather_stop_snow"
((skip++))


## Who

### who_top
msg="[Thu Feb 21 21:12:05 2019] Players in EverQuest:"
run_test "who_top" "$msg"
((run++))

### who_line
msg="[Sun Mar 03 09:05:21 2019] ---------------------------------"
run_test "who_line" "$msg"
((run++))

### who_player
msg="[Thu Feb 21 21:12:05 2019] [60 Hierophant] Indefinite (Wood Elf) <Tempest> ZONE: commons"
run_test "who_player" "$msg"
((run++))

### who_player_afk
msg="[Sun Nov 04 19:54:11 2018]  AFK [60 Hierophant] Phloem (Wood Elf) <Tempest>"
run_test "who_player_afk" "$msg"
((run++))

### who_player_linkdead
msg="[Sun Nov 04 19:48:03 2018]  <LINKDEAD>[60 Phantasmist] Dagner (Gnome) <Tempest>"
run_test "who_player_linkdead" "$msg"
((run++))

### who_total
msg="[Sun Mar 03 09:00:20 2019] There are no players in EverQuest that match those who filters."
run_test "who_total" "$msg"
msg="[Thu Feb 21 21:36:32 2019] There is 1 player in EverQuest."
run_test "who_total" "$msg"
msg="There are 4 players in EverQuest."
run_test "who_total" "$msg"
((run++))


## Other

skip_test "faction_line"
((skip++))

### target_cured
skip_test "target_cured"
((skip++))

### you_camping
msg="[Mon Nov 05 19:44:27 2018] It will take you about 30 seconds to prepare your camp."
run_test "you_camping" "$msg"
msg="[Fri Nov 09 18:17:05 2018] You abandon your preparations to camp."
run_test "you_camping" "$msg"
((run++))

### tell
msg="[Sat Dec 29 21:41:44 2018] Parser tells you, 'tell'"
run_test "tell" "$msg"
((run++))

### guild
msg="[Tue Jan 08 22:52:09 2019] Parser tells the guild, 'huzzah we are a guild'"
run_test "guild" "$msg"
((run++))

### group
msg="[Sat Dec 29 10:02:25 2018] Obbz tells the group, 'we have arrived'"
run_test "group" "$msg"
((run++))

### say
msg="Parser says, 'Incoming, here we go!'"
run_test "say" "$msg"
((run++))

### shout
msg="[Tue Nov 06 19:42:56 2018] Parser shouts, 'LF port to GD'"i
run_test "shout" "$msg"
((run++))

### ooc
msg="[Thu Feb 21 21:20:50 2019] Parser says out of character, 'Congratulations!'"
run_test "ooc" "$msg"
((run++))

### engage
msg="[Sat Dec 29 19:57:17 2018] a dracoliche engages Parser!"
run_test "engage" "$msg"
((run++))

### zoning
msg="[Sat Dec 29 21:55:59 2018] LOADING, PLEASE WAIT..."
run_test "zoning" "$msg"
((skip++))

### random
skip_test "random"
((skip++))

### loc
skip_test "loc"
((skip++))

### group_invite
skip_test "group_invite"
((skip++))

### target
skip_test "target"
((skip++))



# Tests completed
echo -e "\n\n --- COMPLETED ---"
echo -e "  ${LIGHT_GRAY}»${NC} ${CYAN}Skipped${NC} ${BLUE}:${NC} ${LIGHT_GRAY}$skip${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${CYAN}Run${NC} ${BLUE}:${NC} ${LIGHT_GRAY}$run${NC}"
