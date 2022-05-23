#! /usr/bin/env python

"""
   Program:   EQ Alert
   File Name: eqa/lib/parser.py
   Copyright (C) 2022 Michael Geitz

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


def process(exit_flag, log_q, action_q):
    """
    Process: log_q
    Produce: action_q
    """

    try:
        while not exit_flag.is_set():

            # Sleep between empty checks
            queue_size = log_q.qsize()
            if queue_size < 1:
                time.sleep(0.01)

            # Check queue for message
            if not log_q.empty():
                ## Read new message
                log_line = log_q.get()
                ## Strip line of any trailing space
                line = log_line.strip()
                ## If line fits assumed log line structure
                if (
                    re.fullmatch(
                        r"^\[(?:Fri|Mon|S(?:at|un)|T(?:hu|ue)|Wed) (?:A(?:pr|ug)|Dec|Feb|J(?:an|u[ln])|Ma[ry]|Nov|Oct|Sep) [0-9]{2} [0-9]{2}\:[0-9]{2}\:[0-9]{2} [0-9]{4}\] .+",
                        line,
                    )
                    is not None
                ):
                    ### Split timestamp and message payload
                    timestamp, payload = line[1:].split("] ", 1)
                    timestamp = timestamp.split(" ")[3] + ".00"
                    ### Determine line type
                    line_type = determine(payload)
                    ### Build and queue action
                    new_message = eqa_struct.message(
                        timestamp, line_type, "null", "null", payload
                    )
                    action_q.put(new_message)
                else:
                    eqa_settings.log("process_log: Cannot process: " + line)

                log_q.task_done()

    except Exception as e:
        eqa_settings.log(
            "process_log: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def determine(line):
    """Determine type of line"""

    try:
        # Melee
        line_type = check_melee(line)
        if line_type is not None:
            return line_type

        # Spell
        line_type = check_spell(line)
        if line_type is not None:
            return line_type

        # Spell Specific
        line_type = check_spell_specific(line)
        if line_type is not None:
            return line_type

        # Pets
        line_type = check_pets(line)
        if line_type is not None:
            return line_type

        # Received Player Chat
        line_type = check_received_chat(line)
        if line_type is not None:
            return line_type

        # Sent Player Chat
        line_type = check_sent_chat(line)
        if line_type is not None:
            return line_type

        # Command Output
        line_type = check_command_output(line)
        if line_type is not None:
            return line_type

        # System Messages
        line_type = check_system_messages(line)
        if line_type is not None:
            return line_type

        # Group System Messages
        line_type = check_group_system_messages(line)
        if line_type is not None:
            return line_type

        # Loot Trade Messages
        line_type = check_loot_trade(line)
        if line_type is not None:
            return line_type

        # Emotes
        line_type = check_emotes(line)
        if line_type is not None:
            return line_type

        # Who
        line_type = check_who(line)
        if line_type is not None:
            return line_type

        # No Match Found
        return "undetermined"

    except Exception as e:
        eqa_settings.log(
            "process_log (determine): Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )

    return line_type


def check_melee(line):
    """
    Check line for melee
    """
    try:
        # Melee Combat
        if (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ (mauls|hits|crushes|slashes|pierces|bashes|backstabs|bites|kicks|claws|gores|punches|strikes|slices) (you|YOU) for \d+ point(s|) of damage\.$",
                line,
            )
            is not None
        ):
            return "combat_you_receive_melee"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ (mauls|hits|crushes|slashes|pierces|bashes|backstabs|bites|kicks|claws|gores|punches|strikes|slices) [a-zA-Z`\s]+ for \d+ point(s|) of damage\.$",
                line,
            )
            is not None
        ):
            return "combat_other_melee"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ tries to (maul|hit|crush|slash|pierce|bash|backstab|bite|kick|claw|gore|punch|strike|slice) [a-zA-Z`\s]+, but misses\!$",
                line,
            )
            is not None
        ):
            return "combat_other_melee_miss"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ tries to (maul|hit|crush|slash|pierce|bash|backstab|bite|kick|claw|gore|punch|strike|slice) [a-zA-Z\s]+, but [a-zA-Z`\s]+ dodges\!$",
                line,
            )
            is not None
        ):
            return "combat_other_melee_dodge"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ tries to (maul|hit|crush|slash|pierce|bash|backstab|bite|kick|claw|gore|punch|strike|slice) [a-zA-Z\s]+, but [a-zA-Z`\s]+ is INVULNERABLE\!$",
                line,
            )
            is not None
        ):
            return "combat_other_melee_invulnerable"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ tries to (maul|hit|crush|slash|pierce|bash|backstab|bite|kick|claw|gore|punch|strike|slice) [a-zA-Z`\s]+, but [a-zA-Z`\s]+ parries\!$",
                line,
            )
            is not None
        ):
            return "combat_other_melee_parry"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ tries to (maul|hit|crush|slash|pierce|bash|backstab|bite|kick|claw|gore|punch|strike|slice) [a-zA-Z`\s]+, but [a-zA-Z`\s]+ blocks\!$",
                line,
            )
            is not None
        ):
            return "combat_other_melee_block"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ tries to (maul|hit|crush|slash|pierce|bash|backstab|bite|kick|claw|gore|punch|strike|slice) [a-zA-Z`\s]+, but [a-zA-Z`\s]+ ripostes\!$",
                line,
            )
            is not None
        ):
            return "combat_other_melee_reposte"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ tries to (maul|hit|crush|slash|pierce|bash|backstab|bite|kick|claw|gore|punch|strike|slice) [a-zA-Z`\s]+, but [a-zA-Z`\s]+'s magical skin absorbs the blow\!$",
                line,
            )
            is not None
        ):
            return "combat_other_rune_damage"
        elif (
            re.fullmatch(
                r"^You (maul|hit|crush|slash|pierce|bash|backstab|bite|kick|claw|gore|punch|strike|slice) [a-zA-Z`\s]+ for \d+ point(s|) of damage\.$",
                line,
            )
            is not None
        ):
            return "combat_you_melee"
        elif (
            re.fullmatch(
                r"^You try to (maul|hit|crush|slash|pierce|bash|backstab|bite|kick|claw|gore|punch|strike|slice) [a-zA-Z`\s]+, but miss\!$",
                line,
            )
            is not None
        ):
            return "combat_you_melee_miss"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ Scores a critical hit\!\(\d+\)$", line)
            is not None
        ):
            return "combat_other_melee_crit"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ has landed a Thunderous Kick\! \(\d+\)$", line)
            is not None
        ):
            return "combat_other_melee_crit_kick"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ lands a Crippling Blow\!\(\d+\)$", line)
            is not None
        ):
            return "combat_other_melee_crip_blow"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ has become (ENRAGED|enraged)\.$", line)
            is not None
        ):
            return "mob_enrage_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ is no longer enraged\.$", line) is not None:
            return "mob_enrage_off"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ goes on a (RAMPAGE|rampage)\!$", line)
            is not None
        ):
            return "mob_rampage_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ has been slain by [a-zA-Z\s]+\!$", line)
            is not None
        ):
            return "mob_slain_other"
        elif re.fullmatch(r"^You have slain [a-zA-Z`\s]+\!$", line) is not None:
            return "mob_slain_you"
        elif (
            re.fullmatch(r"^Your target is out of range, get closer\!$", line)
            is not None
        ):
            return "mob_out_of_range"
        elif re.fullmatch(r"^You gain experience\!\!$", line) is not None:
            return "experience_solo"
        elif (
            re.fullmatch(r"^You regain some experience from resurrection\.$", line)
            is not None
        ):
            return "experience_solo_resurrection"
        elif re.fullmatch(r"^You gain party experience\!\!$", line) is not None:
            return "experience_group"
        elif re.fullmatch(r"^You have lost experience\.$", line) is not None:
            return "experience_lost"

        return None

    except Exception as e:
        eqa_settings.log(
            "process_log (check_melee): Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def check_spell(line):
    """
    Check line for spell
    """
    try:
        if re.fullmatch(r"^[a-zA-Z`\s]+ begins to cast a spell\.$", line) is not None:
            return "spell_cast_other"
        elif re.fullmatch(r"^You begin casting [a-zA-Z\:`\s\']+\.$", line) is not None:
            return "spell_cast_you"
        elif (
            re.fullmatch(r"^Your [a-zA-Z\s`\:\']+ begins to glow\.$", line) is not None
        ):
            return "spell_cast_item_you"
        elif re.fullmatch(r"^\w+\'s spell fizzles\!$", line) is not None:
            return "spell_fizzle_other"
        elif re.fullmatch(r"^Your spell fizzles\!$", line) is not None:
            return "spell_fizzle_you"
        elif re.fullmatch(r"^Your spell did not take hold\.$", line) is not None:
            return "spell_not_hold"
        elif (
            re.fullmatch(r"^Insufficient Mana to cast this spell\!$", line) is not None
        ):
            return "spell_cast_oom"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s casting is interrupted\!$", line)
            is not None
        ):
            return "spell_interrupt_other"
        elif re.fullmatch(r"^Your spell is interrupted\.$", line) is not None:
            return "spell_interrupt_you"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ regains concentration and continues casting\.$", line
            )
            is not None
        ):
            return "spell_recover_other"
        elif (
            re.fullmatch(
                r"^You regain your concentration and continue your casting\.$", line
            )
            is not None
        ):
            return "spell_recover_you"
        elif re.fullmatch(r"^Your target resisted the .+ spell\.$", line) is not None:
            return "spell_resist_you"
        elif (
            re.fullmatch(
                r"^.+ w(?:ere|as) hit by non-melee for \d+ ?(points of) damage\.$", line
            )
            is not None
        ):
            return "spell_damage"
        elif (
            re.fullmatch(r"^Beginning to memorize [a-zA-Z`\s\'\:]+\.\.\.$", line)
            is not None
        ):
            return "spell_memorize_begin"
        elif (
            re.fullmatch(r"^You have finished memorizing [a-zA-Z`\s\'\:]+\.$", line)
            is not None
        ):
            return "spell_memorize_finish"
        elif (
            re.fullmatch(
                r"^$You cannot memorize a spell you already have memorized\.", line
            )
            is not None
        ):
            return "spell_memorize_already"
        elif re.fullmatch(r"^You forget .+\.", line) is not None:
            return "spell_forget"
        elif re.fullmatch(r"^Your [a-zA-Z\s]+ spell has worn off\.$", line) is not None:
            return "spell_worn_off"
        elif (
            re.fullmatch(
                r"^You try to cast a spell on [a-zA-Z`\s]+, but they are protected\.$",
                line,
            )
            is not None
        ):
            return "spell_protected"
        elif re.fullmatch(r"^You haven't recovered yet\.\.\.$", line) is not None:
            return "spell_cooldown_active"
        elif (
            re.fullmatch(r"^You must be standing to cast a spell\.$", line) is not None
        ):
            return "spell_sitting"
        elif (
            re.fullmatch(r"^You must first select a target for this spell\!$", line)
            is not None
        ):
            return "spell_no_target"
        elif (
            re.fullmatch(r"^A missed note brings \w+'s song to a close\!$", line)
            is not None
        ):
            return "song_interrupted_other"

        return None

    except Exception as e:
        eqa_settings.log(
            "process_log (check_spell): Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def check_received_chat(line):
    """
    Check line for received chat
    """

    try:
        if re.fullmatch(r"^[a-zA-Z\.]+ tells you, \'(.+|)\'$", line) is not None:
            return "tell"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ tells you, \'.+\'$", line) is not None:
            return "tell_npc"
        elif re.fullmatch(r"^\w+ says, \'.+\'$", line) is not None:
            return "say"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ says(,|) \'.+\'$", line) is not None:
            return "say_npc"
        elif re.fullmatch(r"^\w+ shouts, \'.+\'$", line) is not None:
            return "shout"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ shouts, \'.+\'$", line) is not None:
            return "shout_npc"
        elif re.fullmatch(r"^\w+ tells the guild, \'.+\'$", line) is not None:
            return "guild"
        elif re.fullmatch(r"^\w+ tells the group, \'.+\'$", line) is not None:
            return "group"
        elif re.fullmatch(r"^\w+ says out of character, \'.+\'$", line) is not None:
            return "ooc"
        elif (
            re.fullmatch(r"^\w+ auctions, \'(.+|)(WTS|selling|Selling)(.+|)\'$", line)
            is not None
        ):
            return "auction_wts"
        elif (
            re.fullmatch(r"^\w+ auctions, \'(.+|)(WTB|buying|Buying)(.+|)\'$", line)
            is not None
        ):
            return "auction_wtb"
        elif re.fullmatch(r"^\w+ auctions, \'.+\'$", line) is not None:
            return "auction"

        return None

    except Exception as e:
        eqa_settings.log(
            "process_log (check_received_chat): Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def check_sent_chat(line):
    """
    Check line for sent chat
    """

    try:
        if re.fullmatch(r"^You told \w+(, \'| \'\[queued\],).+\'$", line) is not None:
            return "tell_you"
        elif re.fullmatch(r"^You say, \'.+\'$", line) is not None:
            return "say_you"
        elif re.fullmatch(r"^You shout, \'.+\'$", line) is not None:
            return "shout_you"
        elif re.fullmatch(r"^You say to your guild, \'.+\'$", line) is not None:
            return "guild_you"
        elif re.fullmatch(r"^You tell your party, \'.+\'$", line) is not None:
            return "group_you"
        elif re.fullmatch(r"^You say out of character, \'.+\'$", line) is not None:
            return "ooc_you"
        elif re.fullmatch(r"^You auction, \'.+\'$", line) is not None:
            return "auction_you"

        return None

    except Exception as e:
        eqa_settings.log(
            "process_log (check_sent_chat): Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def check_command_output(line):
    """
    Check line for command output
    """

    try:
        if (
            re.fullmatch(
                r"^Your Location is [-]?(?:\d*\.)?\d+\,\ [-]?(?:\d*\.)?\d+\,\ [-]?(?:\d*\.)?\d+$",
                line,
            )
            is not None
        ):
            return "location"
        elif (
            re.fullmatch(
                r"^You think you are heading (?:North(?:East|West)?|South(?:East|West)?|(?:Ea|We)st)\.$",
                line,
            )
            is not None
        ):
            return "direction"
        elif (
            re.fullmatch(r"^You have no idea what direction you are facing\.$", line)
            is not None
        ):
            return "direction_miss"
        elif (
            re.fullmatch(r"^You are now A\.F\.K\. \(Away From Keyboard\)\.", line)
            is not None
        ):
            return "you_afk_on"
        elif re.fullmatch(r"^You are now Looking For a Group\.", line) is not None:
            return "you_lfg_on"
        elif (
            re.fullmatch(r"^You are no longer A\.F\.K\. \(Away From Keyboard\)\.", line)
            is not None
        ):
            return "you_afk_off"
        elif (
            re.fullmatch(r"^You are no longer Looking For a Group\.", line) is not None
        ):
            return "you_lfg_off"
        elif (
            re.fullmatch(
                r"^It will take (you |)about (30|25|20|15|10|5) (more |)seconds to prepare your camp\.$",
                line,
            )
            is not None
        ):
            return "you_camping"
        elif (
            re.fullmatch(r"^You abandon your preparations to camp\.$", line) is not None
        ):
            return "you_camping_abandoned"
        elif re.fullmatch(r"^\*\*.+", line) is not None:
            return "random"
        elif re.fullmatch(r"^Game Time\:.+", line) is not None:
            return "time_game"
        elif re.fullmatch(r"^Earth Time\:.+", line) is not None:
            return "time_earth"
        elif re.fullmatch(r"^MESSAGE OF THE DAY\:.+", line) is not None:
            return "motd_game"
        elif re.fullmatch(r"^GUILD MOTD\:.+", line) is not None:
            return "motd_guild"
        elif re.fullmatch(r"^Summoning [a-zA-Z]+\'s corpse\.\.\.", line) is not None:
            return "summon_corpse"
        elif (
            re.fullmatch(r"^You can\'t use that command while casting\.\.\.$", line)
            is not None
        ):
            return "command_block_casting"
        elif (
            re.fullmatch(r"^You can\'t use that command right now\.\.\.$", line)
            is not None
        ):
            return "command_block"
        elif (
            re.fullmatch(r"^That is not a valid command\.  Please use \/help\.$", line)
            is not None
        ):
            return "command_invalid"

        return None

    except Exception as e:
        eqa_settings.log(
            "process_log (check_command_output): Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def check_system_messages(line):
    """
    Check line for system messages
    """

    try:
        if re.fullmatch(r"^You have entered [a-zA-Z\s\'\:]+\.$", line) is not None:
            return "you_new_zone"
        elif re.fullmatch(r"^LOADING, PLEASE WAIT\.\.\.$", line) is not None:
            return "zoning"
        elif re.fullmatch(r"^You are out of food\.$", line) is not None:
            return "you_outfood"
        elif re.fullmatch(r"^You are out of drink\.$", line) is not None:
            return "you_outdrink"
        elif re.fullmatch(r"^You are out of food and drink\.$", line) is not None:
            return "you_outfooddrink"
        elif (
            re.fullmatch(r"^You are out of food and low on drink\.$", line) is not None
        ):
            return "you_outfoodlowdrink"
        elif (
            re.fullmatch(r"^You are out of drink and low on food\.$", line) is not None
        ):
            return "you_outdrinklowfood"
        elif re.fullmatch(r"^You are thirsty\.$", line) is not None:
            return "you_thirsty"
        elif (
            re.fullmatch(
                r"^Glug, glug, glug\.\.\.  [a-zA-Z]+ takes a drink from [a-zA-Z\s]+\.$",
                line,
            )
            is not None
        ):
            return "drink_other"
        elif re.fullmatch(r"^You are hungry\.", line) is not None:
            return "you_hungry"
        elif re.fullmatch(r"^You are no longer encumbered\.$", line) is not None:
            return "encumbered_off"
        elif re.fullmatch(r"^You are encumbered\!$", line) is not None:
            return "encumbered_on"
        elif (
            re.fullmatch(r"^You have become better at [a-zA-Z\s]+\! \(\d+\)$", line)
            is not None
        ):
            return "skill_up"
        elif re.fullmatch(r"^Welcome to level \d+\!", line) is not None:
            return "ding_up"
        elif (
            re.fullmatch(r"^You LOST a level\! You are now level \d+\!", line)
            is not None
        ):
            return "ding_down"
        elif re.fullmatch(r"^It begins to rain\.$", line) is not None:
            return "weather_start_rain"
        elif re.fullmatch(r"^It begins to snow\.$", line) is not None:
            return "weather_start_snow"
        elif re.fullmatch(r"^You can\'t reach that, get closer\.$", line) is not None:
            return "you_cannot_reach"
        elif (
            re.fullmatch(
                r"^Your faction standing with \w+ (?:could not possibly get any|got) (?:better|worse)\.$",
                line,
            )
            is not None
        ):
            return "faction_line"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ engages \w+\!$", line) is not None:
            return "engage"
        elif (
            re.fullmatch(
                r"^(Targeted \((NPC|Player)\)\: [a-zA-Z\s]+|You no longer have a target\.)",
                line,
            )
            is not None
        ):
            return "target"
        elif re.fullmatch(r"^Welcome to EverQuest\!$", line) is not None:
            return "motd_welcome"
        elif (
            re.fullmatch(r"^You are currently bound in\: [a-zA-Z\s\'\-]+$", line)
            is not None
        ):
            return "you_char_bound"
        elif (
            re.fullmatch(
                r"^[a-zA-Z\s]+ is (?:behind and to the (?:righ|lef)t\.|ahead and to the (?:righ|lef)t\.|(?:straight ahead|behind you)\.|to the (?:righ|lef)t\.)$",
                line,
            )
            is not None
        ):
            return "tracking"
        elif re.fullmatch(r"^Track players \* OFF \*$", line) is not None:
            return "tracking_player_off"
        elif re.fullmatch(r"^Track players \* ON \*$", line) is not None:
            return "tracking_player_on"
        elif (
            re.fullmatch(
                r"^The Gods of Norrath emit a sinister laugh as they toy with their creations\. They are reanimating creatures to provide a greater challenge to the mortals$",
                line,
            )
            is not None
        ):
            return "earthquake"
        elif (
            re.fullmatch(r"^You feel the need to get somewhere safe quickly\.$", line)
            is not None
        ):
            return "earthquake"
        elif re.fullmatch(r"^[Zone]", line) is not None:
            return "zone_message"
        elif re.fullmatch(r"^\<\[SERVER MESSAGE\]\>\:.+", line) is not None:
            return "server_message"
        elif re.fullmatch(r"^FORMAT\:.+", line) is not None:
            return "command_error"
        elif re.fullmatch(r"^\w+ is not online at this time\.$", line) is not None:
            return "tell_offline"
        elif re.fullmatch(r"^Consider whom\?$", line) is not None:
            return "consider_no_target"
        elif re.fullmatch(r"^Auto attack off\.$", line) is not None:
            return "you_auto_attack_off"
        elif re.fullmatch(r"^Auto attack on\.$", line) is not None:
            return "you_auto_attack_on"
        elif re.fullmatch(r"^You lack the proper key\.$", line) is not None:
            return "wrong_key"
        elif re.fullmatch(r"^You are stunned\!$", line) is not None:
            return "you_stun_on"
        elif re.fullmatch(r"^You are unstunned\.$", line) is not None:
            return "you_stun_off"
        elif (
            re.fullmatch(
                r"^(Also, auto-follow works best in wide open areas with low lag\.  Twisty areas, lag, and other factors may cause auto-follow to fail\.|\*WARNING\*\: Do NOT use around lava, water, cliffs, or other dangerous areas because you WILL fall into them\. You have been warned\.)$",
                line,
            )
            is not None
        ):
            return "autofollow_advice"

        return None

    except Exception as e:
        eqa_settings.log(
            "process_log (check_system_messages): Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def check_group_system_messages(line):
    """
    Check line for group system messages
    """

    try:
        if re.fullmatch(r"^[a-zA-Z]+ has gone Linkdead.", line) is not None:
            return "player_linkdead"
        elif re.fullmatch(r"^You have joined the group\.", line) is not None:
            return "group_joined"
        elif re.fullmatch(r"^\w+ has joined the group\.$", line) is not None:
            return "group_joined_other"
        elif re.fullmatch(r"^\w+ has left the group\.$", line) is not None:
            return "group_leave_other"
        elif re.fullmatch(r"^You have been removed from the group\.", line) is not None:
            return "group_removed"
        elif (
            re.fullmatch(r"^You invite [a-zA-Z]+ to join your group\.$", line)
            is not None
        ):
            return "group_invite_other"
        elif (
            re.fullmatch(r"^[a-zA-Z]+ invites you to join a group\.$", line) is not None
        ):
            return "group_invite_you"
        elif (
            re.fullmatch(
                r"^To join the group, click on the \'FOLLOW\' option, or \'DISBAND\' to cancel\.$",
                line,
            )
            is not None
        ):
            return "group_invite_instruction"
        elif re.fullmatch(r"^Your group has been disbanded\.$", line) is not None:
            return "group_disbanded"
        elif (
            re.fullmatch(r"^You are now the leader of your group\.$", line) is not None
        ):
            return "group_leader_you"
        elif re.fullmatch(r"^\w+ is now the leader of your group\.$", line) is not None:
            return "group_leader_other"
        elif re.fullmatch(r"^You have formed the group\.$", line) is not None:
            return "group_created"
        elif (
            re.fullmatch(
                r"^You notify [a-zA-Z]+ that you agree to join the group\.$", line
            )
            is not None
        ):
            return "group_join_notify"

        return None

    except Exception as e:
        eqa_settings.log(
            "process_log (check_group_system_messages): Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def check_loot_trade(line):
    """
    Check line for looting or trading
    """

    try:
        if (
            re.fullmatch(r"^\-\-\w+ has looted [a-zA-Z`\s\:\']+\.\-\-$", line)
            is not None
        ):
            return "looted_item_other"
        elif (
            re.fullmatch(r"^\-\-You have looted [a-zA-Z`\s\:\']+\.\-\-$", line)
            is not None
        ):
            return "looted_item_you"
        elif (
            re.fullmatch(
                r"^You receive (\d+ platinum, |)(\d+ gold, |)(\d+ silver and |)\d+ copper from the corpse\.$",
                line,
            )
            is not None
        ):
            return "looted_money_you"
        elif (
            re.fullmatch(
                r"^You receive \d+ platinum, \d+ gold, \d+ silver, \d+ copper as your split\.$",
                line,
            )
            is not None
        ):
            return "looted_money_other"
        elif (
            re.fullmatch(r"^The total trade is\: \d+ PP, \d+ GP, \d+ SP, \d+ CP$", line)
            is not None
        ):
            return "trade_money"
        elif (
            re.fullmatch(r"^[a-zA-Z]+ has offered you [a-zA-Z`\s\:\']+\.$", line)
            is not None
        ):
            return "trade_item"
        elif (
            re.fullmatch(
                r"^You give \d+ (platinum|gold|silver|copper) to [a-zA-Z`\s]+\.$", line
            )
            is not None
        ):
            return "trade_npc_payment"

        return None

    except Exception as e:
        eqa_settings.log(
            "process_log (check_loot_trade): Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def check_spell_specific(line):
    """
    Check line for spell specific output
    """
    try:
        if re.fullmatch(r"^\w+ begins to regenerate\.$", line) is not None:
            return "spell_regen_on_other"
        elif re.fullmatch(r"^You begin to regenerate\.$", line) is not None:
            return "spell_regen_on_you"
        elif (
            re.fullmatch(r"^You feel the spirit of wolf enter you\.$", line) is not None
        ):
            return "spell_sow_on_you"
        elif re.fullmatch(r"^Your feet slow down\.$", line) is not None:
            return "spell_sow_off_you"
        elif re.fullmatch(r"^You(?:r body fades away| vanish)\.$", line) is not None:
            return "spell_invis_on_you"
        elif re.fullmatch(r"^You (?:return to view|appear)\.$", line) is not None:
            return "spell_invis_off_you"
        elif (
            re.fullmatch(r"^You feel yourself starting to appear\.$", line) is not None
        ):
            return "spell_invis_dropping_you"
        elif re.fullmatch(r"^Your feet leave the ground\.$", line) is not None:
            return "spell_levitate_on_you"
        elif (
            re.fullmatch(r"^You feel as if you are about to fall\.$", line) is not None
        ):
            return "spell_levitate_dropping_you"
        elif re.fullmatch(r"^You can no longer levitate\.$", line) is not None:
            return "spell_levitate_off_you"
        elif (
            re.fullmatch(r"^You have healed .+ for \d+ points of damage\.$", line)
            is not None
        ):
            return "spell_heal_you"
        elif re.fullmatch(r"^Your target has been cured\.$", line) is not None:
            return "spell_cured_other"
        elif re.fullmatch(r"^You have been summoned\!$", line) is not None:
            return "spell_summoned_you"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ yawns\.$", line) is not None:
            return "spell_slow_on"
        elif re.fullmatch(r"^You feel yourself bind to the area\.$", line) is not None:
            return "spell_bind_you"
        elif (
            re.fullmatch(r"^Your gate is too unstable, and collapses\.$", line)
            is not None
        ):
            return "spell_gate_collapse"

        return None

    except Exception as e:
        eqa_settings.log(
            "process_log (check_spell_specific): Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def check_emotes(line):
    """
    Check line for emotes
    """

    try:
        if (
            re.fullmatch(
                r"^(You agree with everyone around you\.|You agree with [a-zA-Z`\s]+\.)$",
                line,
            )
            is not None
        ):
            return "emote_agree_you"
        elif (
            re.fullmatch(
                r"^(You are amazed\!|You gasp at [a-zA-Z`\s]+ in amazement\.)$", line
            )
            is not None
        ):
            return "emote_amaze_you"
        elif (
            re.fullmatch(
                r"^(You apologize to everyone\.|You apologize to [a-zA-Z`\s]+ whole\-heartedly\.)$",
                line,
            )
            is not None
        ):
            return "emote_apologize_you"
        elif (
            re.fullmatch(
                r"^(You give a round of applause\.|You applaud [a-zA-Z`\s\']+ performance\.)$",
                line,
            )
            is not None
        ):
            return "emote_applaud_you"
        elif (
            re.fullmatch(
                r"^(You make a rude gesture\.|You make a rude gesture at [a-zA-Z`\s]+\.)$",
                line,
            )
            is not None
        ):
            return "emote_bird_you"
        elif (
            re.fullmatch(
                r"^(You look around for someone to bite\!|You bite [a-zA-Z`\s]+ on the leg\!)$",
                line,
            )
            is not None
        ):
            return "emote_bite_you"
        elif (
            re.fullmatch(
                r"^(You bleed quietly\.|You bleed all over [a-zA-Z`\s]+\.)$", line
            )
            is not None
        ):
            return "emote_bleed_you"
        elif (
            re.fullmatch(
                r"^(You blink in disbelief\.|You blink at [a-zA-Z`\s]+ in disbelief\.)$",
                line,
            )
            is not None
        ):
            return "emote_blink_you"
        elif (
            re.fullmatch(r"^(You blush profusely\.|You blush at [a-zA-Z`\s]+\.)$", line)
            is not None
        ):
            return "emote_blush_you"
        elif (
            re.fullmatch(
                r"^(You boggle\, shaking your head and looking confused\.|You boggle at [a-zA-Z`\s]+\, shaking your head and looking confused\.)$",
                line,
            )
            is not None
        ):
            return "emote_boggle_you"
        elif (
            re.fullmatch(
                r"^(You look around for someone to bonk\!|You bonk [a-zA-Z`\s]+ on the head\!)$",
                line,
            )
            is not None
        ):
            return "emote_bonk_you"
        elif re.fullmatch(r"^\w+ bonks \w+ on the head\!$", line) is not None:
            return "emote_bonk_other"
        elif (
            re.fullmatch(
                r"^(You inform everyone that you are bored\.|You inform [a-zA-Z`\s]+ that you are bored\.)$",
                line,
            )
            is not None
        ):
            return "emote_bored_you"
        elif (
            re.fullmatch(
                r"^(You bounce with excitement\.|You bounce around [a-zA-Z`\s]+\.)$",
                line,
            )
            is not None
        ):
            return "emote_bounce_you"
        elif (
            re.fullmatch(r"^(You bow\.|You bow before [a-zA-Z`\s]+\.)$", line)
            is not None
        ):
            return "emote_bow_you"
        elif re.fullmatch(r"^(\w+ bows before \w+\.|\w+ bows\.)$", line) is not None:
            return "emote_bow_other"
        elif (
            re.fullmatch(
                r"^(You announce that you will be right back\.|You let [a-zA-Z`\s]+ know that you will be right back\.)$",
                line,
            )
            is not None
        ):
            return "emote_brb_you"
        elif (
            re.fullmatch(
                r"^(You burp loudly\.|You burp loudly at [a-zA-Z`\s]+\.)$", line
            )
            is not None
        ):
            return "emote_burp_you"
        elif (
            re.fullmatch(
                r"^(You wave goodbye to everyone\.|You wave goodbye to [a-zA-Z`\s]+\.)$",
                line,
            )
            is not None
        ):
            return "emote_bye_you"
        elif (
            re.fullmatch(
                r"^(You cackle gleefully\.|You cackle gleefully at [a-zA-Z`\s]+\.)$",
                line,
            )
            is not None
        ):
            return "emote_cackle_you"
        elif (
            re.fullmatch(
                r"^(You look peaceful and calm\.|You try to calm down [a-zA-Z`\s]+\.)$",
                line,
            )
            is not None
        ):
            return "emote_calm_you"
        elif (
            re.fullmatch(r"^(You cheer\.|You cheer at [a-zA-Z`\s]+\.)$", line)
            is not None
        ):
            return "emote_cheer_you"
        elif (
            re.fullmatch(r"^(\w+ cheers\.|\w+ cheers at [a-zA-Z`\s]+\.)$", line)
            is not None
        ):
            return "emote_cheer_other"
        elif (
            re.fullmatch(r"^(You chuckle\.|You chuckle at [a-zA-Z`\s]+\.)$", line)
            is not None
        ):
            return "emote_chuckle_you"
        elif (
            re.fullmatch(
                r"^(You clap your hands together \- hurray\!|You clap happily for [a-zA-Z`\s]+ \- hurray\!)$",
                line,
            )
            is not None
        ):
            return "emote_clap_you"
        elif (
            re.fullmatch(
                r"^(You need to be comforted\.|You comfort [a-zA-Z`\s]+\.)$", line
            )
            is not None
        ):
            return "emote_comfort_you"
        elif (
            re.fullmatch(
                r"^(You congratulate those around you on a job well done\.|You congratulate [a-zA-Z`\s]+ on a job well done\.)$",
                line,
            )
            is not None
        ):
            return "emote_congratulate_you"
        elif (
            re.fullmatch(r"^(You cough\.|You cough at [a-zA-Z`\s]+\.)$", line)
            is not None
        ):
            return "emote_cough_you"
        elif (
            re.fullmatch(r"^(You cringe\.|You cringe away from [a-zA-Z`\s]+\.)$", line)
            is not None
        ):
            return "emote_cringe_you"
        elif (
            re.fullmatch(r"^(You cry\.|You cry over [a-zA-Z`\s]+\.)$", line) is not None
        ):
            return "emote_cry_you"
        elif (
            re.fullmatch(
                r"^(You look around you curiously\.|You look at [a-zA-Z`\s]+ curiously\.)$",
                line,
            )
            is not None
        ):
            return "emote_curious_you"
        elif (
            re.fullmatch(
                r"^(You stand on your tip\-toes and do a dance of joy\!|You grab hold of [a-zA-Z`\s]+ and begin to dance with them\.)$",
                line,
            )
            is not None
        ):
            return "emote_dance_you"
        elif (
            re.fullmatch(
                r"^\w+ grabs hold of \w+ and begins to dance with (?:h(?:er|im)|it)\.$",
                line,
            )
            is not None
        ):
            return "emote_dance_other"
        elif (
            re.fullmatch(
                r"^(You drool \-\- something must have you excited\!|You drool all over [a-zA-Z`\s]+\.)$",
                line,
            )
            is not None
        ):
            return "emote_drool_you"
        elif (
            re.fullmatch(r"^(You duck\.|You duck behind [a-zA-Z`\s]+\.)$", line)
            is not None
        ):
            return "emote_duck_you"
        elif (
            re.fullmatch(
                r"^(You raise an eyebrow inquiringly\.|You raise an eyebrow at [a-zA-Z`\s]+\.)$",
                line,
            )
            is not None
        ):
            return "emote_eye_you"
        elif re.fullmatch(r"^(You fidget\.)$", line) is not None:
            return "emote_fidget_you"
        elif (
            re.fullmatch(
                r"^(You flex your muscles proudly\.|You flex at [a-zA-Z`\s]+\.)$", line
            )
            is not None
        ):
            return "emote_flex_you"
        elif (
            re.fullmatch(r"^(You frown\.|You frown at [a-zA-Z`\s]+\.)$", line)
            is not None
        ):
            return "emote_frown_you"
        elif (
            re.fullmatch(
                r"^(You gasp in astonishment\.|You gasp at [a-zA-Z`\s]+ in astonishment\.)$",
                line,
            )
            is not None
        ):
            return "emote_gasp_you"
        elif (
            re.fullmatch(r"^(You giggle\.|You giggle at [a-zA-Z`\s]+\.)$", line)
            is not None
        ):
            return "emote_giggle_you"
        elif (
            re.fullmatch(
                r"^(You glare at nothing in particular\.|You turn an icy glare upon [a-zA-Z`\s]+\.)$",
                line,
            )
            is not None
        ):
            return "emote_glare_you"
        elif (
            re.fullmatch(
                r"^(You grin evilly\.|You grin evilly at [a-zA-Z`\s]+\.)$", line
            )
            is not None
        ):
            return "emote_grin_you"
        elif (
            re.fullmatch(
                r"^(You groan\.|You groan at the sight of [a-zA-Z`\s]+\.)$", line
            )
            is not None
        ):
            return "emote_groan_you"
        elif (
            re.fullmatch(
                r"^(You grovel pitifully\.|You grovel before [a-zA-Z`\s]+\.)$", line
            )
            is not None
        ):
            return "emote_grovel_you"
        elif (
            re.fullmatch(
                r"^(You are so happy\!|You are very happy with [a-zA-Z`\s]+\.)$", line
            )
            is not None
        ):
            return "emote_happy_you"
        elif (
            re.fullmatch(
                r"^(You need food\, badly\.|You let [a-zA-Z`\s]+ know that you need food\, badly\.)$",
                line,
            )
            is not None
        ):
            return "emote_hungry_you"
        elif (
            re.fullmatch(r"^(You hug yourself\.|You hug [a-zA-Z`\s]+\.)$", line)
            is not None
        ):
            return "emote_hug_you"
        elif (
            re.fullmatch(
                r"^(You introduce yourself\. Hi there\!|You introduce [a-zA-Z`\s]+\.)$",
                line,
            )
            is not None
        ):
            return "emote_introduce_you"
        elif (
            re.fullmatch(
                r"^(You were JUST KIDDING\!|You let [a-zA-Z`\s]+ know that you were JUST KIDDING\!)$",
                line,
            )
            is not None
        ):
            return "emote_jk_you"
        elif (
            re.fullmatch(
                r"^(You blow a kiss into the air\.|You kiss [a-zA-Z`\s]+ on the cheek\.)$",
                line,
            )
            is not None
        ):
            return "emote_kiss_you"
        elif (
            re.fullmatch(
                r"^(You kneel down\.|You kneel before [a-zA-Z`\s]+ in humility and reverence\.)$",
                line,
            )
            is not None
        ):
            return "emote_kneel_you"
        elif (
            re.fullmatch(r"^(You laugh\.|You laugh at [a-zA-Z`\s]+\.)$", line)
            is not None
        ):
            return "emote_laugh_you"
        elif (
            re.fullmatch(
                r"^(You look completely lost\!|You inform [a-zA-Z`\s]+ that you are completely lost\!)$",
                line,
            )
            is not None
        ):
            return "emote_lost_you"
        elif (
            re.fullmatch(
                r"^(You look around for someone to massage\.|You massage [a-zA-Z`\s\']+ shoulders\.)$",
                line,
            )
            is not None
        ):
            return "emote_massage_you"
        elif (
            re.fullmatch(r"^(You moan\.|You moan at [a-zA-Z`\s]+\.)$", line) is not None
        ):
            return "emote_moan_you"
        elif (
            re.fullmatch(
                r"^(You lower your head and mourn the loss of the dead\.|You lower your head and mourn the loss of [a-zA-Z`\s]+\.)$",
                line,
            )
            is not None
        ):
            return "emote_mourn_you"
        elif re.fullmatch(r"^(You nod\.|You nod at [a-zA-Z`\s]+\.)$", line) is not None:
            return "emote_nod_you"
        elif re.fullmatch(r"^(You nudge|You nudge [a-zA-Z`\s]+\.)$", line) is not None:
            return "emote_nudge_you"
        elif (
            re.fullmatch(
                r"^(You panic and scream\.|You panic at the sight of [a-zA-Z`\s]+\.)$",
                line,
            )
            is not None
        ):
            return "emote_panic_you"
        elif (
            re.fullmatch(
                r"^(You pat yourself on the back\.|You pat [a-zA-Z`\s]+ on the back\.)$",
                line,
            )
            is not None
        ):
            return "emote_pat_you"
        elif (
            re.fullmatch(
                r"^(You peer around intently\.|You peer at [a-zA-Z`\s]+\, looking them up and down\.)$",
                line,
            )
            is not None
        ):
            return "emote_peer_you"
        elif (
            re.fullmatch(
                r"^(You plead with everyone around you\.|You plead with [a-zA-Z`\s]+ desperately\.)$",
                line,
            )
            is not None
        ):
            return "emote_plead_you"
        elif (
            re.fullmatch(
                r"^(You point straight ahead\.|You point at [a-zA-Z`\s]+\. Yeah you\!)$",
                line,
            )
            is not None
        ):
            return "emote_point_you"
        elif (
            re.fullmatch(r"^(You poke yourself\.|You poke [a-zA-Z`\s]+\.)$", line)
            is not None
        ):
            return "emote_poke_you"
        elif (
            re.fullmatch(
                r"^(You ponder the matters at hand\.|You ponder [a-zA-Z`\s]+\. What is going on with them\?)$",
                line,
            )
            is not None
        ):
            return "emote_ponder_you"
        elif (
            re.fullmatch(r"^(You purr\.|You purr at [a-zA-Z`\s]+\.)$", line) is not None
        ):
            return "emote_purr_you"
        elif (
            re.fullmatch(
                r"^(You look completely puzzled\.|You look at [a-zA-Z`\s]+\, completely puzzled\.)$",
                line,
            )
            is not None
        ):
            return "emote_puzzle_you"
        elif (
            re.fullmatch(
                r"^(You raise your hand\.|You look at [a-zA-Z`\s]+ and raise your hand\.)$",
                line,
            )
            is not None
        ):
            return "emote_raise_you"
        elif (
            re.fullmatch(
                r"^(You let everyone know that you are ready\!|You ask [a-zA-Z`\s]+ if they are ready\.)$",
                line,
            )
            is not None
        ):
            return "emote_ready_you"
        elif (
            re.fullmatch(
                r"^(You emit a low rumble and then roar like a lion\!|You emit a low rumble and then roar at [a-zA-Z`\s]+\.)$",
                line,
            )
            is not None
        ):
            return "emote_roar_you"
        elif (
            re.fullmatch(
                r"^(You roll on the floor laughing\.|You roll on the floor laughing at [a-zA-Z`\s]+\.)$",
                line,
            )
            is not None
        ):
            return "emote_rofl_you"
        elif (
            re.fullmatch(
                r"^(You salute the gods in pure admiration\.|You snap to attention and salute [a-zA-Z`\s]+ crisply\.)$",
                line,
            )
            is not None
        ):
            return "emote_salute_you"
        elif (
            re.fullmatch(
                r"^(You shiver\. Brrrrrr\.|You shiver at the thought of messing with [a-zA-Z`\s]+\.)$",
                line,
            )
            is not None
        ):
            return "emote_shiver_you"
        elif (
            re.fullmatch(
                r"^(You shrug unknowingly\.|You shrug at [a-zA-Z`\s]+\.)$", line
            )
            is not None
        ):
            return "emote_shrug_you"
        elif (
            re.fullmatch(
                r"^(You sigh\, clearly disappointed\.|You sigh at [a-zA-Z`\s]+\.)$",
                line,
            )
            is not None
        ):
            return "emote_sigh_you"
        elif (
            re.fullmatch(
                r"^(You smack yourself on the forehead\.|You smack [a-zA-Z`\s]+\.)$",
                line,
            )
            is not None
        ):
            return "emote_smack_you"
        elif (
            re.fullmatch(r"^(You smile\.|You beam a smile at [a-zA-Z`\s]+\.)$", line)
            is not None
        ):
            return "emote_smile_you"
        elif re.fullmatch(r"^\w+ beams a smile at [a-zA-Z`\s]+\.$", line) is not None:
            return "emote_smile_other"
        elif (
            re.fullmatch(
                r"^(You smirk mischievously\.|You smirk mischievously at [a-zA-Z`\s]+\.)$",
                line,
            )
            is not None
        ):
            return "emote_smirk_you"
        elif (
            re.fullmatch(
                r"^(You bare your teeth in a terrible snarl\.|You snarl meanly at [a-zA-Z`\s]+\.)$",
                line,
            )
            is not None
        ):
            return "emote_snarl_you"
        elif (
            re.fullmatch(
                r"^(You snicker softly\.|You snicker softly at [a-zA-Z`\s]+\.)$", line
            )
            is not None
        ):
            return "emote_snicker_you"
        elif (
            re.fullmatch(
                r"^(You stare at the ground\.|You stare at [a-zA-Z`\s]+\, completely lost in their eyes\.)$",
                line,
            )
            is not None
        ):
            return "emote_stare_you"
        elif (
            re.fullmatch(
                r"^(You tap your foot impatiently\.|You tap your foot as you look at [a-zA-Z`\s]+ impatiently\.)$",
                line,
            )
            is not None
        ):
            return "emote_tap_you"
        elif (
            re.fullmatch(
                r"^(You look about for someone to tease\.|You tease [a-zA-Z`\s]+ mercilessly\.)$",
                line,
            )
            is not None
        ):
            return "emote_tease_you"
        elif (
            re.fullmatch(
                r"^(You thank everyone\.|You thank [a-zA-Z`\s]+ heartily\.)$", line
            )
            is not None
        ):
            return "emote_thank_you"
        elif re.fullmatch(r"^\w+ thanks [a-zA-Z`\s]+ heartily\.$", line) is not None:
            return "emote_thank_other"
        elif (
            re.fullmatch(
                r"^(You need drink\, badly\!|You let [a-zA-Z`\s]+ know that you need drink\, badly\.)$",
                line,
            )
            is not None
        ):
            return "emote_thirsty_you"
        elif (
            re.fullmatch(
                r"^(You veto the idea\.|You veto [a-zA-Z`\s\']+ idea\!)$", line
            )
            is not None
        ):
            return "emote_veto_you"
        elif (
            re.fullmatch(r"^(You wave\.|You wave at [a-zA-Z`\s]+\.)$", line) is not None
        ):
            return "emote_wave_you"
        elif re.fullmatch(r"^\w+ waves at [a-zA-Z`\s]+\.$", line) is not None:
            return "emote_wave_other"
        elif (
            re.fullmatch(
                r"^(You whine pitifully\.|You whine pitifully at [a-zA-Z`\s]+\.)$", line
            )
            is not None
        ):
            return "emote_whine_you"
        elif (
            re.fullmatch(
                r"^(You whistle a little tune\.|You whistle at [a-zA-Z`\s]+ appreciatively\.)$",
                line,
            )
            is not None
        ):
            return "emote_whistle_you"
        elif (
            re.fullmatch(
                r"^(You open your mouth wide and yawn\.|You yawn rudely in [a-zA-Z`\s\']+ face\.)$",
                line,
            )
            is not None
        ):
            return "emote_yawn_you"

        return None

    except Exception as e:
        eqa_settings.log(
            "process_log (check_emotes): Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def check_who(line):
    """
    Check line for who output
    """

    try:
        if re.fullmatch(r"^Players (on|in) EverQuest\:$", line) is not None:
            return "who_top"
        elif re.fullmatch(r"^Friends currently on EverQuest\:$", line) is not None:
            return "who_top_friends"
        elif re.fullmatch(r"^Players Looking For Groups\:$", line) is not None:
            return "who_top_lfg"
        elif re.fullmatch(r"^---------------------------$", line) is not None:
            return "who_line"
        elif re.fullmatch(r"^---------------------------------$", line) is not None:
            return "who_line_friends"
        elif (
            re.fullmatch(
                r"^( AFK |\<LINKDEAD\>| AFK  <LINKDEAD>|)\[(\d+ [a-zA-Z\s]+|ANONYMOUS)\] \w+( \([a-zA-Z\s]+\)|)( \<[a-zA-Z\s]+\>|  \<[a-zA-Z\s]+\>|)( ZONE\: \w+|  ZONE\: \w+|)( LFG|  LFG|)$",
                line,
            )
            is not None
        ):
            return "who_player"
        elif (
            re.fullmatch(
                r"^There (is|are) \d+ (player|players) in [a-zA-Z\s\-\']+\.$", line
            )
            is not None
        ):
            return "who_total"
        elif (
            re.fullmatch(
                r"^There are no players in EverQuest that match those who filters\.$",
                line,
            )
            is not None
        ):
            return "who_total_empty"
        elif (
            re.fullmatch(
                r"^There are no players in [a-zA-Z\s\-\']+ that match those who filters\.$",
                line,
            )
            is not None
        ):
            return "who_total_local_empty"

        return None

    except Exception as e:
        eqa_settings.log(
            "process_log (check_who): Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def check_pets(line):
    """
    Check line for pet responses
    """

    try:
        if (
            re.fullmatch(
                r"^[a-zA-Z\s]+ (says|tells you)(,|) \'Following you, Master\.\'$", line
            )
            is not None
        ):
            return "pet_follow"
        elif (
            re.fullmatch(
                r"^[a-zA-Z\s]+ (says|tells you)(,|) \'Attacking [a-zA-Z\s`]+ Master\.\'$",
                line,
            )
            is not None
        ):
            return "pet_attack"
        elif (
            re.fullmatch(
                r"^[a-zA-Z\s]+ (says|tells you)(,|) \'No longer taunting attackers, Master\.\'$",
                line,
            )
            is not None
        ):
            return "pet_taunt_off"
        elif (
            re.fullmatch(
                r"^[a-zA-Z\s]+ (says|tells you)(,|) \'At your service Master\.\'$", line
            )
            is not None
        ):
            return "pet_spawn"
        elif (
            re.fullmatch(
                r"^[a-zA-Z\s]+ (says|tells you)(,|) \'Changing position, Master\.\'$",
                line,
            )
            is not None
        ):
            return "pet_sit_stand"
        elif (
            re.fullmatch(
                r"^[a-zA-Z\s]+ (says|tells you)(,|) \'Guarding with my life\.\.oh splendid one\.\'$",
                line,
            )
            is not None
        ):
            return "pet_guard"
        elif (
            re.fullmatch(
                r"^[a-zA-Z\s]+ (says|tells you)(,|) \'Sorry, Master\.\.calming down\.\'$",
                line,
            )
            is not None
        ):
            return "pet_back"
        elif (
            re.fullmatch(
                r"^[a-zA-Z\s]+ (says|tells you)(,|) \'That is not a legal target master\.\'$",
                line,
            )
            is not None
        ):
            return "pet_illegal_target"
        elif (
            re.fullmatch(
                r"^[a-zA-Z\s]+ (says|tells you)(,|) \'Sorry to have failed you, oh Great One\.\'$",
                line,
            )
            is not None
        ):
            return "pet_dead"

        return None

    except Exception as e:
        eqa_settings.log(
            "process_log (check_pets): Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


if __name__ == "__main__":
    main()
