#! /bin/bash

#
# Test EQ Alert Parsing
#

# Set ctrl+c exit
function stop_tests() {
  echo -e "\n\033[0;36mStopping tests\033[0m ..."
  exit 0
}
trap stop_tests SIGINT

# Get default char log for testing
EQ_LOGS=$(jq '.settings.paths.char_log' config.json)
DEFAULT_CHAR=$(jq '.characters.default' config.json | tr -d '"')
CHAR_LOG="${EQ_LOGS//\"}eqlog_${DEFAULT_CHAR^}_project1999.txt"

ACTIVE=$(pgrep -f eqalert.py)

if [ -z $ACTIVE ]; then
  echo -e "\n\033[0;36mUsage\033[0m"
  echo -e "./parse_test.sh"
  echo -e "\nEnsure EQ Alert is running"
  exit 0
fi

skip=0
run=0

# you_tell
echo -e "\033[0;34m\033[0;34mType\033[0m\033[0m you_tell"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# you_say
echo -e "\033[0;34mType\033[0m: you_say"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# you_shout
echo -e "\033[0;34mType\033[0m: you_shout"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# you_group
echo -e "\033[0;34mType\033[0m: you_group"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# you_ooc
echo -e "\033[0;34mType\033[0m: you_ooc"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# you_guild
echo -e "\033[0;34mType\033[0m: you_guild"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# you_auction
echo -e "\033[0;34mType\033[0m: you_auction"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# you_auction_wts:wtb
echo -e "\033[0;34mType\033[0m: you_auction_wts:wtb"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# you_auction_wts
echo -e "\033[0;34mType\033[0m: you_auction_wts"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# you_auction_wtb
echo -e "\033[0;34mType\033[0m: you_auction_wtb"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# you_new_zone
echo -e "\033[0;34mType\033[0m: you_new_zone"
echo "[Sat Dec 29 21:56:56 2018] You have entered The Wakening Lands." >> "$CHAR_LOG"
sleep 0.02
echo "[Sat Dec 29 21:58:18 2018] You have entered Kael Drakkel." >> "$CHAR_LOG"
sleep 0.02
echo "[Sun Dec 30 10:28:06 2018] You have entered Butcherblock Mountains." >> "$CHAR_LOG"
sleep 0.02
echo -e "  » \033[0;35mrun\033[0m"
((run++))

# you_healed
echo -e "\033[0;34mType\033[0m: you_healed"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# you_hungry
echo -e "\033[0;34mType\033[0m: you_hungry"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# you_afk_on
echo -e "\033[0;34mType\033[0m: you_afk_on"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# you_lfg_on
echo -e "\033[0;34mType\033[0m: you_lfg_on"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# you_afk_off
echo -e "\033[0;34mType\033[0m: you_afk_off"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# you_lfg_off
echo -e "\033[0;34mType\033[0m: you_lfg_off"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# you_outfood
echo -e "\033[0;34mType\033[0m: you_outfood"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# you_outdrink
echo -e "\033[0;34mType\033[0m: you_outdrink"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# you_outfooddrink
echo -e "\033[0;34mType\033[0m: you_outfooddrink"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# you_outfoodlowdrink
echo -e "\033[0;34mType\033[0m: you_outfoodlowdrink"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# you_outdrinklowfood
echo -e "\033[0;34mType\033[0m: you_outdrinklowfood"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# you_thirsty
echo -e "\033[0;34mType\033[0m: you_thirsty"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# you_hungry
echo -e "\033[0;34mType\033[0m: you_hungry"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# you_spell_forget
echo -e "\033[0;34mType\033[0m: you_spell_forgot"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# spell_break_charm
echo -e "\033[0;34mType\033[0m: spell_break_charm"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# spell_break_ensare
echo -e "\033[0;34mType\033[0m: spell_break_ensare"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# spell_break
echo -e "\033[0;34mType\033[0m: spell_break"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# faction_line
echo -e "\033[0;34mType\033[0m: faction_line"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# target_cured
echo -e "\033[0;34mType\033[0m: target_cured"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# who_line
echo -e "\033[0;34mType\033[0m: who_line"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# mysterious_oner
echo -e "\033[0;34mType\033[0m: mysterious_oner"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# tell
echo -e "\033[0;34mType\033[0m: tell"
echo "[Sat Dec 29 21:41:44 2018] Parser tells you, 'tell'" >> "$CHAR_LOG"
sleep 0.01
echo -e "  » \033[0;35mrun\033[0m"
((run++))

# guild
echo -e "\033[0;34mType\033[0m: guild"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# group
echo -e "\033[0;34mType\033[0m: group"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# say
echo -e "\033[0;34mType\033[0m: say"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# shout
echo -e "\033[0;34mType\033[0m: shout"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# ooc
echo -e "\033[0;34mType\033[0m: ooc"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# auction
echo -e "\033[0;34mType\033[0m: auction"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# auction_wts
echo -e "\033[0;34mType\033[0m: auction_wts"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# auction_wtb
echo -e "\033[0;34mType\033[0m: auction_wtb"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# spell_something
echo -e "\033[0;34mType\033[0m: spell_something"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# spell_fizzle
echo -e "\033[0;34mType\033[0m: spell_fizzle"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# spell_interrupted
echo -e "\033[0;34mType\033[0m: spell_interrupted"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# dot_damage
echo -e "\033[0;34mType\033[0m: dot_damage"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# spell_damage
echo -e "\033[0;34mType\033[0m: spell_damage"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# engage
echo -e "\033[0;34mType\033[0m: engage"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# zoning
echo -e "\033[0;34mType\033[0m: zoning"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# random
echo -e "\033[0;34mType\033[0m: random"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# loc
echo -e "\033[0;34mType\033[0m: loc"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# group_invite
echo -e "\033[0;34mType\033[0m: group_invite"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# who_total
echo -e "\033[0;34mType\033[0m: who_total"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# who_player
echo -e "\033[0;34mType\033[0m: who_player"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# who_player_afk
echo -e "\033[0;34mType\033[0m: who_player_afk"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# who_player_linkdead
echo -e "\033[0;34mType\033[0m: who_player_linkdead"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# who_top
echo -e "\033[0;34mType\033[0m: who_top"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# target
echo -e "\033[0;34mType\033[0m: target"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# emote_bow
echo -e "\033[0;34mType\033[0m: emote_bow"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# emote_thank
echo -e "\033[0;34mType\033[0m: emote_thank"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# emote_wave
echo -e "\033[0;34mType\033[0m: emote_wave"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# emote_dance
echo -e "\033[0;34mType\033[0m: emote_dance"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# emote_bonk
echo -e "\033[0;34mType\033[0m: emote_bonk"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# emote_smile
echo -e "\033[0;34mType\033[0m: emote_smile"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# emote_cheer
echo -e "\033[0;34mType\033[0m: emote_cheer"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# weather_start_rain
echo -e "\033[0;34mType\033[0m: weather_start_rain"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# weather_start_snow
echo -e "\033[0;34mType\033[0m: weather_start_snow"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# weather_stop_rain
echo -e "\033[0;34mType\033[0m: weather_stop_rain"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# weather_stop_snow
echo -e "\033[0;34mType\033[0m: weather_stop_snow"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))

# you_camping
echo -e "\033[0;34mType\033[0m: you_camping"
echo -e "  » \033[0;36mskip\033[0m"
((skip++))


# Tests completed
echo -e " --- COMPLETED ---"
echo -e "  » \033[0;36mSkipped: \033[0;35m$skip\033[0m"
echo -e "  » \033[0;36mRun \033[0;35m$run\033[0m"
