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
import re

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
                line = log_line.strip()
                # Split timestamp and message payload
                timestamp, payload = line[1:].split('] ', 1)
                timestamp = timestamp.split(' ')[3] + '.00'
                # Determine line type
                line_type = determine(payload)
                # Build and queue action
                new_message = eqa_struct.message(timestamp, line_type, 'null', 'null', payload.lower())
                action_q.put(new_message)

    except Exception as e:
        eqa_settings.log('process_log: Error on line ' +
                         str(sys.exc_info()[-1].tb_lineno) + ': ' + str(e))


def determine(line):
    """Determine type of line"""

    try:
        # Melee Combat
        if re.fullmatch(r'^[a-zA-Z\s]+ (hits|crushes|slashes|pierces|bashes|backstabs|bites|kicks|claws|gores|punches|strikes|slices) [a-zA-Z\s]+ for \d+ points of damage\.', line) is not None:
            line_type = "combat_other_melee"
        elif re.fullmatch(r'^[a-zA-Z\s]+ tries to (hit|crush|slash|pierce|bash|backstab|bite|kick|claw|gore|punch|strike|slice) [a-zA-Z\s]+, but misses\!', line) is not None:
            line_type = "combat_other_melee_miss"
        elif re.fullmatch(r'^[a-zA-Z\s]+ (hits|crushes|slashes|pierces|bashes|backstabs|bites|kicks|claws|gores|punches|strikes|slices) you for \d+ points of damage\.', line) is not None:
            line_type = "combat_you_receive_melee"
        elif re.fullmatch(r'^You (hit|crush|slash|pierce|bash|backstab|bite|kick|claw|gore|punch|strike|slice) [a-zA-Z\s]+ for \d+ points of damage\.', line) is not None:
            line_type = "combat_you_melee"
        elif re.fullmatch(r'^You try to (hit|crush|slash|pierce|bash|backstab|bite|kick|claw|gore|punch|strike|slice) [a-zA-Z\s]+, but miss\!', line) is not None:
            line_type = "combat_you_melee_miss"

        # Player Messages
        elif re.fullmatch(r'^\w+ tells you, \'.+\'$', line) is not None:
            line_type = "tell"
        elif re.fullmatch(r'^\w+ says, \'.+\'$', line) is not None:
            line_type = "say"
        elif re.fullmatch(r'^\w+ shouts, \'.+\'$', line) is not None:
            line_type = "shout"
        elif re.fullmatch(r'^\w+ tells the guild, \'.+\'$', line) is not None:
            line_type = "guild"
        elif re.fullmatch(r'^\w+ tells the group, \'.+\'$', line) is not None:
            line_type = "group"
        elif re.fullmatch(r'^\w+ says out of character, \'.+\'$', line) is not None:
            line_type = "ooc"
        elif re.fullmatch(r'^\w+ auctions, \'(.+|)(WTS|selling|Selling)(.+|)\'$', line) is not None:
            line_type = "auction_wts"
        elif re.fullmatch(r'^\w+ auctions, \'(.+|)(WTB|buying|Buying)(.+|)\'$', line) is not None:
            line_type = "auction_wtb"
        elif re.fullmatch(r'^\w+ auctions, \'.+\'$', line) is not None:
            line_type = "auction"
        elif re.fullmatch(r'^You told \w+, \'.+\'$', line) is not None:
            line_type = "you_tell"
        elif re.fullmatch(r'^You say, \'.+\'$', line) is not None:
            line_type = "you_say"
        elif re.fullmatch(r'^You shout, \'.+\'$', line) is not None:
            line_type = "you_shout"
        elif re.fullmatch(r'^You say to your guild, \'.+\'$', line) is not None:
            line_type = "you_guild"
        elif re.fullmatch(r'^You tell your party, \'.+\'$', line) is not None:
            line_type = "you_group"
        elif re.fullmatch(r'^You say out of character, \'.+\'$', line) is not None:
            line_type = "you_ooc"
        elif re.fullmatch(r'^You auction, \'.+\'$', line) is not None:
            line_type = "you_auction"

        # Player Status
        elif re.fullmatch(r'^Your Location is [-]?(?:\d*\.)?\d+\,\ [-]?(?:\d*\.)?\d+\,\ [-]?(?:\d*\.)?\d+$', line) is not None:
            line_type = "location"
        elif re.fullmatch(r'^You think you are heading (?:North(?:East|West)?|South(?:East|West)?|(?:Ea|We)st)\.$', line) is not None:
            line_type = "direction"
        elif re.fullmatch(r'^You have no idea what direction you are facing\.$', line) is not None:
            line_type = "direction_miss"
        elif re.fullmatch(r'^You have entered .+\.$', line) is not None:
            line_type = "you_new_zone"
        elif re.fullmatch(r'^You have healed .+ for \d+ points of damage\.$', line) is not None:
            line_type = "you_healed"
        elif re.fullmatch(r'^You are now A\.F\.K\. \(Away From Keyboard\)\.', line) is not None:
            line_type = "you_afk_on"
        elif re.fullmatch(r'^You are now Looking For a Group\.', line) is not None:
            line_type = "you_lfg_on"
        elif re.fullmatch(r'^You are no longer A\.F\.K\. \(Away From Keyboard\)\.', line) is not None:
            line_type = "you_afk_off"
        elif re.fullmatch(r'^You are no longer Looking For a Group\.', line) is not None:
            line_type = "you_lfg_off"
        elif re.fullmatch(r'^You are out of food\.', line) is not None:
            line_type = "you_outfood"
        elif re.fullmatch(r'^You are out of drink\.', line) is not None:
            line_type = "you_outdrink"
        elif re.fullmatch(r'^You are out of food and drink\.', line) is not None:
            line_type = "you_outfooddrink"
        elif re.fullmatch(r'^You are out of food and low on drink\.', line) is not None:
            line_type = "you_outfoodlowdrink"
        elif re.fullmatch(r'^You are out of drink and low on food\.', line) is not None:
            line_type = "you_outdrinklowfood"
        elif re.fullmatch(r'^You are thirsty\.', line) is not None:
            line_type = "you_thirsty"
        elif re.fullmatch(r'^You are hungry\.', line) is not None:
            line_type = "you_hungry"

        # Spells
        elif re.fullmatch(r'^You forget .+\.', line) is not None:
            line_type = "you_spell_forget"
        elif re.fullmatch(r'^\w+\'s spell fizzles\!$', line) is not None:
            line_type = "spell_fizzle"
        elif re.fullmatch(r'^Your spell is interrupted\.', line) is not None:
            line_type = "you_spell_fizzle"
        elif re.fullmatch(r'^\w+\'s casting is interrupted\!\.', line) is not None:
            line_type = "spell_fizzle"
        elif re.fullmatch(r'^Your target resisted the .+ spell\.$', line) is not None:
            line_type = "spell_resist"
        elif re.fullmatch(r'^.+ w(?:ere|as) hit by non-melee for \d+ ?(points of) damage\.$', line) is not None:
            line_type = "spell_damage"
        elif re.fullmatch(r'^\w+ begins to regenerate\.$', line)  is not None:
            line_type = "spell_regen"
        elif re.fullmatch(r'^Your charm spell has worn off\.$', line) is not None:
            line_type = "spell_break_charm"
        elif re.fullmatch(r'^Your Ensnare spell has worn off\.$', line) is not None:
            line_type = "spell_break_ensnare"

        # Emotes
        elif re.fullmatch(r'^\w+ bows before \w+\.$', line) is not None:
            line_type = "emote_bow"
        elif re.fullmatch(r'^\w+ thanks \w+ heartily\.$', line) is not None:
            line_type = "emote_thank"
        elif re.fullmatch(r'^\w+ waves at \w+\.$', line) is not None:
            line_type = "emote_wave"
        elif re.fullmatch(r'^\w+ grabs hold of \w+ and begins to dance with (?:h(?:er|im)|it)\.$', line) is not None:
            line_type = "emote_dance"
        elif re.fullmatch(r'^\w+ bonks \w+ on the head\!$', line) is not None:
            line_type = "emote_bonk"
        elif re.fullmatch(r'^\w+ beams a smile at (a|) \w+$', line) is not None:
            line_type = "emote_smile"
        elif re.fullmatch(r'^\w+ cheers at \w+$', line) is not None:
            line_type = "emote_cheer"

        # World Status
        elif re.fullmatch(r'^It begins to rain\.$', line) is not None:
            line_type = "weather_start_rain"
        elif re.fullmatch(r'^It begins to snow\.$', line) is not None:
            line_type = "weather_start_snow"
        elif re.fullmatch(r'^Players in EverQuest\:$', line) is not None:
            line_type = "who_top"
        elif re.fullmatch(r'^---------------------------------$', line) is not None:
            line_type = "who_line"
        elif re.fullmatch(r'^\[\d+ (?:(?:(?:Shadow )?Knigh|Hierophan|Revenan)t|(?:Elemental|Phantasm)ist|High Priest|Illusionist|(?:Grandmast|P(?:athfind|reserv)|C(?:hannel|avali)|(?:Enchan|Mas)t|(?:Begu|Def)il|Conjur|Sorcer|Wa(?:nder|rd)|(?:Crusa|Outri)d|Rang|Evok|Reav)er|Necromancer|(?:B(?:lackgu)?|Wiz)ard|Grave Lord|(?:T(?:roubadou|empla)|Warrio|Vica)r|A(?:rch Mage|ssassin)|Minstrel|Virtuoso|(?:(?:Myrmid|Champi)o|Magicia|Shama)n|(?:Discipl|Oracl|R(?:ogu|ak))e|Luminary|Warlock|Heretic|Paladin|(?:Warlor|Drui)d|Cleric|Mystic|Monk)\] \w+ \((?:Barbarian|Halfling|Half\-Elf|(?:Dark|High) Elf|Wood Elf|Skeleton|Erudite|Iksar|Troll|(?:Gnom|Ogr)e|Dwarf|Human)\)(?:( \<[a-zA-Z\s]+\> ZONE\: \w+| \<[a-zA-Z\s]+\>|))$', line) is not None:
            line_type = "who_player"
        elif re.fullmatch(r'^AFK \[\d+ (?:(?:(?:Shadow )?Knigh|Hierophan|Revenan)t|(?:Elemental|Phantasm)ist|High Priest|Illusionist|(?:Grandmast|P(?:athfind|reserv)|C(?:hannel|avali)|(?:Enchan|Mas)t|(?:Begu|Def)il|Conjur|Sorcer|Wa(?:nder|rd)|(?:Crusa|Outri)d|Rang|Evok|Reav)er|Necromancer|(?:B(?:lackgu)?|Wiz)ard|Grave Lord|(?:T(?:roubadou|empla)|Warrio|Vica)r|A(?:rch Mage|ssassin)|Minstrel|Virtuoso|(?:(?:Myrmid|Champi)o|Magicia|Shama)n|(?:Discipl|Oracl|R(?:ogu|ak))e|Luminary|Warlock|Heretic|Paladin|(?:Warlor|Drui)d|Cleric|Mystic|Monk)\] \w+ \((?:Barbarian|Halfling|Half\-Elf|(?:Dark|High) Elf|Wood Elf|Skeleton|Erudite|Iksar|Troll|(?:Gnom|Ogr)e|Dwarf|Human)\)(?:( \<[a-zA-Z\s]+\> ZONE\: \w+| \<[a-zA-Z\s]+\>|))$', line) is not None:
            line_type = "who_player_afk"
        elif re.fullmatch(r'^\<LINKDEAD\>\[\d+ (?:(?:(?:Shadow )?Knigh|Hierophan|Revenan)t|(?:Elemental|Phantasm)ist|High Priest|Illusionist|(?:Grandmast|P(?:athfind|reserv)|C(?:hannel|avali)|(?:Enchan|Mas)t|(?:Begu|Def)il|Conjur|Sorcer|Wa(?:nder|rd)|(?:Crusa|Outri)d|Rang|Evok|Reav)er|Necromancer|(?:B(?:lackgu)?|Wiz)ard|Grave Lord|(?:T(?:roubadou|empla)|Warrio|Vica)r|A(?:rch Mage|ssassin)|Minstrel|Virtuoso|(?:(?:Myrmid|Champi)o|Magicia|Shama)n|(?:Discipl|Oracl|R(?:ogu|ak))e|Luminary|Warlock|Heretic|Paladin|(?:Warlor|Drui)d|Cleric|Mystic|Monk)\] \w+ \((?:Barbarian|Halfling|Half\-Elf|(?:Dark|High) Elf|Wood Elf|Skeleton|Erudite|Iksar|Troll|(?:Gnom|Ogr)e|Dwarf|Human)\)(?:( \<[a-zA-Z\s]+\> ZONE\: \w+| \<[a-zA-Z\s]+\>|))$', line) is not None:
            line_type = "who_player_linkdead"
        elif re.fullmatch(r'^There (is|are) \d+ (player|players) in [a-zA-Z\s]+\.$', line) is not None:
            line_type = "who_total"
        elif re.fullmatch(r'^There are no players in EverQuest that match those who filters\.$', line) is not None:
            line_type = "who_total"
        elif re.fullmatch(r'^Your faction standing with \w+ (?:could not possibly get any|got) (?:better|worse)\.$', line) is not None:
            line_type = "faction_line"
        elif re.fullmatch(r'^Your target has been cured\.$', line) is not None:
            line_type = "target_cured"
        elif re.fullmatch(r'^It will take you about (30|25|20|15|10|5) seconds to prepare your camp\.$', line) is not None:
            line_type = "you_camping"
        elif re.fullmatch(r'^You abandon your preparations to camp\.$', line) is not None:
            line_type = "you_camping_abandoned"
        elif re.fullmatch(r'^[a-zA-Z\s]+ engages \w+\!$', line) is not None:
            line_type = "engage"
        elif re.fullmatch(r'^LOADING, PLEASE WAIT\.\.\.$', line) is not None:
            line_type = "zoning"
        elif re.fullmatch(r'^\*\*.+', line) is not None:
            line_type = "random"
        elif re.fullmatch(r'^\w+ invites you to join a group\.$', line) is not None:
            line_type = "group_invite"
        elif re.fullmatch(r'^(Targeted \((NPC|Player)\)\: [a-zA-Z\s]+|You no longer have a target\.)', line) is not None:
            line_type = "target"
        else:
            line_type = "undetermined"

    except Exception as e:
        eqa_settings.log('process_log (determine): Error on line ' +
                         str(sys.exc_info()[-1].tb_lineno) + ': ' + str(e))

    return line_type

if __name__ == '__main__':
    main()
