#! /usr/bin/env python

"""
   Program:   EQ Alert
   File Name: eqa/lib/parser.py
   Copyright (C) 2019 Michael Geitz

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.
   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.
   You should have received a copy of the GNU General Public License along
   with this program; if not, write to the Free Software Foundation, Inc.,
   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

from collections import deque
import sys
import time

import eqa.lib.struct as eqa_struct
import eqa.lib.settings as eqa_settings


def last_line(character_log):
  """Reads and returns last line"""
  try:
    with open(character_log, 'r') as f:
      content = deque(f, 1)
    return content[0]
  except Exception as e:
    eqa_settings.log('last_line: ' + str(e))


def process(exit_flag, log_q, action_q):
  """
    Process: log_q
    Produce action_q
  """

  try:
    while not exit_flag.is_set():
      time.sleep(0.001)
      if not log_q.empty():
        # Read raw log line
        log_line = log_q.get()
        log_q.task_done()

        # Strip line of trailing space and lowercase everything
        line = log_line.strip().lower()
        # Split timestamp and message payload
        timestamp, payload = line[1:].split('] ', 1)
        timestamp = timestamp.split(' ')[3] + '.00'
        # Determine line type
        line_type = determine(payload)
        # Build and queue action
        new_message = eqa_struct.message(timestamp, line_type, 'null', 'null', payload)
        action_q.put(new_message)

  except Exception as e:
      eqa_settings.log('process_log: Error on line ' +
                       str(sys.exc_info()[-1].tb_lineno) + ': ' + str(e))


def determine(line):
    """Determine type of line"""

    line_type = "undetermined"
    line_list = line.split(' ')

    try:
        # You
        if line_list[0] == "you":
            # You told
            if line_list[1] == "told":
                line_type = "you_tell"
            # You say
            elif line_list[1] == "say,":
                line_type = "you_say"
            # You shout
            elif line_list[1] == "shout,":
                line_type = "you_shout"
            # You say to ...
            elif line_list[1] == "say":
                if line_list[4] == "character,":
                    line_type = "you_ooc"
                if line_list[4] == "guild,":
                    line_type = "you_guild"
            # You auction
            elif line_list[1] == "auction,":
                line_type = "you_auction"
                if "wts" in line or "selling" in line and "wtb" in line or "buying" in line:
                    line_type = "you_auction_wts:wtb"
                if "wts" in line or "selling" in line:
                    line_type = "you_auction_wts"
                if "wtb" in line or "buying" in line:
                    line_type = "you_auction_wtb"
            # You have
            elif line_list[1] == "have":
                if line_list[2] == "entered":
                    line_type = "you_new_zone"
                elif line_list[5] == "direction":
                    line_type = "direction_miss"
                elif line_list[2] == "healed":
                    line_type = "you_healed"
            # You think
            elif line_list[1] == "think":
                if line_list[4] == "heading":
                    line_type = "direction"
            # You were
            elif line_list[1] == "were":
                if line_list[2] == "hit":
                    if line_list[4] == "non-melee":
                        line_type = "hit_you_non_melee"
            # You are
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
            # You forget
            elif line_list[1] == "forget":
                line_type == "you_spell_forget"
            # You ... hungry
            elif "hungry." in line_list:
                line_type = "you_hungry"
            # You ... party,
            elif "party," in line:
                line_type = "you_group"

        # Your
        elif line_list[0] == "your":
            # Your location
            if line_list[1] == "location":
                if line_list[2] == "is":
                    line_type = "location"
            # Your spell
            elif line_list[1] == "spell":
                if line_list[3] == "interrupted.":
                    line_type = "spell_interrupted"
            # Your ... spell
            elif line_list[2] == "spell":
                if line_list[1] == "charm":
                    line_type = "spell_break_charm"
                elif line_list[1] == "ensnare":
                    line_type = "spell_break_ensare"
                else:
                    line_type = "spell_break"
            # Your faction
            elif line_list[1] ==  "faction":
                line_type = "faction_line"
            # Your target
            elif line_list[1] == "target":
                if line_list[2] == "resisted":
                    line_type = "spell_resist"
                elif line_list[4] == "cured.":
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
                    line_type = "spell_regen"

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

    except Exception as e:
        eqa_settings.log('determine: Error on line ' +
                         str(sys.exc_info()[-1].tb_lineno) + ': ' + str(e))


if __name__ == '__main__':
    main()
