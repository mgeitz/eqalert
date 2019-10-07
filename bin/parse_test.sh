#! /bin/bash

#
# Test EQ Alert Parsing
#
#
#    * Ensure EQ Alert is running against the default character before testing
#


# Variables

## Things worth changing
CONFIG_PATH="$HOME/.eqa/config.json"

## Paths
EQ_LOGS=$(jq '.settings.paths.char_log' ${CONFIG_PATH})
DEFAULT_CHAR=$(jq '.characters.default' ${CONFIG_PATH} | tr -d '"')
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


# Functions

## Default Test: Append Message To Character Log
function run_test() {
  echo -e "\n  ${PURPLE}Type${NC} ${BLUE}:${NC} ${CYAN}$1${NC}"
  echo -e "  ${LIGHT_GRAY}»${NC} ${LIGHT_GRAY}$2${NC}"
  echo $2 >> "$CHAR_LOG"
  sleep 0.01
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
if [ -z $(pgrep -f eqalert.py) ]; then
  test_usage
  exit 0
fi


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
msg="[Tue Oct 30 20:53:59 2018] You say, 'anyone want potg?'"
run_test "you_say" "$msg"
((run++))

### you_shout
msg="[Wed Jun 24 21:25:49 2015] You shout, 'train to ent'"
run_test "you_shout" "$msg"
((run++))

### you_group
msg="[Tue Jan 08 22:58:40 2019] You tell your party, 'incoming'"
run_test "you_group" "$msg"
((run++))

### you_ooc
msg="[Sun Oct 28 20:21:10 2018] You say out of character, 'Hail for druid buffs at cb lift'"
run_test "you_ooc" "$msg"
((run++))

### you_guild
msg="[Fri Nov 02 16:46:37 2018] You say to your guild, 'Day drinking does me well'"
run_test "you_guild" "$msg"
((run++))

### you_auction
msg="[Mon Feb 05 19:27:20 2018] You auction, 'Spell: Bedlam PST!'"
run_test "you_auction" "$msg"
msg="[Fri May 06 22:23:05 2016] You auction, 'parser'"
run_test "you_auction" "$msg"
((run++))

### you_auction_wts:wtb
msg="[Mon Feb 21 13:49:05 2017] You auction, 'WTB Spell: Parser, WTS Super Powers'"
run_test "you_auction_wts:wtb" "$msg"
msg="[Mon Dec 16 09:52:27 2019] You auction, 'selling some shit, buying other shit'"
run_test "you_auction_wts:wtb" "$msg"
((run++))

### you_auction_wts
msg="[Fri May 06 22:23:05 2016] You auction, 'WTS Guardians Mace - Loam Encrusted Sleeves - Wu's Fighting Wristbands Small Wisdom Deity - Embroidered Black Cape - Kromzek Surveyor Scope - The Scent of Marr PST!'"
run_test "you_auction_wts" "$msg"
msg="[Fri Mar 12 04:43:26 2014] You auction, 'selling bags'"
run_test "you_auction_wts" "$msg"
((run++))

### you_auction_wtb
msg="[Mon Feb 05 19:27:20 2018] You auction, 'WTB Spell: Bedlam PST!'"
run_test "you_auction_wtb" "$msg"
msg="[Mon Feb 05 19:27:20 2018] You auction, 'buying novelty coins'"
((run++))

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
msg="[Sat Dec 29 20:51:36 2018] You are now A.F.K. (Away From Keyboard)."
run_test "you_afk_on" "$msg"
((run++))

### you_lfg_on
msg="[Sun Jan 06 10:18:00 2019] You are now Looking For a Group."
run_test "you_lfg_on" "$msg"
((run++))

### you_afk_off
msg="[Sat Dec 29 20:51:38 2018] You are no longer A.F.K. (Away From Keyboard)."
run_test "you_afk_off" "$msg"
((run++))

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
msg="[Sun May 06 10:07:21 2018] You forget Ensnare."
run_test "you_spell_forget" "$msg"
((run++))


## Spell

### spell_something
# wth is this
skip_test "spell_something"
((skip++))

### spell_fizzle
msg="[Sat Dec 29 20:26:38 2018] Parser's spell fizzles!"
run_test "spell_fizzle" "$msg"
((run++))

### spell_interrupted
msg="[Sat Dec 29 20:38:45 2018] Your spell is interrupted."
run_test "spell_interrupted" "$msg"
msg="[Sat Dec 29 20:36:22 2018] Parser's casting is interrupted!"
run_test "spell_interrupted" "$msg"
((run++))

### spell_resist
msg="[Mon Oct 29 18:28:33 2018] Your target resisted the Ensnare spell."
run_test "spell_resist" "$msg"
((run++))

### spell_damage
msg="[Sun Feb 11 00:29:35 2018] You were hit by non-melee for 17 damage."
run_test "spell_damage" "$msg"
msg="[Sat Feb 10 22:30:34 2018] Errkak Icepaw was hit by non-melee for 20 points of damage."
run_test "spell_damage" "$msg"
msg="[Sat Feb 10 21:46:05 2018] a crystalline watcher was hit by non-melee for 20 points of damage."
run_test "spell_damage" "$msg"
((run++))

### spell_regen
msg="[Sat Dec 29 22:26:46 2018] Slanging begins to regenerate."
run_test "spell_regen" "$msg"
((run++))

### spell_break_charm
msg="[Mon Feb 12 22:12:32 2018] Your charm spell has worn off."
run_test "spell_break_charm" "$msg"
((run++))

### spell_break_ensare
msg="[Mon Oct 29 18:49:03 2018] Your Ensnare spell has worn off."
run_test "spell_break_ensare" "$msg"
((run++))

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
msg="[Sun Mar 03 09:13:15 2019] Parser auctions, 'WTS Shrunken Goblin Skull Earring 2k'"
run_test "auction_wts" "$msg"
msg="[Sun Mar 03 09:13:15 2019] Parser auctions, 'selling a pretty flower 10k'"
run_test "auction_wts" "$msg"
((run++))

### auction_wtb
msg="[Sun Mar 03 09:14:20 2019] Parser auctions, 'WTB mask of the hunter'"
run_test "auction_wtb" "$msg"
msg="[Sun Mar 03 09:14:20 2019] Parser auctions, 'buying one half a parser'"
run_test "auction_wtb" "$msg"
((run++))


## Emotes

### emote_bow
msg="[Sat Apr 09 09:55:26 2016] Parser bows before Parsette."
run_test "emote_bow" "$msg"
((run++))

### eimote_thank
msg="[Sat Feb 10 22:43:15 2018] Parser thanks Parsette heartily."
run_test "emote_thank" "$msg"
((run++))

### emote_wave
msg="[Sun Feb 11 02:35:46 2018] Parser waves at Parsette."
run_test "emote_wave" "$msg"
((run++))

### emote_dance
msg="[Fri Jun 26 23:56:50 2015] Parser grabs hold of Parsette and begins to dance with her."
run_test "emote_dance" "$msg"
((run++))

### emote_bonk
msg="[Sat Apr 16 00:21:39 2016] Parsette bonks Parser on the head!"
run_test "emote_bonk" "$msg"
((run++))

### emote_smile
msg="[Mon Feb 12 23:23:48 2018] Parsette beams a smile at a Parser"
run_test "emote_smile" "$msg"
((run++))

### emote_cheer
msg="[Sun Feb 11 03:47:25 2018] Parser cheers at Parsette."
run_test "emote_cheer" "$msg"
((run++))


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
((run++))


## Other

### faction_line
msg="[Mon Feb 12 23:29:49 2018] Your faction standing with MayongMistmoore could not possibly get any better."
run_test "faction_line" "$msg"
msg="[Thu Jan 25 22:56:58 2018] Your faction standing with VenrilSathir could not possibly get any worse."
run_test "faction_line" "$msg"
msg="[Sun Feb 11 02:28:57 2018] Your faction standing with Chetari got worse."
run_test "faction_line" "$msg"
msg="[Sun Feb 11 03:44:51 2018] Your faction standing with Kromzek got better."
run_test "faction_line" "$msg"
((run++))

### target_cured
msg="[Fri Nov 09 20:16:41 2018] Your target has been cured."
run_test "target_cured" "$msg"
((run++))

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
msg="[Sat Dec 29 10:02:25 2018] Parser tells the group, 'we have arrived'"
run_test "group" "$msg"
((run++))

### say
msg="[Tue Jan 28 21:02:19 2018] Parser says, 'Incoming, here we go!'"
run_test "say" "$msg"
((run++))

### shout
msg="[Tue Nov 06 19:42:56 2018] Parser shouts, 'LF port to GD'"
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
((run++))

### random
msg="[Sat Feb 10 22:31:12 2018] **A Magic Die is rolled by Valreth."
run_test "random" "$msg"
msg="[Sun Jan 06 10:25:41 2019] **It could have been any number from 0 to 555, but this time it turned up a 528."
run_test "random" "$msg"
((run++))

### loc
msg="[Sun Feb 11 16:51:10 2018] Your Location is 2083.14, 3109.68, -154.26"
run_test "loc" "$msg"
((run++))

### group_invite
msg="[Mon Feb 12 23:40:36 2018] Parser invites you to join a group."
run_test "group_invite" "$msg"
((run++))

### target
msg="[Sun Mar 03 08:39:42 2019] Targeted (NPC): Parser"
run_test "target" "$msg"
msg="[Sun Mar 03 08:40:13 2019] Targeted (Player): Parsette"
run_test "target" "$msg"
msg="[Sat Mar 02 10:07:37 2019] You no longer have a target."
run_test "target" "$msg"
((run++))



# Tests completed
echo -e "\n\n --- COMPLETED ---"
echo -e "  ${LIGHT_GRAY}»${NC} ${CYAN}Skipped${NC} ${BLUE}:${NC} ${LIGHT_GRAY}$skip${NC}"
echo -e "  ${LIGHT_GRAY}»${NC} ${CYAN}Run${NC} ${BLUE}:${NC} ${LIGHT_GRAY}$run${NC}"
