#! /usr/bin/env python

"""
Returns the determined line type of a line in eq.log
"""
__author__ = "Michael Geitz"
__version__ = "0.1.1"

from collections import deque
import pyinotify

import eqa_struct


def parse(line, message):
    """Consume the log and produce santized messages"""

    timestamp, payload = line[1:].split('] ', 1)
    line_type = determine(payload.lower())
    new_message = eqa_struct.message(line_type, timestamp, 'null', 'null', payload)

    message.put(new_message)


def monitor(stop_watcher, character_log, message):
    """Parse on file changes"""
    log_watch = pyinotify.WatchManager()
    log_notifier = pyinotify.Notifier(log_watch)

    def callback(event):
        if event.mask == pyinotify.IN_CLOSE_WRITE:
            parse(read(character_log), message)

    log_watch.add_watch(character_log, pyinotify.IN_CLOSE_WRITE, callback)

    try:
        while not stop_watcher.is_set():
            log_notifier.process_events()
            if log_notifier.check_events():
                log_notifier.read_events()
            if stop_watcher.is_set():
                log_notifier.stop()

    except Exception as e:
        stop_watcher.set()
        log_notifier.stop()


def read(log_path):
    """Reads and returns the eqlog.txt file"""

    with open(log_path, 'r') as f:
        content = deque(f, 1)
    return content[0]


def determine(line):
    """Determine type of line"""

    line_type = "undetermined"
    line_list = line.split(' ')

   # chat your player initiates
    if line_list[0] == "you":
        if line_list[1] == "told":
            line_type = "you_tell"
        elif line_list[1] == "say,":
            line_type = "you_say"
        elif line_list[1] == "shout,":
            line_type = "you_shout"
        elif "party," in line:
            line_type = "you_group"
        elif line_list[1] == "say":
            if line_list[4] == "character,":
                line_type = "you_ooc"
            if line_list[4] == "guild,":
                line_type = "you_guild"
        elif line_list[1] == "auction,":
            line_type = "you_auction"
            if "wts" in line or "selling" in line and "wtb" in line or "buying" in line:
                line_type = "you_auction_wts:wtb"
            if "wts" in line or "selling" in line:
                line_type = "you_auction_wts"
            if "wtb" in line or "buying" in line:
                line_type = "you_auction_wtb"
        elif line_list[1] == "have":
            if line_list[2] == "entered":
                line_type = "you_new_zone"
            elif line_list[2] == "healed":
                line_type = "you_healed"
        elif "hungry." in line_list:
            line_type = "you_hungry"
        elif line_list[1] == "are":
            if line_list[2] == "now":
                if "a.f.k." in line:
                    line_type = "you_afk_on"
                elif line.endswith("looking for a group."):
                    line_type = "you_lfg_on"
            elif line_list[2] == "no":
                if "a.f.k." in line:
                    line_type = "you_afk_off"
                elif line.endswith("looking for a group."):
                    line_type = "you_lfg_off"
            elif line_list[2] == "out":
                if line_list[-1] == "food." and "drink" not in line and "drink." not in line:
                    line_type = "you_outfood"
                elif line_list[-1] == "drink." and "food" not in line and "food." not in line:
                    line_type = "you_outdrink"
                elif line.endswith("food and drink."):
                    line_type = "you_outfooddrink"
                elif line.endswith("drink and low on food."):
                    line_type = "you_outdrinklowfood"
                elif line.endswith("food and low on drink."):
                    line_type = "you_outfoodlowdrink"
            elif line_list[-1] == "thirsty.":
                line_type = "you_thirsty"
            elif line_list[-1] == "hungry.":
                line_type = "you_hungry"
        elif line_list[1] == "forget":
            line_type == "you_spell_forget"

    elif line_list[0] == "your":
        if line_list[2] == "spell":
            if line_list[1] == "charm":
                line_type = "spell_break_charm"
            elif line_list[1] == "ensnare":
                line_type = "spell_break_ensare"
            else:
                line_type = "spell_break"
        elif line_list[1] ==  "faction":
            line_type = "faction_line"
        elif line_list[1] == "target":
            if line_list[4] == "cured.":
                line_type = "target_cured"
    elif line_list[0].startswith("-"):
        line_type = "who_line"
    elif len(line_list) == 1:
        line_type = "mysterious_oner"

    # chat from other players
    elif line_list[1] == "tells":
        if line_list[2] == "you,":
            line_type = "tell" # or emote
        if line_list[3] == "guild,":
            line_type = "guild" # or emote
        if line_list[3] == "group,":
            line_type = "group" # or emote
    elif line_list[1] == "says,":
        line_type = "say" # or emote
    elif line_list[1] == "shouts,":
        line_type = "shout" # or emote
    elif line_list[1] == "says":
        if line_list[4] == "character,":
            line_type = "ooc" # or emote
    elif line_list[1] == "auctions,":
        line_type = "auction" # or emote
        #if "wts" in line or "selling" in line and "wtb" in line or "buying" in line:
        #    line_type = "auction_wts:wtb"
        if "wts" in line or "selling" in line:
            line_type = "auction_wts"
        elif "wtb" in line or "buying" in line:
            line_type = "auction_wtb"

    # spells / casting
    elif line_list[1] == "spell":
        line_type = "spell_something"
        if line_list[2] == "fizzles!":
            line_type = "spell_fizzle"
    elif line_list[1] == "casting":
        if line_list[3] == "interrupted!":
           line_type = "spell_interrupted"
    elif line_list[1] == "begins":  # assumes only spell messages have [player] begins...
        if len(line_list) > 3:
            if line_list[3] == "regenerate.":
                line_list = "spell_regen"

    # spell damage (has/was)
    elif "has" in line_list:
        if line_list[line_list.index("has") + 1] == "taken" and line_list[line_list.index("has") + 3] == "damage":
            line_type = "dot_damage"
    elif "was" in line_list:
        if line_list[line_list.index("was") + 1] == "hit" and line_list[line_list.index("was") + 3] == "non-melee":
            line_type = "spell_damage"

    # engage messages
    elif "engages" in line_list and line_list[-1].endswith("!"):
        line_type = "engage"

    # combat
    #elif line_list[-2] == "but" and line_list[-1] == "misses!":
    #    line_type = "melee_miss"
    #elif line_list[-1] == "damage.":
    #    if len(line_list) > 2:
    #        if line_list[-3] == "points":
    #            line_type = "melee_hit"

    # other
    # Damn falling messages causing a problem
    #elif "injured" in line:
    #    if line_list[2] == "injured":
    #        if line_list[-1] == "falling.":
    #            line_type == "fall_damage"

    elif line_list[0] == "loading,":
        line_type = "zoning"
    elif line_list[0][0] == "*":
        line_type = "random"
    # chat from in game prompts or commands
    elif line_list[1] == "Location" and line_list[0] == "Your":
        line_type = "loc"
    elif line_list[0] == "To" and line_list[1] == "join":
        line_type = "group_invite"
    elif line_list[0] == "there" and line_list[1] == "are":
        line_type = "who_total"
    elif line_list[0].startswith("["):
        line_type = "who_player"
    elif line_list[0] == "afk":
        line_type = "who_player_afk"
    elif line_list[0].startswith("<linedead>"):
        line_type = "who_player_linkdead"
    elif line_list[0] ==  "players" or line_list[0] == "Friends":
        line_type = "who_top"
    elif line_list[0] == "targeted" :
        line_type = "target"

    # possible emotes
    elif line_list[1] == "bows" :
        line_type = "emote_bow"
    elif line_list[1] == "thanks" :
        line_type = "emote_thank"
    elif line_list[1] == "waves" :
        line_type = "emote_wave"
    elif line_list[1] == "dances" :
        line_type = "emote_dance"
    elif line_list[1] == "bonks" :
        line_type = "emote_bonk"
    elif line_list[1] == "beams" :
        line_type = "emote_smile"
    elif line_list[1] == "cheers." or line_list[1] == "cheers":
        line_type = "emote_cheer"

    # other
    elif line_list[0] == "it":
        if line_list[1] == "begins":
            if "rain." in line:
                line_type = "weather_start_rain"
            if "snow." in line:
                line_type = "weather_start_snow"
        elif line_list[1] == "stops":
            if "raining." in line:
                line_type = "weather_stop_rain" # the sky clears as the rain ceases to fall.
            if "snowing." in line:
                line_type = "weather_stop_snow"
        elif line_list[-1] == "camp.":
            line_type == "you_camping"

    return line_type

if __name__ == '__main__':
    main()

