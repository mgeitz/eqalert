#! /usr/bin/env python

"""
   Program:   EQ Alert
   File Name: eqa/lib/parser.py
   Copyright (C) 2024 M Geitz

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

import sys
import time
import re
import datetime

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
            if log_q.qsize() < 1:
                time.sleep(0.01)

            # Check queue for message
            if not log_q.empty():
                ## Read new message
                line = log_q.get().strip()
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
                    timestamp = (
                        timestamp.split(" ")[3]
                        + "."
                        + datetime.datetime.now().strftime("%f")[:1]
                        + "0"
                    )
                    ### Build and queue action
                    action_q.put(
                        eqa_struct.message(
                            timestamp, determine(payload), None, None, payload
                        )
                    )
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

        # Who
        line_type = check_who(line)
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

        # Ability Output
        line_type = check_ability_output(line)
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

        # Spell Specific
        line_type = check_spell_specific(line)
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
                r"^[a-zA-Z`\s]+ (stings|mauls|hits|crushes|slashes|pierces|bashes|backstabs|bites|kicks|claws|gores|punches|strikes|slices) (you|YOU) for \d+ point(s|) of damage\.$",
                line,
            )
            is not None
        ):
            return "combat_you_receive_melee"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s\-]+ (stings|mauls|hits|crushes|slashes|pierces|bashes|backstabs|bites|kicks|claws|gores|punches|strikes|slices) [a-zA-Z`\s\-]+ for \d+ point(s|) of damage\.$",
                line,
            )
            is not None
        ):
            return "combat_other_melee"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s\-]+ tries to (sting|maul|hit|crush|slash|pierce|bash|backstab|bite|kick|claw|gore|punch|strike|slice) [a-zA-Z`\s\-]+, but misses\!$",
                line,
            )
            is not None
        ):
            return "combat_other_melee_miss"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s\-]+ tries to (sting|maul|hit|crush|slash|pierce|bash|backstab|bite|kick|claw|gore|punch|strike|slice) [a-zA-Z`\s\-]+, but [a-zA-Z`\s\-]+ dodges\!$",
                line,
            )
            is not None
        ):
            return "combat_other_melee_dodge"
        elif (
            re.fullmatch(
                r"^You try to (sting|maul|hit|crush|slash|pierce|bash|backstab|bite|kick|claw|gore|punch|strike|slice) [a-zA-Z`\s\-]+, but [a-zA-Z`\s\-]+ dodges\!$",
                line,
            )
            is not None
        ):
            return "combat_you_melee_dodge"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s\-]+ tries to (sting|maul|hit|crush|slash|pierce|bash|backstab|bite|kick|claw|gore|punch|strike|slice) YOU, but YOU dodge\!$",
                line,
            )
            is not None
        ):
            return "combat_you_melee_dodge"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s\-]+ tries to (sting|maul|hit|crush|slash|pierce|bash|backstab|bite|kick|claw|gore|punch|strike|slice) [a-zA-Z`\s\-]+, but [a-zA-Z`\s\-]+ is INVULNERABLE\!$",
                line,
            )
            is not None
        ):
            return "combat_other_melee_invulnerable"
        elif (
            re.fullmatch(
                r"^You try to (sting|maul|hit|crush|slash|pierce|bash|backstab|bite|kick|claw|gore|punch|strike|slice) [a-zA-Z`\s\-]+, but [a-zA-Z`\s\-]+ is INVULNERABLE\!$",
                line,
            )
            is not None
        ):
            return "combat_you_melee_invulnerable"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s\-]+ tries to (sting|maul|hit|crush|slash|pierce|bash|backstab|bite|kick|claw|gore|punch|strike|slice) YOU, but ([a-zA-Z`\s\-]+|) are INVULNERABLE\!$",
                line,
            )
            is not None
        ):
            return "combat_your_melee_invulnerable"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s\-]+ tries to (sting|maul|hit|crush|slash|pierce|bash|backstab|bite|kick|claw|gore|punch|strike|slice) [a-zA-Z`\s\-]+, but [a-zA-Z`\s\-]+ parries\!$",
                line,
            )
            is not None
        ):
            return "combat_other_melee_parry"
        elif (
            re.fullmatch(
                r"^You try to (sting|maul|hit|crush|slash|pierce|bash|backstab|bite|kick|claw|gore|punch|strike|slice) [a-zA-Z`\s\-]+, but [a-zA-Z`\s\-]+ parries\!$",
                line,
            )
            is not None
        ):
            return "combat_you_melee_parry"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s\-]+ tries to (sting|maul|hit|crush|slash|pierce|bash|backstab|bite|kick|claw|gore|punch|strike|slice) [a-zA-Z`\s\-]+, but [a-zA-Z`\s\-]+ blocks\!$",
                line,
            )
            is not None
        ):
            return "combat_other_melee_block"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s\-]+ tries to (sting|maul|hit|crush|slash|pierce|bash|backstab|bite|kick|claw|gore|punch|strike|slice) [a-zA-Z`\s\-]+, but [a-zA-Z`\s\-]+ ripostes\!$",
                line,
            )
            is not None
        ):
            return "combat_other_melee_riposte"
        elif (
            re.fullmatch(
                r"^You try to (sting|maul|hit|crush|slash|pierce|bash|backstab|bite|kick|claw|gore|punch|strike|slice) [a-zA-Z`\s\-]+, but [a-zA-Z`\s\-]+ ripostes\!$",
                line,
            )
            is not None
        ):
            return "combat_you_melee_riposte"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s\-]+ tries to (sting|maul|hit|crush|slash|pierce|bash|backstab|bite|kick|claw|gore|punch|strike|slice) [a-zA-Z`\s\-]+, but [a-zA-Z`\s\-]+'s magical skin absorbs the blow\!$",
                line,
            )
            is not None
        ):
            return "combat_other_rune_damage"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s\-]+ tries to (sting|maul|hit|crush|slash|pierce|bash|backstab|bite|kick|claw|gore|punch|strike|slice) YOU, but YOUR magical skin absorbs the blow\!$",
                line,
            )
            is not None
        ):
            return "combat_your_rune_damage"
        elif (
            re.fullmatch(
                r"^You try to (sting|maul|hit|crush|slash|pierce|bash|backstab|bite|kick|claw|gore|punch|strike|slice) [a-zA-Z`\s\-]+, but [a-zA-Z`\s\-]+'s magical skin absorbs the blow\!$",
                line,
            )
            is not None
        ):
            return "combat_you_rune_damage"
        elif (
            re.fullmatch(
                r"^You (sting|maul|hit|crush|slash|pierce|bash|backstab|bite|kick|claw|gore|punch|strike|slice) [a-zA-Z`\s\-]+ for \d+ point(s|) of damage\.$",
                line,
            )
            is not None
        ):
            return "combat_you_melee"
        elif (
            re.fullmatch(
                r"^You try to (sting|maul|hit|crush|slash|pierce|bash|backstab|bite|kick|claw|gore|punch|strike|slice) [a-zA-Z`\s\-]+, but miss\!$",
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
            re.fullmatch(r"^[a-zA-Z`\s\-]+ has become (ENRAGED|enraged)\.$", line)
            is not None
        ):
            return "mob_enrage_on"
        elif re.fullmatch(r"^[a-zA-Z`\s\-]+ is no longer enraged\.$", line) is not None:
            return "mob_enrage_off"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s\-]+ goes on a (RAMPAGE|rampage)\!$", line)
            is not None
        ):
            return "mob_rampage_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s\-]+ has been slain by [a-zA-Z`\s\-]+\!$", line)
            is not None
        ):
            return "mob_slain_other"
        elif re.fullmatch(r"^You have slain [a-zA-Z`\s\-]+\!$", line) is not None:
            return "mob_slain_you"
        elif (
            re.fullmatch(r"^You have been slain by [a-zA-Z`\s\-]+\!$", line) is not None
        ):
            return "you_slain"
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
        elif re.fullmatch(r"^You have been knocked unconscious\!$", line) is not None:
            return "unconscious"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s\-]+ was pierced by thorns\.$", line) is not None
        ):
            return "combat_other_ds_thorns_damage"
        elif re.fullmatch(r"^YOU are pierced by thorns\!$", line) is not None:
            return "combat_you_ds_thorns_damage"
        elif re.fullmatch(r"^[a-zA-Z`\s\-]+ was burned\.$", line) is not None:
            return "combat_other_ds_fire_damage"
        elif re.fullmatch(r"^YOU are burned\!$", line) is not None:
            return "combat_you_ds_fire_damage"
        elif (
            re.fullmatch(
                r"^You must first click on the being you wish to attack\!$", line
            )
            is not None
        ):
            return "combat_you_no_target"
        elif (
            re.fullmatch(r"^You can\'t see your target from here\.$", line) is not None
        ):
            return "combat_you_cannot_see"
        elif re.fullmatch(r"^You can\'t hit them from here\.$", line) is not None:
            return "combat_you_cannot_hit"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s\-]+ executes a FLURRY of attacks on [a-zA-Z`0-9\'\s\-]+\!$",
                line,
            )
            is not None
        ):
            return "combat_other_flurry"
        elif (
            re.fullmatch(
                r"^A (shimmer|glimmering) drake (kicks|tries to kick).*\.$",
                line,
            )
            is not None
        ):
            return "combat_ranger_drake"

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
            return "spells_cast_other"
        elif re.fullmatch(r"^You begin casting [a-zA-Z\:`\s\']+\.$", line) is not None:
            return "spells_cast_you"
        elif (
            re.fullmatch(r"^Your [0-9a-zA-Z\s`\:\'\-]+ begins to glow\.$", line)
            is not None
        ):
            return "spells_cast_item_you"
        elif re.fullmatch(r"^\w+\'s spell fizzles\!$", line) is not None:
            return "spells_fizzle_other"
        elif re.fullmatch(r"^Your spell fizzles\!$", line) is not None:
            return "spells_fizzle_you"
        elif re.fullmatch(r"^Your spell did not take hold\.$", line) is not None:
            return "spells_not_hold"
        elif (
            re.fullmatch(r"^Insufficient Mana to cast this spell\!$", line) is not None
        ):
            return "spells_cast_oom"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s casting is interrupted\!$", line)
            is not None
        ):
            return "spells_interrupt_other"
        elif re.fullmatch(r"^Your spell is interrupted\.$", line) is not None:
            return "spells_interrupt_you"
        elif re.fullmatch(r"^[a-zA-Z]+\'s song ends abruptly\.$", line) is not None:
            return "spells_song_end"
        elif (
            re.fullmatch(r"^You are too distracted to cast a spell now\!$", line)
            is not None
        ):
            return "spells_distracted"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ regains concentration and continues casting\.$", line
            )
            is not None
        ):
            return "spells_recover_other"
        elif (
            re.fullmatch(
                r"^You regain your concentration and continue your casting\.$", line
            )
            is not None
        ):
            return "spells_recover_you"
        elif re.fullmatch(r"^Your target resisted the .+ spell\.$", line) is not None:
            return "spells_resist_other"
        elif re.fullmatch(r"^You resist the .+ spell\!$", line) is not None:
            return "spells_resist_you"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ was hit by non\-melee for \d+ point(s|) of damage\.$",
                line,
            )
            is not None
        ):
            return "spells_damage_other"
        elif (
            re.fullmatch(r"^You were hit by non\-melee for \d+ damage\.$", line)
            is not None
        ):
            return "spells_damage_you"
        elif re.fullmatch(r"^Aborting memorization of spell\.$", line) is not None:
            return "spells_memorize_abort"
        elif (
            re.fullmatch(r"^Beginning to memorize [a-zA-Z`\s\'\:]+\.\.\.$", line)
            is not None
        ):
            return "spells_memorize_begin"
        elif (
            re.fullmatch(
                r"^You are not high enough level to memorize that spell\.$", line
            )
            is not None
        ):
            return "spells_memorize_too_high"
        elif (
            re.fullmatch(
                r"^You will have to achieve level \d+ before you can scribe the [a-zA-Z`\s\'\:]+\.$",
                line,
            )
            is not None
        ):
            return "spells_scribe_not_yet"
        elif (
            re.fullmatch(r"^Beginning to scribe [a-zA-Z`\s\'\:]+\.\.\.$", line)
            is not None
        ):
            return "spells_scribe_begin"
        elif (
            re.fullmatch(
                r"^You have finished scribing [a-zA-Z`\s\'\:]+(\.\.\.|\.)$", line
            )
            is not None
        ):
            return "spells_scribe_finish"
        elif (
            re.fullmatch(
                r"^Right click on another Scribe Slot in your Spell Book to swap this Spell position with the new one\.$",
                line,
            )
            is not None
        ):
            return "spells_scribe_swap_instruction"
        elif re.fullmatch(r"^Swapping Spell Book Scribe slots\.$", line) is not None:
            return "spells_scribe_swap"
        elif (
            re.fullmatch(r"^You have finished memorizing [a-zA-Z`\s\'\:]+\.$", line)
            is not None
        ):
            return "spells_memorize_finish"
        elif (
            re.fullmatch(
                r"^You cannot memorize a spell you already have memorized\.$", line
            )
            is not None
        ):
            return "spells_memorize_already"
        elif re.fullmatch(r"^You forget .+\.", line) is not None:
            return "spells_forget"
        elif (
            re.fullmatch(r"^Your [a-zA-Z`\'\s]+ spell has worn off\.$", line)
            is not None
        ):
            return "spells_worn_off"
        elif (
            re.fullmatch(
                r"^You try to cast a spell on [a-zA-Z`\s]+, but they are protected\.$",
                line,
            )
            is not None
        ):
            return "spells_protected_other"
        elif re.fullmatch(r"^You haven't recovered yet\.\.\.$", line) is not None:
            return "spells_cooldown_active"
        elif (
            re.fullmatch(r"^You must be standing to cast a spell\.$", line) is not None
        ):
            return "spells_sitting"
        elif (
            re.fullmatch(r"^You must first select a target for this spell\!$", line)
            is not None
        ):
            return "spells_no_target"
        elif (
            re.fullmatch(r"^A missed note brings \w+'s song to a close\!$", line)
            is not None
        ):
            return "songs_interrupted_other"
        elif (
            re.fullmatch(r"^You feel as if you are about to fall\.$", line) is not None
        ):
            return "spells_levitate_dropping_you"
        elif re.fullmatch(r"^You can\'t levitate in this zone\.$", line) is not None:
            return "spells_levitate_block"
        elif (
            re.fullmatch(
                r"^You feel as if you are about to look like yourself again\.$", line
            )
            is not None
        ):
            return "spells_illusion_dropping_you"
        elif re.fullmatch(r"^Your target has been cured\.$", line) is not None:
            return "spells_cured_other"
        elif re.fullmatch(r"^You feel yourself bind to the area\.$", line) is not None:
            return "spells_bind_you"
        elif (
            re.fullmatch(r"^Your gate is too unstable, and collapses\.$", line)
            is not None
        ):
            return "spells_gate_collapse"
        elif (
            re.fullmatch(r"^[\w\s\'`]+ begins to cast the gate spell\.$", line)
            is not None
        ):
            return "spells_gate_npc_casting"
        elif re.fullmatch(r"^[a-zA-Z`\s\'\-]+ Gates\.$", line) is not None:
            return "spells_gated_npc"
        elif (
            re.fullmatch(r"^You feel yourself starting to appear\.$", line) is not None
        ):
            return "spells_invis_dropping_you"
        elif (
            re.fullmatch(
                r"^\w+ tries to cast an invisibility spell on you, but you are already invisible\.$",
                line,
            )
            is not None
        ):
            return "spells_invis_already"
        elif re.fullmatch(r"^You have been summoned\!$", line) is not None:
            return "spells_summoned_you"
        elif (
            re.fullmatch(r"^You have healed .+ for \d+ point(s|) of damage\.$", line)
            is not None
        ):
            return "spells_heal_you"
        elif (
            re.fullmatch(r"^\w+ has healed you for \d+ point(s|) of damage\.$", line)
            is not None
        ):
            return "spells_heal_other"
        elif (
            re.fullmatch(
                r"^Your spell is too powerful for your intended target\.$", line
            )
            is not None
        ):
            return "spells_too_powerful"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ tries to cast a spell on you, but you are protected\.$",
                line,
            )
            is not None
        ):
            return "spells_protected_you"
        elif re.fullmatch(r"^You can't cast spells while stunned\!$", line) is not None:
            return "spells_stun_cast_block"

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
        if (
            re.fullmatch(r"^[a-zA-Z\s`]+ tells you, \'Welcome to my bank\!\'$", line)
            is not None
        ):
            return "tell_npc_bank_open"
        elif (
            re.fullmatch(r"^[a-zA-Z\s`]+ tells you, \'Come back soon\!\'$", line)
            is not None
        ):
            return "tell_npc_bank_closed"
        elif (
            re.fullmatch(
                r"^[a-zA-Z\s`]+ tells you, \'(That\'ll be|I\'ll give you) .+ (for the|per) .+\'$",
                line,
            )
            is not None
        ):
            return "trade_npc_item_price"
        elif (
            re.fullmatch(r"^[a-zA-Z\.]+ tells you(, in \w+|), \'(.+|)\'$", line)
            is not None
        ):
            return "tell"
        elif (
            re.fullmatch(
                r"^[a-zA-Z\.]+ tells you,in an unknown tongue, \'(.+|)\'$", line
            )
            is not None
        ):
            return "tell_unknown_tongue"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ tells you(,|) \'.+\'$", line) is not None:
            return "tell_npc"
        elif re.fullmatch(r"^\w+ says(, in \w+|), \'(.+|)\'$", line) is not None:
            return "say"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ says(,|) \'.+\'$", line) is not None:
            return "say_npc"
        elif (
            re.fullmatch(r"^\w+ says,in an unknown tongue, \'(.+|)\'$", line)
            is not None
        ):
            return "say_unknown_tongue"
        elif re.fullmatch(r"^\w+ shouts(, in \w+|), \'(.+|)\'$", line) is not None:
            return "shout"
        elif (
            re.fullmatch(r"^\w+ shouts,in an unknown tongue, \'(.+|)\'$", line)
            is not None
        ):
            return "shout_unknown_tongue"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+( |  )shouts(,|) \'.+(\'|)$", line) is not None
        ):
            return "shout_npc"
        elif (
            re.fullmatch(r"^\w+ tells the guild(, in \w+|), \'(.+|)\'$", line)
            is not None
        ):
            return "guild"
        elif (
            re.fullmatch(r"^\w+ tells the group(, in \w+|), \'(.+|)\'$", line)
            is not None
        ):
            return "group"
        elif (
            re.fullmatch(r"^\w+ says out of character(, in \w+|), \'(.+|)\'$", line)
            is not None
        ):
            return "ooc"
        elif (
            re.fullmatch(
                r"^\w+ auctions(, in \w+|), \'(.+|)(wts|WTS|selling|Selling)(.+|)\'$",
                line,
            )
            is not None
        ):
            return "auction_wts"
        elif (
            re.fullmatch(
                r"^\w+ auctions(, in \w+|), \'(.+|)(wtb|WTB|buying|Buying)(.+|)\'$",
                line,
            )
            is not None
        ):
            return "auction_wtb"
        elif re.fullmatch(r"^\w+ auctions(, in \w+|), \'(.+|)\'$", line) is not None:
            return "auction"
        elif (
            re.fullmatch(r"^\w+ auctions,in an unknown tongue, \'(.+|)\'$", line)
            is not None
        ):
            return "auction_unknown_tongue"
        elif re.fullmatch(r"^[a-zA-Z]+ BROADCASTS, \'(.+|)\'$", line) is not None:
            return "broadcast"

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
        if (
            re.fullmatch(r"^You told [a-zA-Z\.]+(, \'| \'\[queued\],)(.+|)\'$", line)
            is not None
        ):
            return "tell_you"
        elif re.fullmatch(r"^You say, \'(.+|)\'$", line) is not None:
            return "say_you"
        elif re.fullmatch(r"^You shout, \'(.+|)\'$", line) is not None:
            return "shout_you"
        elif re.fullmatch(r"^You say to your guild, \'(.+|)\'$", line) is not None:
            return "guild_you"
        elif re.fullmatch(r"^You tell your party, \'(.+|)\'$", line) is not None:
            return "group_you"
        elif re.fullmatch(r"^You say out of character, \'(.+|)\'$", line) is not None:
            return "ooc_you"
        elif re.fullmatch(r"^You auction, \'(.+|)\'$", line) is not None:
            return "auction_you"
        elif re.fullmatch(r"^You petition, \'(.+|)\'$", line) is not None:
            return "petition_you"

        return None

    except Exception as e:
        eqa_settings.log(
            "process_log (check_sent_chat): Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def check_ability_output(line):
    """
    Check line for ability output
    """

    try:
        if (
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
        elif re.fullmatch(r"^Forage Error\: Cursor not empty\.$", line) is not None:
            return "forage_cursor_empty"
        elif re.fullmatch(r"^You must be standing to forage\.$", line) is not None:
            return "forage_standing"
        elif (
            re.fullmatch(
                r"^You have scrounged up something that doesn't look edible\.$", line
            )
            is not None
        ):
            return "forage_not_edible"
        elif re.fullmatch(r"^You have scrounged up some .+\.$", line) is not None:
            return "forage_edible"
        elif (
            re.fullmatch(r"^You can\'t try to forage while attacking\.$", line)
            is not None
        ):
            return "forage_attacking"
        elif re.fullmatch(r"^You fail to locate any food nearby\.$", line) is not None:
            return "forage_fail"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\-\s]+ is (?:behind and to the (?:righ|lef)t\.|ahead and to the (?:righ|lef)t\.|(?:straight ahead|behind you)\.|to the (?:righ|lef)t\.)$",
                line,
            )
            is not None
        ):
            return "tracking"
        elif re.fullmatch(r"^Track players \* OFF \*$", line) is not None:
            return "tracking_player_off"
        elif re.fullmatch(r"^Track players \* ON \*$", line) is not None:
            return "tracking_player_on"
        elif re.fullmatch(r"^You have lost your tracking target\.$", line) is not None:
            return "tracking_target_lost"
        elif re.fullmatch(r"^You begin tracking [a-zA-Z\s`]+\.$", line) is not None:
            return "tracking_begin"
        elif re.fullmatch(r"^\w+ has fallen to the ground\.", line) is not None:
            return "feign_failure_other"
        elif (
            re.fullmatch(
                r"^You (?:have moved and are no longer hidden\!\!|are no longer hidden\.)$",
                line,
            )
            is not None
        ):
            return "hide_drop"
        elif re.fullmatch(r"^You begin to hide\.\.\.$", line) is not None:
            return "hide_enabled"
        elif re.fullmatch(r"^You stop hiding\.$", line) is not None:
            return "hide_disabled"
        elif (
            re.fullmatch(r"^You must stand perfectly still to hide\!$", line)
            is not None
        ):
            return "hide_moving"
        elif (
            re.fullmatch(r"^You can't try to hide while attacking.$", line) is not None
        ):
            return "hide_attacking"
        elif (
            re.fullmatch(r"^You are being bandaged\. Stay relatively still\.$", line)
            is not None
        ):
            return "bandage_you_other"
        elif re.fullmatch(r"^You begin to bandage yourself\.$", line) is not None:
            return "bandage_you_you"
        elif re.fullmatch(r"^You must be standing to bind wounds\.$", line) is not None:
            return "bandage_block_stand"
        elif (
            re.fullmatch(
                r"^You cannot have your wounds bound above \d+\% hitpoints\.$", line
            )
            is not None
        ):
            return "bandage_cap_other"
        elif (
            re.fullmatch(r"^You cannot bind wounds above \d+\% hitpoints\.$", line)
            is not None
        ):
            return "bandage_cap_you"
        elif (
            re.fullmatch(r"^You can't fish while holding something\.$", line)
            is not None
        ):
            return "fishing_holding"
        elif (
            re.fullmatch(r"^You can't fish without a fishing pole, go buy one\.$", line)
            is not None
        ):
            return "fishing_no_pole"
        elif re.fullmatch(r"^You cast your line\.$", line) is not None:
            return "fishing_cast"
        elif re.fullmatch(r"^You caught, something\.\.\.$", line) is not None:
            return "fishing_caught_something"
        elif re.fullmatch(r"^You didn't catch anything\.$", line) is not None:
            return "fishing_caught_nothing"
        elif re.fullmatch(r"^You lost your bait\!$", line) is not None:
            return "fishing_lost_bait"
        elif re.fullmatch(r"^Trying to catch land sharks perhaps\?$", line) is not None:
            return "fishing_no_water"
        elif (
            re.fullmatch(
                r"^You need to put your fishing pole in your primary hand\.$", line
            )
            is not None
        ):
            return "fishing_creatively"
        elif re.fullmatch(r"^Your fishing pole broke\!$", line) is not None:
            return "fishing_pole_broke"
        elif (
            re.fullmatch(r"^You spill your beer while bringing in your line\.$", line)
            is not None
        ):
            return "fishing_spill_beer"
        elif (
            re.fullmatch(
                r"^You must have a lock pick in your inventory to do this\.$", line
            )
            is not None
        ):
            return "required_pick"
        elif re.fullmatch(r"^Ability not ready\.$", line) is not None:
            return "ability_not_ready"
        elif (
            re.fullmatch(
                r"^You taunt [a-zA-Z`\s\-]+ to ignore others and attack you\!$", line
            )
            is not None
        ):
            return "taunt_you"
        elif (
            re.fullmatch(r"^You must target an NPC to taunt first\.$", line) is not None
        ):
            return "taunt_missing_target"

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
        elif (
            re.fullmatch(r"^You must be sitting to prepare to camp\.$", line)
            is not None
        ):
            return "you_camping_standing"
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
        elif re.fullmatch(r"^Summoning [a-zA-Z]+\'s corpse\.\.\.$", line) is not None:
            return "summon_corpse"
        elif (
            re.fullmatch(r"^You don\'t have any corpses in this zone\.$", line)
            is not None
        ):
            return "summon_corpse_none"
        elif (
            re.fullmatch(r"^You do not have consent to summon that corpse\.$", line)
            is not None
        ):
            return "summon_corpse_no_consent"
        elif (
            re.fullmatch(r"^The corpse is too far away to summon\.$", line) is not None
        ):
            return "summon_corpse_too_far"
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
            re.fullmatch(
                r"^You must be completely stopped before doing this action\.$", line
            )
            is not None
        ):
            return "command_block_moving"
        elif (
            re.fullmatch(r"^You can't attack with your spell book open\.$", line)
            is not None
        ):
            return "command_block_spellbook"
        elif (
            re.fullmatch(r"^That is not a valid command\.  Please use \/help\.$", line)
            is not None
        ):
            return "command_invalid"
        elif (
            re.fullmatch(
                r"^You have no friends, but you can add some with\: \/friends \<name\>$",
                line,
            )
            is not None
        ):
            return "friend_empty"
        elif (
            re.fullmatch(
                r"^\w+ is no longer your friend\.$",
                line,
            )
            is not None
        ):
            return "friend_remove"
        elif (
            re.fullmatch(
                r"^\w+ is now your friend\.$",
                line,
            )
            is not None
        ):
            return "friend_add"
        elif (
            re.fullmatch(
                r"^You have added \w+ to your IGNORE list\.$",
                line,
            )
            is not None
        ):
            return "ignore_add"
        elif (
            re.fullmatch(
                r"^If you need help, click on the EQ Menu button at the bottom of your screen and select the \"Help\" option\.$",
                line,
            )
            is not None
        ):
            return "titanium_client_help_message"
        elif (
            re.fullmatch(r"^Reading UI data from [a-zA-Z\\]+ directory.\.\.$", line)
            is not None
        ):
            return "client_ui_load"
        elif re.fullmatch(r"^Making all existing corpses visible\.$", line) is not None:
            return "hide_corpse_none"
        elif (
            re.fullmatch(r"^Hiding all existing corpses except yours\.$", line)
            is not None
        ):
            return "hide_corpse_all"
        elif (
            re.fullmatch(
                r"^Now any corpse you loot, except your own, will be hidden when you finish looting but leave items on the corpse\.$",
                line,
            )
            is not None
        ):
            return "hide_corpse_looted"
        elif re.fullmatch(r"^You have been added to the list\.$", line) is not None:
            return "list_added"
        elif (
            re.fullmatch(
                r"^You have moved out of the range of the Item List\. If you do not return within \d+ seconds, you will be removed from the list\.$",
                line,
            )
            is not None
        ):
            return "list_leaving"
        elif (
            re.fullmatch(
                r"^You have left your item list zone\. If you do not return to the camp within \d+ seconds, you will be removed from the list\.$",
                line,
            )
            is not None
        ):
            return "list_leaving_zone"
        elif (
            re.fullmatch(
                r"^You have re\-entered the range for your Item List\. Please remain in the area to refresh your range timer\.$",
                line,
            )
            is not None
        ):
            return "list_re_entered"
        elif (
            re.fullmatch(r"^There are no lists in this zone to join\.$", line)
            is not None
        ):
            return "list_none"
        elif (
            re.fullmatch(r"^You are already on a list\. You are position \d+\.$", line)
            is not None
        ):
            return "list_position"
        elif (
            re.fullmatch(r"^You are not in range of a list to join\.$", line)
            is not None
        ):
            return "list_out_of_range"
        elif (
            re.fullmatch(
                r"^You have been removed from the Item List because you did not stay in range\.$",
                line,
            )
            is not None
        ):
            return "list_removed_range"
        elif (
            re.fullmatch(
                r"^You are currently able to inspect other players by right\-clicking on them\.$",
                line,
            )
            is not None
        ):
            return "inspect_toggle_on"
        elif (
            re.fullmatch(
                r"^You are currently NOT able to inspect other players by right\-clicking on them\.$",
                line,
            )
            is not None
        ):
            return "inspect_toggle_off"
        elif (
            re.fullmatch(
                r"^\w+\'s birthdate\: .+\.$",
                line,
            )
            is not None
        ):
            return "birthdate"
        elif (
            re.fullmatch(
                r"^This session\: .+$",
                line,
            )
            is not None
        ):
            return "played_session"
        elif (
            re.fullmatch(
                r"^Total time playing \w+\: .+$",
                line,
            )
            is not None
        ):
            return "played_total"
        elif (
            re.fullmatch(
                r"^Your total time entitled on this account is 0\.0 years\.$",
                line,
            )
            is not None
        ):
            return "account_subscription"
        elif (
            re.fullmatch(
                r"^To remove consent, use \/deny \<playername\>$",
                line,
            )
            is not None
        ):
            return "corpse_consent"
        elif (
            re.fullmatch(
                r"^You have not received any tells, so you cannot reply\.$",
                line,
            )
            is not None
        ):
            return "reply_empty"
        elif re.fullmatch(r"^  \/[a-zA-Z0-9]+", line) is not None:
            return "help_command_output"
        elif (
            re.fullmatch(
                r"^--------------------------------------------------------------------------------$",
                line,
            )
            is not None
        ):
            return "help_command_line"
        elif re.fullmatch(r"^List of commands$", line) is not None:
            return "help_command_header"
        elif (
            re.fullmatch(
                r"^Format\: \/help \<class\> Where class is one of normal, emote, or guild$",
                line,
            )
            is not None
        ):
            return "help_command_format"
        elif (
            re.fullmatch(r"^Normal will display a list of all commands\.$", line)
            is not None
        ):
            return "help_command_normal"
        elif (
            re.fullmatch(r"^Emote will display a list of all player emotes\.$", line)
            is not None
        ):
            return "help_command_emote"
        elif (
            re.fullmatch(r"^Guild will display a list of guild commands\.$", line)
            is not None
        ):
            return "help_command_guild"
        elif (
            re.fullmatch(
                r"^Voice will display a list of voice control commands\.$", line
            )
            is not None
        ):
            return "help_command_voice"
        elif (
            re.fullmatch(r"^Chat will display a list of chat channel commands\.$", line)
            is not None
        ):
            return "help_command_chat"
        elif re.fullmatch(r"^List of Friends$", line) is not None:
            return "friend_list_header"
        elif re.fullmatch(r"^-----------------$", line) is not None:
            return "friend_list_line"
        elif re.fullmatch(r"^You have \d+ friend\(s\)\.$", line) is not None:
            return "friend_list_total"
        elif re.fullmatch(r"^Format\: \/target \<name\>$", line) is not None:
            return "target_command_format"
        elif (
            re.fullmatch(r"^NAMES OF THOSE CURRENTLY BEING IGNORED\:$", line)
            is not None
        ):
            return "ignore_list_header"
        elif re.fullmatch(r"^FORMAT\:.+", line) is not None:
            return "command_error"
        elif re.fullmatch(r"^Usage\: .+", line) is not None:
            return "command_usage"
        elif (
            re.fullmatch(
                r"^You must wait a bit longer before using the rewind command again\.$",
                line,
            )
            is not None
        ):
            return "rewind_output_wait"
        elif (
            re.fullmatch(
                r"^Rewinding to previous location\.$",
                line,
            )
            is not None
        ):
            return "rewind_output"

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
        if re.fullmatch(r"^You have entered [a-zA-Z\s\'\:\-]+\.$", line) is not None:
            return "you_new_zone"
        elif re.fullmatch(r"^LOADING, PLEASE WAIT\.\.\.$", line) is not None:
            return "zoning"
        elif re.fullmatch(r"^You are out of food\.$", line) is not None:
            return "you_outfood"
        elif re.fullmatch(r"^Ahhh\. That was refreshing\.$", line) is not None:
            return "drink_you_finish"
        elif re.fullmatch(r"^Ahhh\. That was tasty\.$", line) is not None:
            return "eat_you_finish"
        elif (
            re.fullmatch(
                r"^You could not possibly eat any more, you would explode\!$", line
            )
            is not None
        ):
            return "eat_you_full"
        elif re.fullmatch(r"^You are out of drink\.$", line) is not None:
            return "you_outdrink"
        elif re.fullmatch(r"^You are out of food and drink\.$", line) is not None:
            return "you_outfooddrink"
        elif (
            re.fullmatch(r"^You are out of food and low on drink\.$", line) is not None
        ):
            return "you_outfoodlowdrink"
        elif re.fullmatch(r"^You are low on drink\.$", line) is not None:
            return "you_lowdrink"
        elif re.fullmatch(r"^You are low on food\.$", line) is not None:
            return "you_lowfood"
        elif re.fullmatch(r"^You are low on food and drink\.$", line) is not None:
            return "you_lowfoodlowdrink"
        elif (
            re.fullmatch(r"^You are out of drink and low on food\.$", line) is not None
        ):
            return "you_outdrinklowfood"
        elif re.fullmatch(r"^You are thirsty\.$", line) is not None:
            return "you_thirsty"
        elif (
            re.fullmatch(
                r"^Glug, glug, glug\.\.\.  [a-zA-Z]+ takes a drink from [a-zA-Z\.\s\:\']+\.$",
                line,
            )
            is not None
        ):
            return "drink_other"
        elif (
            re.fullmatch(
                r"^You take a drink from [a-zA-Z\s\:\']+\.$",
                line,
            )
            is not None
        ):
            return "drink_you"
        elif (
            re.fullmatch(
                r"^Chomp, chomp, chomp\.\.\.  [a-zA-Z]+ takes a bite from [a-zA-Z\s\:\']+\.$",
                line,
            )
            is not None
        ):
            return "eat_other"
        elif (
            re.fullmatch(r"^You take a bite out of [a-zA-Z\s\:\']+\.$", line)
            is not None
        ):
            return "eat_you"
        elif re.fullmatch(r"^You are hungry\.$", line) is not None:
            return "you_hungry"
        elif re.fullmatch(r"^You are no longer encumbered\.$", line) is not None:
            return "encumbered_off"
        elif re.fullmatch(r"^You are encumbered\!$", line) is not None:
            return "encumbered_on"
        elif (
            re.fullmatch(
                r"^You have become better at [0-9a-zA-Z\'\s]+\! \(\d+\)$", line
            )
            is not None
        ):
            return "skill_up"
        elif (
            re.fullmatch(r"^Error\: Skill at cap value\, training failed\.$", line)
            is not None
        ):
            return "skill_max"
        elif (
            re.fullmatch(r"^You must learn advanced trade skills in the field\.$", line)
            is not None
        ):
            return "skill_max_tradeskill"
        elif (
            re.fullmatch(r"^(You have gained a level\! |)Welcome to level \d+\!$", line)
            is not None
        ):
            return "ding_up"
        elif (
            re.fullmatch(r"^You LOST a level\! You are now level \d+\!$", line)
            is not None
        ):
            return "ding_down"
        elif re.fullmatch(r"^You are conscious again\!$", line) is not None:
            return "concious_you"
        elif re.fullmatch(r"^You died\.$", line) is not None:
            return "dead_you"
        elif re.fullmatch(r"^\w+ died\.$", line) is not None:
            return "dead_other"
        elif re.fullmatch(r"^It begins to rain\.$", line) is not None:
            return "weather_start_rain"
        elif re.fullmatch(r"^It begins to snow\.$", line) is not None:
            return "weather_start_snow"
        elif re.fullmatch(r"^You can\'t reach that, get closer\.$", line) is not None:
            return "you_cannot_reach"
        elif (
            re.fullmatch(
                r"^Your faction standing with [A-Za-z0-9`\'\-]+ (?:could not possibly get any|got) (?:better|worse)\.$",
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
        elif re.fullmatch(r"^\[Zone\] .+", line) is not None:
            return "zone_message"
        elif re.fullmatch(r"^\<\[SERVER MESSAGE\]\>\:.+", line) is not None:
            return "server_message"
        elif re.fullmatch(r"^\w+ is not online at this time\.$", line) is not None:
            return "tell_offline"
        elif (
            re.fullmatch(
                r"^Your queued tell to \w+ failed to be delivered \(Player now offline\)\.$",
                line,
            )
            is not None
        ):
            return "tell_queued_offline"
        elif re.fullmatch(r"^Consider whom\?$", line) is not None:
            return "consider_no_target"
        elif (
            re.fullmatch(r"^It is futile to consider the dead\.\.\.$", line) is not None
        ):
            return "consider_dead"
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
        elif re.fullmatch(r"^You will now auto\-follow \w+\.$", line) is not None:
            return "autofollow_on"
        elif (
            re.fullmatch(r"^You are no longer auto\-following \w+\.$", line) is not None
        ):
            return "autofollow_off"
        elif (
            re.fullmatch(
                r"^You must first target a group member to auto\-follow\.$", line
            )
            is not None
        ):
            return "autofollow_no_target"
        elif (
            re.fullmatch(
                r"^(Also, auto-follow works best in wide open areas with low lag\.  Twisty areas, lag, and other factors may cause auto-follow to fail\.|\*WARNING\*\: Do NOT use around lava, water, cliffs, or other dangerous areas because you WILL fall into them\. You have been warned\.)$",
                line,
            )
            is not None
        ):
            return "autofollow_advice"
        elif re.fullmatch(r"^[a-zA-Z\s`]+ was injured by falling\.$", line) is not None:
            return "fall_damage_other"
        elif re.fullmatch(r"^YOU were injured by falling\.$", line) is not None:
            return "fall_damage_you"
        elif (
            re.fullmatch(r"^[a-zA-Z\s`]+ goes into a berserker frenzy\!$", line)
            is not None
        ):
            return "warrior_berserk_on"
        elif re.fullmatch(r"^[a-zA-Z\s`]+ is no longer berserk\.$", line) is not None:
            return "warrior_berserk_off"
        elif (
            re.fullmatch(r"^Returning to home point, please wait\.\.\.$", line)
            is not None
        ):
            return "walk_of_shame"
        elif (
            re.fullmatch(
                r"^You have been given permission to drag [a-zA-Z]+\'s corpse in all zones\.$",
                line,
            )
            is not None
        ):
            return "drag_permission_received"
        elif (
            re.fullmatch(r"^Your target is too far away, get closer\!$", line)
            is not None
        ):
            return "target_attack_too_far"
        elif re.fullmatch(r"^You must be standing to attack\!$", line) is not None:
            return "target_attack_sitting"
        elif (
            re.fullmatch(r"^\w+ is looking at your equipment\.\.\.$", line) is not None
        ):
            return "inspect_you"
        elif re.fullmatch(r"^You are inspecting [A-Za-z]+\.$", line) is not None:
            return "inspect_other"
        elif re.fullmatch(r"^You have lost your target\.$", line) is not None:
            return "target_lost"
        elif (
            re.fullmatch(
                r"^Inventory full, and item is NO TRADE, so cannot auto-inventory the item\.$",
                line,
            )
            is not None
        ):
            return "auto_inventory_full"
        elif (
            re.fullmatch(r"^I don\'t see anyone by that name around here\.\.\.$", line)
            is not None
        ):
            return "target_cannot_see"
        elif (
            re.fullmatch(
                r"^[a-zA-Z]+ yells for help from (?:ahead and to the (?:righ|lef)t of you|behind you(?: and to the (?:righ|lef)t)?|off to the left of you|off to the right of you|straight ahead of you)$",
                line,
            )
            is not None
        ):
            return "yell_help"
        elif (
            re.fullmatch(
                r"^You yell for help\.$",
                line,
            )
            is not None
        ):
            return "yell_help_you"
        elif (
            re.fullmatch(
                r"^[a-zA-Z\s`]+ (?:scowls at you, ready to attack|(?:looks (?:your way apprehensive|upon you warm)|regards you (?:indifferent|as an al)|judges you amiab)ly|gl(?:ares at you threatening|owers at you dubious)ly|kindly considers you) \-\- .+",
                line,
            )
            is not None
        ):
            return "consider"
        elif (
            re.fullmatch(
                r"^There was no place to put that\!  The item has dropped to the ground\!$",
                line,
            )
            is not None
        ):
            return "item_dropped_no_room"
        elif (
            re.fullmatch(
                r"^You just dropped your .+\.",
                line,
            )
            is not None
        ):
            return "item_dropped"
        elif (
            re.fullmatch(r"^That item cannot be dropped, traded, or sold\.$", line)
            is not None
        ):
            return "item_no_drop"
        elif re.fullmatch(r"^Talking to yourself again\?$", line) is not None:
            return "tell_yourself"
        elif (
            re.fullmatch(r"^This corpse is too old to be resurrected\.$", line)
            is not None
        ):
            return "corpse_too_old"
        elif (
            re.fullmatch(
                r"^This corpse\'s resurrection time will expire in .+\.$", line
            )
            is not None
        ):
            return "corpse_res_timer"
        elif re.fullmatch(r"^This corpse will decay in .+\.$", line) is not None:
            return "corpse_decay_timer"
        elif re.fullmatch(r"^You are too fatigued to jump\!$", line) is not None:
            return "jump_fatigue"
        elif (
            re.fullmatch(r"^All Discipline Timers have been Reset\.$", line) is not None
        ):
            return "gm_reset_discipline"
        elif re.fullmatch(r"^All Ability Timers have been Reset\.$", line) is not None:
            return "gm_reset_ability"
        elif (
            re.fullmatch(
                r"^\[Achievement\] Congratulations to .+ for becoming the first .+\!$",
                line,
            )
            is not None
        ):
            return "achievement_first"
        elif (
            re.fullmatch(
                r"^Try attacking someone other than yourself, it\'s more productive\.$",
                line,
            )
            is not None
        ):
            return "attack_self"
        elif (
            re.fullmatch(
                r"^You cannot assist yourself\!$",
                line,
            )
            is not None
        ):
            return "assist_self"
        elif (
            re.fullmatch(
                r"^You must target the person you wish to assist, or type their name after the command\.$",
                line,
            )
            is not None
        ):
            return "assist_no_target"
        elif (
            re.fullmatch(
                r"^You have the helm, captain\.$",
                line,
            )
            is not None
        ):
            return "boat_operator"
        elif (
            re.fullmatch(
                r"^Please wait until we reconnect you with the Universal Chat service\.  Your request has not been sent\.$",
                line,
            )
            is not None
        ):
            return "chat_disconnected"
        elif (
            re.fullmatch(
                r"^You are not a member of the \w+ class guild\.  Begone\.$",
                line,
            )
            is not None
        ):
            return "npc_guild_wrong"
        elif (
            re.fullmatch(
                r"^Spell can only be cast during the night\.$",
                line,
            )
            is not None
        ):
            return "cast_night_only"
        elif (
            re.fullmatch(
                r"^This spell only works on animals\.$",
                line,
            )
            is not None
        ):
            return "cast_animal_only"
        elif (
            re.fullmatch(
                r"^You can only cast this spell in the outdoors\.$",
                line,
            )
            is not None
        ):
            return "cast_outdoors_only"
        elif (
            re.fullmatch(
                r"^You are unable to change form here\.$",
                line,
            )
            is not None
        ):
            return "cast_change_form_block"
        elif (
            re.fullmatch(
                r"^You cannot use this item unless it is equipped\.$",
                line,
            )
            is not None
        ):
            return "item_must_equip"
        elif (
            re.fullmatch(
                r"^That item is too big to fit in that container\.$",
                line,
            )
            is not None
        ):
            return "item_too_big"
        elif (
            re.fullmatch(
                r"^You cannot place containers in containers\.$",
                line,
            )
            is not None
        ):
            return "container_container"
        elif (
            re.fullmatch(
                r"^You are no longer roleplaying\.$",
                line,
            )
            is not None
        ):
            return "roleplay_off"
        elif (
            re.fullmatch(
                r"^You are now roleplaying\.$",
                line,
            )
            is not None
        ):
            return "roleplay_on"
        elif (
            re.fullmatch(
                r"^You are no longer anonymous\.$",
                line,
            )
            is not None
        ):
            return "anon_on"
        elif (
            re.fullmatch(
                r"^You are now anonymous\.$",
                line,
            )
            is not None
        ):
            return "anon_off"
        elif (
            re.fullmatch(
                r"^Your class, deity, race and\/or level may not equip that item\.$",
                line,
            )
            is not None
        ):
            return "equip_block"
        elif (
            re.fullmatch(
                r"^Your race, class, or deity cannot use this item\.$",
                line,
            )
            is not None
        ):
            return "use_block"
        elif re.fullmatch(r"^You cannot remove this effect\.$", line) is not None:
            return "effect_removal_block"
        elif (
            re.fullmatch(r"^You must first target a group member\.$", line) is not None
        ):
            return "target_group_member"
        elif (
            re.fullmatch(
                r"^You cannot pick up a lore item you already possess\.$", line
            )
            is not None
        ):
            return "lore_pickup"
        elif (
            re.fullmatch(r"^You cannot have more than one pet at a time\.$", line)
            is not None
        ):
            return "too_many_pets"
        elif (
            re.fullmatch(
                r"^You have accepted [a-zA-Z]+\'s challenge to duel to the death\!$",
                line,
            )
            is not None
        ):
            return "duel_accept_you"
        elif (
            re.fullmatch(
                r"^[a-zA-Z]+ has defeated [a-zA-Z]+ in a duel to the death\! [a-zA-Z]+ has fled like a cowardly dog\!$",
                line,
            )
            is not None
        ):
            return "duel_end_fled"
        elif (
            re.fullmatch(r"^[a-zA-Z]+ has challenged you to duel to the death\!$", line)
            is not None
        ):
            return "duel_challenge"
        elif (
            re.fullmatch(
                r"^You have challenged [a-zA-Z]+ to duel to the death\!$", line
            )
            is not None
        ):
            return "duel_challenge_you"
        elif (
            re.fullmatch(
                r"^[a-zA-Z]+ has accepted your challenge to duel to the death\!  Fight\!$",
                line,
            )
            is not None
        ):
            return "duel_challenge_you_accepted"
        elif re.fullmatch(r"^You can't attack while stunned\!$", line) is not None:
            return "attack_stun_block"
        elif (
            re.fullmatch(r"^You are not sufficient level to use this item\.$", line)
            is not None
        ):
            return "item_click_too_low"
        elif (
            re.fullmatch(
                r"^You must stand up and be still to perform this action\.$", line
            )
            is not None
        ):
            return "action_not_standing_still"
        elif re.fullmatch(r"^YOU were sliced by a pendulum\.$", line) is not None:
            return "pendulum_knife"

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
        elif re.fullmatch(r"^You cannot invite yourself\.$", line) is not None:
            return "group_invite_yourself"
        elif (
            re.fullmatch(r"^You can only group with player characters\.$", line)
            is not None
        ):
            return "group_invite_npc"
        elif (
            re.fullmatch(
                r"^To join the group, click on the \'FOLLOW\' option, or \'DISBAND\' to cancel\.$",
                line,
            )
            is not None
        ):
            return "group_invite_instruction"
        elif (
            re.fullmatch(
                r"^You cancel the invitation to join [a-zA-Z]+\'s group\.$", line
            )
            is not None
        ):
            return "group_invite_you_cancel"
        elif (
            re.fullmatch(
                r"^You cannot invite someone to join your group, only your leader may do so\.$",
                line,
            )
            is not None
        ):
            return "group_invite_not_lead"
        elif (
            re.fullmatch(r"^That person is already in your party\.$", line) is not None
        ):
            return "group_invite_already"
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
        elif re.fullmatch(r"^You remove \w+ from the party\.$", line) is not None:
            return "group_removed_other"
        elif (
            re.fullmatch(
                r"^\w+ is currently considering joining another group\.$", line
            )
            is not None
        ):
            return "group_considering"
        elif (
            re.fullmatch(
                r"^You are not in a group\. Talking to yourself again\?\?\?$", line
            )
            is not None
        ):
            return "group_alone"
        elif (
            re.fullmatch(
                r"^You notify [a-zA-Z]+ that you agree to join the group\.$", line
            )
            is not None
        ):
            return "group_join_notify"
        elif (
            re.fullmatch(r"^\w+ rejects your offer to join the group\.$", line)
            is not None
        ):
            return "group_join_reject"
        elif re.fullmatch(r"^\w+ is already in another group\.$", line) is not None:
            return "group_already"
        elif (
            re.fullmatch(
                r"^You must target a player or use \/invite \<name\> to invite someone to your group\.$",
                line,
            )
            is not None
        ):
            return "invite_no_target"
        elif (
            re.fullmatch(r"^[a-zA-Z]+ is now a regular member of your guild\.$", line)
            is not None
        ):
            return "guild_member_other"
        elif re.fullmatch(r"^[a-zA-Z]+ has joined your guild\.$", line) is not None:
            return "guild_member_other_accept"
        elif (
            re.fullmatch(
                r"^You have invited \w+ to become a member of the guild\.$", line
            )
            is not None
        ):
            return "guild_member_other_invite"
        elif (
            re.fullmatch(r"^You are now a regular member of the guild\.$", line)
            is not None
        ):
            return "guild_member_you"
        elif re.fullmatch(r"^You are now an officer of the guild\.$", line) is not None:
            return "guild_officer_you"
        elif re.fullmatch(r"^\w+ is now an officer of your guild\.$", line) is not None:
            return "guild_officer_other"
        elif re.fullmatch(r"^You have joined [A-Za-z\s]+\.$", line) is not None:
            return "guild_member_you_accept"
        elif (
            re.fullmatch(r"^Attempting to remove you from the guild\.\.\.$", line)
            is not None
        ):
            return "guild_remove_you_attempt"
        elif (
            re.fullmatch(r"^Unable to remove \w+ from your guild\.$", line) is not None
        ):
            return "guild_remove_fail"
        elif (
            re.fullmatch(r"^You are no longer a member of [A-Za-z\s]+\.$", line)
            is not None
        ):
            return "guild_remove_you"
        elif re.fullmatch(r"^\w+ has declined to join the guild\.$", line) is not None:
            return "guild_invite_other_decline"
        elif (
            re.fullmatch(
                r"^You may only invite living Player Characters in your current zone into your guild\.$",
                line,
            )
            is not None
        ):
            return "guild_invite_instructions"
        elif (
            re.fullmatch(r"^[a-zA-Z]+ is the leader of [A-Za-z\s\-\`]+\.$", line)
            is not None
        ):
            return "guild_status_leader"
        elif (
            re.fullmatch(r"^[a-zA-Z]+ is an officer of [A-Za-z\s\-\`]+\.$", line)
            is not None
        ):
            return "guild_status_officer"
        elif (
            re.fullmatch(r"^[a-zA-Z]+ is a member of [A-Za-z\s\-\`]+\.$", line)
            is not None
        ):
            return "guild_status_member"
        elif re.fullmatch(r"^[a-zA-Z]+ is not in a guild\.$", line) is not None:
            return "guild_status_none"
        elif (
            re.fullmatch(
                r"^You must target a living Player Character, or supply a player name, to list guild status\.$",
                line,
            )
            is not None
        ):
            return "guild_status_instructions"
        elif (
            re.fullmatch(
                r"^This command can only be used by officers and leaders of a guild to set or clear the guild motd\.  To view the guild motd, use the new \/getguildmotd command\.$",
                line,
            )
            is not None
        ):
            return "guild_motd_wrong_command"

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
            re.fullmatch(
                r"^\-\-\w+ has looted [a-zA-Z0-9`\s\:\'\.\-\(\)]+\.\-\-$", line
            )
            is not None
        ):
            return "looted_item_other"
        elif (
            re.fullmatch(
                r"^\-\-You have looted [a-zA-Z0-9`\s\:\'\.\-\(\)]+\.\-\-$", line
            )
            is not None
        ):
            return "looted_item_you"
        elif (
            re.fullmatch(
                r"^You receive .+ from the corpse\.$",
                line,
            )
            is not None
        ):
            return "looted_money_you"
        elif (
            re.fullmatch(
                r"^You receive .+ as your split\.$",
                line,
            )
            is not None
        ):
            return "looted_money_you_split"
        elif (
            re.fullmatch(
                r"^You receive .+ pieces\.$",
                line,
            )
            is not None
        ):
            return "quest_money"
        elif (
            re.fullmatch(
                r"^You will now automatically split money with your group\.$",
                line,
            )
            is not None
        ):
            return "split_on"
        elif (
            re.fullmatch(
                r"^You will no longer split money with your group\.$",
                line,
            )
            is not None
        ):
            return "split_off"
        elif (
            re.fullmatch(
                r"^Please input a valid number of coins to split\.$",
                line,
            )
            is not None
        ):
            return "split_invalid"
        elif (
            re.fullmatch(
                r"^Format\: \/split \<platinum\> \<gold\> \<silver\> \<copper\>\.$",
                line,
            )
            is not None
        ):
            return "split_format"
        elif (
            re.fullmatch(
                r"^e\.g\. \/split 0 1 5 24  would split 0 plat\, 1 gold\, 5 silver\, 24 copper\.$",
                line,
            )
            is not None
        ):
            return "split_format_example"
        elif (
            re.fullmatch(
                r"^\w+ shares money with the group\.$",
                line,
            )
            is not None
        ):
            return "split_shared"
        elif (
            re.fullmatch(
                r"^You receive .+ from [a-zA-Z\s]+ for .+\.$",
                line,
            )
            is not None
        ):
            return "trade_npc_item_sold"
        elif (
            re.fullmatch(r"^The total trade is\: \d+ PP, \d+ GP, \d+ SP, \d+ CP$", line)
            is not None
        ):
            return "trade_money"
        elif re.fullmatch(r"^\w+ adds some coins to the trade\.$", line) is not None:
            return "trade_money_add"
        elif (
            re.fullmatch(
                r"^[a-zA-Z]+ has offered you [a-zA-Z0-9`\(\)\s\:\'\-\.\,]+\.$", line
            )
            is not None
        ):
            return "trade_item"
        elif re.fullmatch(r"^You give .+ to [a-zA-Z`\s]+\.$", line) is not None:
            return "trade_npc_payment"
        elif re.fullmatch(r"^You have cancelled the trade\.$", line) is not None:
            return "trade_cancel_you"
        elif re.fullmatch(r"^\w+ has cancelled the trade\.$", line) is not None:
            return "trade_cancel_other"
        elif (
            re.fullmatch(r"^You may not loot this corpse at this time\.$", line)
            is not None
        ):
            return "loot_wait"
        elif (
            re.fullmatch(
                r"^Error\: OP\_LootRequest\: Corpse not found \(ent \= 0\)$", line
            )
            is not None
        ):
            return "loot_error_corpse"
        elif (
            re.fullmatch(
                r"^Error\: Corpse\:\:LootItem\: BeingLootedBy \!\= client$", line
            )
            is not None
        ):
            return "loot_error_item"
        elif (
            re.fullmatch(r"^You are too far away to loot that corpse\.$", line)
            is not None
        ):
            return "loot_too_far"
        elif (
            re.fullmatch(r"^Someone is already looting that corpse\.$", line)
            is not None
        ):
            return "loot_corpse_locked"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is interested in making a trade\.$", line)
            is not None
        ):
            return "trade_interest"
        elif (
            re.fullmatch(r"^[a-zA-Z]+ has fashioned [a-zA-Z0-9\s\:\-]+\.$", line)
            is not None
        ):
            return "tradeskill_create_other"
        elif (
            re.fullmatch(
                r"^You have fashioned the items together to create something new\!$",
                line,
            )
            is not None
        ):
            return "tradeskill_create_you"
        elif (
            re.fullmatch(
                r"^[a-zA-Z]+ was not successful in making [a-zA-Z0-9\s\:\-]+\.$", line
            )
            is not None
        ):
            return "tradeskill_fail_other"
        elif (
            re.fullmatch(
                r"^You lacked the skills to fashion the items together\.$", line
            )
            is not None
        ):
            return "tradeskill_fail_you"
        elif (
            re.fullmatch(
                r"^You can no longer advance your skill from making this item\.$", line
            )
            is not None
        ):
            return "tradeskill_skill_cap"
        elif (
            re.fullmatch(
                r"^You cannot combine items when your hands are full\!  Your cursor must be free of items and money before you can combine items together in a special container\.$",
                line,
            )
            is not None
        ):
            return "tradeskill_hands_full"
        elif (
            re.fullmatch(
                r"^You cannot combine these items in this container type\!$", line
            )
            is not None
        ):
            return "tradeskill_wrong_container"
        elif (
            re.fullmatch(
                r"^You cannot loot this Lore Item you already have one\.$", line
            )
            is not None
        ):
            return "loot_lore"
        elif (
            re.fullmatch(r"^Trade Error \(Slots in Use\)\. Contact Staff\.$", line)
            is not None
        ):
            return "trade_error"
        elif (
            re.fullmatch(r"^You are too far away from [a-zA-Z`\s]+ to trade\.$", line)
            is not None
        ):
            return "trade_too_far"
        elif (
            re.fullmatch(
                r"^Trade cancelled, duplicated Lore Items would result\.$", line
            )
            is not None
        ):
            return "trade_lore_item"

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
        ### Spell Specific You
        if re.fullmatch(r"^You .+", line) is not None:
            if re.fullmatch(r"^You experience a quickening\.$", line) is not None:
                return "spell_aanyas_quickening_you_on"
            elif re.fullmatch(r"^You drink the potion\.$", line) is not None:
                return "spell_line_potion_you_on"
                # return "spell_accuracy_you_on"
                # return "spell_adroitness_you_on"
                # return "spell_aura_of_antibody_you_on"
                # return "spell_aura_of_cold_you_on"
                # return "spell_aura_of_heat_you_on"
                # return "spell_aura_of_purity_you_on"
                # return "spell_cohesion_you_on"
                # return "spell_null_aura_you_on"
                # return "spell_power_you_on"
                # return "spell_stability_you_on"
                # return "spell_vigor_you_on"
            elif (
                re.fullmatch(r"^You are adorned by an aura of radiant grace\.$", line)
                is not None
            ):
                return "spell_adorning_grace_you_on"
            elif re.fullmatch(r"^You no longer feel shielded\.$", line) is not None:
                return "spell_line_holy_guard_you_off"
                # return "spell_aegis_you_off"
                # return "spell_bulwark_of_faith_you_off"
            elif (
                re.fullmatch(r"^You are enveloped by the Aegis of Ro\.$", line)
                is not None
            ):
                return "spell_aegis_of_ro_you_on"
            elif (
                re.fullmatch(r"^You are filled with the power of Aegolism\.$", line)
                is not None
            ):
                return "spell_aegolism_you_on"
            elif (
                re.fullmatch(
                    r"^You feel feverish(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_line_dot_disease_you_on"
                # return "spell_affliction_you_on"
                # return "spell_plague_you_on"
                # return "spell_scourge_you_on"
                # return "spell_sebilite_pox_you_on"
                # return "spell_sicken_you_on"
            elif re.fullmatch(r"^You feel agile\.$", line) is not None:
                return "spell_agility_you_on"
            elif re.fullmatch(r"^You stop floating\.$", line) is not None:
                return "spell_agilmentes_aria_of_eagles_you_off"
            elif re.fullmatch(r"^You feel much faster\.$", line) is not None:
                return "spell_line_haste_you_on"
                # return "spell_alacrity_you_on"
                # return "spell_celerity_you_on"
                # return "spell_quickness_you_on"
                # return "spell_swift_like_the_wind_you_on"
            elif (
                re.fullmatch(
                    r"^You feel a pulse of static energy wash over you\.$", line
                )
                is not None
            ):
                return "spell_line_bard_cancel_you_on"
                # return "spell_alenias_disenchanting_melody_you_on"
                # return "spell_song_of_highsun_you_on"
            elif re.fullmatch(r"^You feel quite amicable\.$", line) is not None:
                return "spell_line_faction_increase_you_on"
                # return "spell_alliance_you_on"
                # return "spell_benevolence_you_on"
                # return "spell_collaboration_you_on"
            elif re.fullmatch(r"^You no longer feel amicable\.$", line) is not None:
                return "spell_line_faction_increase_you_off"
                # return "spell_alliance_you_off"
                # return "spell_benevolence_you_off"
                # return "spell_collaboration_you_off"
            elif re.fullmatch(r"^You have been charmed\.$", line) is not None:
                return "spell_line_charm_you_on"
                # return "spell_allure_you_on"
                # return "spell_alluring_whispers_you_on"
                # return "spell_beguile_you_on"
                # return "spell_boltrans_agacerie_you_on"
                # return "spell_charm_you_on"
                # return "spell_dictate_you_on"
                # return "spell_dragon_charm_you_on"
                # return "spell_vampire_charm_you_on"
            elif re.fullmatch(r"^You are no longer charmed\.$", line) is not None:
                return "spell_line_charm_you_off"
                # return "spell_allure_you_off"
                # return "spell_alluring_whispers_you_off"
                # return "spell_beguile_you_off"
                # return "spell_boltrans_agacerie_you_off"
                # return "spell_charm_you_off"
                # return "spell_dictate_you_off"
                # return "spell_dragon_charm_you_off"
                # return "spell_vampire_charm_you_off"
            elif (
                re.fullmatch(r"^You feel your health begin to drain away\.$", line)
                is not None
            ):
                return "spell_allure_of_death_you_on"
            elif re.fullmatch(r"^You feel better\.$", line) is not None:
                return "spell_line_feel_better_you_off"
                # return "spell_allure_of_death_you_off"
                # return "spell_dark_pact_you_off"
                # return "spell_infectious_cloud_you_off"
                # return "spell_light_healing_you_on"
                # return "spell_putrid_breath_you_off"
            elif re.fullmatch(r"^You feel alluring\.$", line) is not None:
                return "spell_alluring_aura_you_on"
            elif re.fullmatch(r"^You begin to sweat aloe\.$", line) is not None:
                return "spell_aloe_sweat_you_on"
            elif re.fullmatch(r"^You feel annulled\.$", line) is not None:
                return "spell_annul_magic_you_on"
            elif re.fullmatch(r"^You feel smaller\.$", line) is not None:
                return "spell_line_shrink_you_on"
                # return "spell_ant_legs_you_on"
                # return "spell_shrink_you_on"
            elif re.fullmatch(r"^You return to normal height\.$", line) is not None:
                return "spell_line_shrink_you_off"
                # return "spell_ant_legs_you_off"
                # return "spell_shrink_you_off"
            elif (
                re.fullmatch(r"^You feel the skin peel from your bones\.$", line)
                is not None
            ):
                return "spell_line_nec_regen_you_on"
                # return "spell_arch_lich_you_on"
                # return "spell_call_of_bones_you_on"
                # return "spell_demi_lich_you_on"
                # return "spell_lich_you_on"
            elif re.fullmatch(r"^You feel armored\.$", line) is not None:
                return "spell_line_int_caster_shield_you_on"
                # return "spell_arch_shielding_you_on"
                # return "spell_greater_shielding_you_on"
                # return "spell_lesser_shielding_you_on"
                # return "spell_major_shielding_you_on"
                # return "spell_minor_shielding_you_on"
                # return "spell_shield_of_the_magi_you_on"
                # return "spell_shielding_you_on"
            elif (
                re.fullmatch(r"^You feel the favor of the gods upon you\.$", line)
                is not None
            ):
                return "spell_line_holy_armor_you_on"
                # return "spell_armor_of_faith_you_on"
                # return "spell_guard_you_on"
                # return "spell_holy_armor_you_on"
                # return "spell_shield_of_words_you_on"
            elif re.fullmatch(r"^You no longer feel blessed\.$", line) is not None:
                return "spell_line_holy_armor_you_off"
                # return "spell_armor_of_faith_you_off"
                # return "spell_guard_you_off"
                # return "spell_holy_armor_you_off"
                # return "spell_shield_of_words_you_off"
            elif re.fullmatch(r"^You feel protected\.$", line) is not None:
                return "spell_line_protection_you_on"
                # return "spell_armor_of_protection_you_on"
                # return "spell_kazumis_note_of_preservation_you_on"
            elif re.fullmatch(r"^You feel a shortness of breath\.$", line) is not None:
                return "spell_line_dot_enc_you_on"
                # return "spell_asphyxiate_you_on"
                # return "spell_choke_you_on"
                # return "spell_gasping_embrace_you_on"
                # return "spell_shallow_breath_you_on"
                # return "spell_suffocate_you_on"
            elif re.fullmatch(r"^You can breathe again\.$", line) is not None:
                return "spell_line_dot_enc_you_off"
                # return "spell_asphyxiate_you_off"
                # return "spell_choke_you_off"
                # return "spell_gasping_embrace_you_off"
                # return "spell_shallow_breath_you_off"
                # return "spell_suffocate_you_off"
            elif re.fullmatch(r"^You return to your body\.$", line) is not None:
                return "spell_line_target_vision_you_off"
                # return "spell_assiduous_vision_you_off"
                # return "spell_vision_you_off"
            elif (
                re.fullmatch(r"^You feel your body pulse with energy\.$", line)
                is not None
            ):
                return "spell_line_haste_stats_you_on"
                # return "spell_augment_you_on"
                # return "spell_augmentation_you_on"
                # return "spell_inner_fire_you_on"
            elif re.fullmatch(r"^You begin to regenerate\.$", line) is not None:
                return "spell_line_regen_you_on"
                # return "spell_aura_of_battle_you_on"
                # return "spell_chloroplast_you_on"
                # return "spell_extended_regeneration_you_on"
                # return "spell_pack_chloroplast_you_on"
                # return "spell_pack_regeneration_you_on"
                # return "spell_regeneration_you_on"
                # return "spell_regrowth_you_on"
                # return "spell_regrowth_of_the_grove_you_on"
            elif re.fullmatch(r"^You have stopped regenerating\.$", line) is not None:
                return "spell_line_regen_you_off"
                # return "spell_aura_of_battle_you_off"
                # return "spell_chloroplast_you_off"
                # return "spell_extended_regeneration_you_off"
                # return "spell_fungal_regrowth_you_off"
                # return "spell_pack_chloroplast_you_off"
                # return "spell_pack_regeneration_you_off"
                # return "spell_regeneration_you_off"
                # return "spell_regrowth_you_off"
                # return "spell_regrowth_of_the_grove_you_off"
                # return "spell_stalwart_regeneration_you_off"
            elif (
                re.fullmatch(r"^You feel forgiveness in your mind\.$", line) is not None
            ):
                return "spell_atone_you_on"
            elif (
                re.fullmatch(r"^You are covered by an aura of black petals\.$", line)
                is not None
            ):
                return "spell_aura_of_black_petals_you_on"
            elif (
                re.fullmatch(r"^You are covered by an aura of blue petals\.$", line)
                is not None
            ):
                return "spell_aura_of_blue_petals_you_on"
            elif (
                re.fullmatch(r"^You are covered by an aura of green petals\.$", line)
                is not None
            ):
                return "spell_aura_of_green_petals_you_on"
            elif (
                re.fullmatch(r"^You are covered by an aura of red petals\.$", line)
                is not None
            ):
                return "spell_aura_of_red_petals_you_on"
            elif (
                re.fullmatch(r"^You are covered by an aura of white petals\.$", line)
                is not None
            ):
                return "spell_aura_of_white_petals_you_on"
            elif re.fullmatch(r"^You are entombed in ice\.$", line) is not None:
                return "spell_avalanche_you_on"
                # return "spell_entomb_in_ice_you_on"
            elif (
                re.fullmatch(
                    r"^You are knocked backward(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_avatar_power_you_on"
            elif re.fullmatch(r"^You are enveloped by flame\.$", line) is not None:
                return "spell_barrier_of_combustion_you_on"
            elif (
                re.fullmatch(
                    r"^You are surrounded by a swirling maelstrom of magical force\.$",
                    line,
                )
                is not None
            ):
                return "spell_barrier_of_force_you_on"
            elif re.fullmatch(r"^You begin to spin\.$", line) is not None:
                return "spell_line_spin_you_on"
                # return "spell_bellowing_winds_you_on"
                # return "spell_dyns_dizzying_draught_you_on"
                # return "spell_rodricks_gift_you_on"
                # return "spell_spin_the_bottle_you_on"
                # return "spell_whirl_till_you_hurl_you_on"
            elif re.fullmatch(r"^You feel dizzy\.$", line) is not None:
                return "spell_line_spin_you_off"
                # return "spell_bellowing_winds_you_off"
                # return "spell_dyns_dizzying_draught_you_off"
                # return "spell_spin_the_bottle_you_off"
                # return "spell_whirl_till_you_hurl_you_off"
            elif re.fullmatch(r"^You become mad\.$", line) is not None:
                return "spell_line_berserker_madness_you_on"
                # return "spell_berserker_madness_i_you_on"
                # return "spell_berserker_madness_ii_you_on"
                # return "spell_berserker_madness_iii_you_on"
                # return "spell_berserker_madness_iv_you_on"
            elif re.fullmatch(r"^You become sane.$", line) is not None:
                return "spell_line_berserker_madness_you_off"
                # return "spell_berserker_madness_i_you_off"
                # return "spell_berserker_madness_ii_you_off"
                # return "spell_berserker_madness_iii_you_off"
                # return "spell_berserker_madness_iv_you_off"
            elif re.fullmatch(r"^You feel your agility return\.$", line) is not None:
                return "spell_berserker_strength_you_off"
            elif (
                re.fullmatch(r"^You feel yourself bind to the area\.$", line)
                is not None
            ):
                return "spell_bind_affinity_you_on"
            elif re.fullmatch(r"^You cast Bind Affinity\.$", line) is not None:
                return "spell_bind_affinity_you_cast"
            elif re.fullmatch(r"^You feel your mind fog\.$", line) is not None:
                return "spell_line_memblur_you_on"
                # return "spell_blanket_of_forgetfulness_you_on"
                # return "spell_memory_blur_you_on"
                # return "spell_memory_flux_you_on"
                # return "spell_mind_wipe_you_on"
                # return "spell_reoccurring_amnesia_you_on"
            elif (
                re.fullmatch(
                    r"^You feel your skin ignite(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_line_fire_ignite_you_on"
                # return "spell_blaze_you_on"
                # return "spell_call_of_flame_you_on"
                # return "spell_firestrike_you_on"
                # return "spell_ignite_you_on"
                # return "spell_inferno_shock_you_on"
                # return "spell_lightning_shock_you_on"
                # return "spell_shock_of_flame_you_on"
            elif (
                re.fullmatch(r"^You feel your heart begin to race\.$", line) is not None
            ):
                return "spell_line_npc_item_haste_you_on"
                # return "spell_blessing_of_the_grove_you_on"
                # return "spell_haste_you_on"
                # return "spell_swift_spirit_you_on"
            elif re.fullmatch(r"^You freeze in terror\.$", line) is not None:
                return "spell_blinding_fear_you_on"
            elif re.fullmatch(r"^You are no longer afraid\.$", line) is not None:
                return "spell_line_fear_you_off"
                # return "spell_blinding_fear_you_off"
                # return "spell_cloud_of_fear_you_off"
                # return "spell_dragon_roar_you_off"
                # return "spell_fear_you_off"
                # return "spell_inspire_fear_you_off"
                # return "spell_invoke_fear_you_off"
                # return "spell_panic_you_off"
                # return "spell_wave_of_fear_you_off"
            elif (
                re.fullmatch(r"^You are blinded by a flash of light\.$", line)
                is not None
            ):
                return "spell_line_blind_you_on"
                # return "spell_blinding_luminance_you_on"
                # return "spell_flash_of_light_you_on"
            elif (
                re.fullmatch(r"^You are caught in a raging blizzard.$", line)
                is not None
            ):
                return "spell_blizzard_you_on"
            elif (
                re.fullmatch(
                    r"^You stagger as spirits of frost slam against you(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_line_blizzard_blast_you_on"
                # return "spell_blizzard_blast_you_on"
                # return "spell_spirit_strike_you_on"
                # return "spell_winters_roar_you_on"
            elif (
                re.fullmatch(
                    r"^You feel your lifeforce drain away(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_line_nec_hp_you_on"
                # return "spell_bond_of_death_you_on"
                # return "spell_curse_of_the_garou_you_on"
                # return "spell_deflux_you_on"
                # return "spell_drain_soul_you_on"
                # return "spell_drain_spirit_you_on"
                # return "spell_life_leech_you_on"
                # return "spell_lifespike_you_on"
                # return "spell_lifetap_you_on"
                # return "spell_siphon_you_on"
                # return "spell_siphon_life_you_on"
                # return "spell_spirit_tap_you_on"
                # return "spell_strike_of_the_chosen_you_on"
            elif (
                re.fullmatch(r"^You feel your skin burn from your body\.$", line)
                is not None
            ):
                return "spell_ignite_bones_you_on"
                # return "spell_bone_melt_you_on"
            elif (
                re.fullmatch(
                    r"^You feel the bones of your enemy shatter beneath your hammer\.$",
                    line,
                )
                is not None
            ):
                return "spell_bone_shatter_you_on"
                # return "spell_bone_shatter_you_cast"
            elif re.fullmatch(r"^You are enveloped in lava\.$", line) is not None:
                return "spell_line_high_mag_ds_you_on"
                # return "spell_boon_of_immolation_you_on"
                # return "spell_shield_of_lava_you_on"
            elif re.fullmatch(r"^You feel\.\.\. strange\.$", line) is not None:
                return "spell_boon_of_the_garou_you_on"
            elif re.fullmatch(r"^You feel very brave\.$", line) is not None:
                return "spell_bravery_you_on"
            elif (
                re.fullmatch(
                    r"^You are slammed by an intense gust of wind(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_breath_of_karana_you_on"
            elif (
                re.fullmatch(r"^You are immolated by blazing flames.$", line)
                is not None
            ):
                return "spell_line_dru_fire_you_on"
                # return "spell_breath_of_ro_you_on"
                # return "spell_ros_fiery_sundering_you_on"
            elif (
                re.fullmatch(r"^You feel your heart stop beating\.$", line) is not None
            ):
                return "spell_breath_of_the_dead_you_on"
            elif re.fullmatch(r"^You resume breathing\.$", line) is not None:
                return "spell_line_enduring_breath_you_off"
                # return "spell_breath_of_the_dead_you_off"
                # return "spell_enduring_breath_you_off"
                # return "spell_everlasting_breath_you_off"
            elif (
                re.fullmatch(r"^You feel poison course through your veins\.$", line)
                is not None
            ):
                return "spell_blood_claw_you_on"
            elif (
                re.fullmatch(r"^You are slowed by the mist of the seas\.$", line)
                is not None
            ):
                return "spell_breath_of_the_sea_you_on"
            elif re.fullmatch(r"^You return to normal\.$", line) is not None:
                return "spell_line_brittle_haste_you_off"
                # return "spell_brittle_haste_ii_you_off"
                # return "spell_brittle_haste_iii_you_off"
                # return "spell_brittle_haste_iv_you_off"
            elif (
                re.fullmatch(
                    r"^You reel in pain as every bone in your body vibrates\.$", line
                )
                is not None
            ):
                return "spell_line_brd_bruscos_you_on"
                # return "spell_bruscos_boastful_bellow_you_on"
                # return "spell_bruscos_bombastic_bellow_you_on"
                # return "spell_occlusion_of_sound_you_on"
            elif (
                re.fullmatch(
                    r"^You throw your head back and let loose a great bellow\.$", line
                )
                is not None
            ):
                return "spell_bruscos_boastful_bellow_you_cast"
            elif (
                re.fullmatch(
                    r"^You throw your head back and let loose a stunning bellow\.$",
                    line,
                )
                is not None
            ):
                return "spell_bruscos_bombastic_bellow_you_cast"
            elif (
                re.fullmatch(r"^You feel your skin blister and burn\.$", line)
                is not None
            ):
                return "spell_burn_you_on"
            elif re.fullmatch(r"^You have been teleported\.$", line) is not None:
                return "spell_line_npc_port_you_on"
                # return "spell_burningtouch_you_on"
                # return "spell_trakanons_touch_you_on"
            elif (
                re.fullmatch(
                    r"^You feel your skin singe as the Burst of Fire hits you(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_burst_of_fire_you_on"
            elif (
                re.fullmatch(r"^You are enveloped in a cadeau of flame\.$", line)
                is not None
            ):
                return "spell_cadeau_of_flame_you_on"
            elif re.fullmatch(r"^You feel your body go numb\.$", line) is not None:
                return "spell_calimony_you_on"
            elif re.fullmatch(r"^You regain feeling\.$", line) is not None:
                return "spell_calimony_you_off"
            elif (
                re.fullmatch(r"^You feel your aggression subside\.$", line) is not None
            ):
                return "spell_line_pacify_you_on"
                # return "spell_calm_you_on"
                # return "spell_calm_animal_you_on"
                # return "spell_pacify_you_on"
                # return "spell_soothe_you_on"
                # return "spell_wake_of_tranquility_you_on"
            elif re.fullmatch(r"^You return to view\.$", line) is not None:
                return "spell_camouflage_you_off"
            elif re.fullmatch(r"^You feel a bit dispelled\.$", line) is not None:
                return "spell_cancel_magic_you_on"
                # return "spell_phobocancel_you_on"
            elif (
                re.fullmatch(r"^You are filled by the spirit of water\.$", line)
                is not None
            ):
                return "spell_captain_nalots_quickening_you_on"
            elif (
                re.fullmatch(
                    r"^You are pelted by hailstones(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_cascade_of_hail_you_on"
            elif re.fullmatch(r"^You are engulfed in darkness\.$", line) is not None:
                return "spell_line_nec_snare_you_on"
                # return "spell_cascading_darkness_you_on"
                # return "spell_dooming_darkness_you_on"
                # return "spell_engulfing_darkness_you_on"
            elif re.fullmatch(r"^You feel asinine\.$", line) is not None:
                return "spell_cassindras_insipid_ditty_you_on"
            elif re.fullmatch(r"^You no longer feel asinine\.$", line) is not None:
                return "spell_cassindras_insipid_ditty_you_off"
            elif re.fullmatch(r"^You cast your sight\.$", line) is not None:
                return "spell_cast_sight_you_on"
            elif re.fullmatch(r"^You feel magnanimous of spirit\.$", line) is not None:
                return "spell_center_you_on"
            elif re.fullmatch(r"^You exhale a sickly green cloud\.$", line) is not None:
                return "spell_ceticious_cloud_you_cast"
            elif re.fullmatch(r"^You feel your pulse quicken\.$", line) is not None:
                return "spell_chant_of_battle_other_on"
            elif (
                re.fullmatch(
                    r"^You experience chaotic weightlessness(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_line_grav_flux_you_on"
                # return "spell_chaos_breath_you_on"
                # return "spell_gravity_flux_you_on"
                # return "spell_scream_of_chaos_you_on"
            elif (
                re.fullmatch(r"^You are wracked by chilling poison\.$", line)
                is not None
            ):
                return "spell_chilling_embrace_you_on"
            elif (
                re.fullmatch(r"^You are blasted with chlorophyll\.$", line) is not None
            ):
                return "spell_chloroblast_you_on"
            elif (
                re.fullmatch(r"^You feel an aura of enchantment wash over you\.$", line)
                is not None
            ):
                return "spell_cindas_charismatic_carillon_you_on"
            elif re.fullmatch(r"^You feel the enchantment fade\.$", line) is not None:
                return "spell_cindas_charismatic_carillon_you_off"
            elif (
                re.fullmatch(r"^You are surrounded by a summer haze\.$", line)
                is not None
            ):
                return "spell_circle_of_summer_you_on"
            elif (
                re.fullmatch(r"^You are surrounded by a winter haze\.$", line)
                is not None
            ):
                return "spell_circle_of_winter_you_on"
            elif re.fullmatch(r"^You feel cleansed\.$", line) is not None:
                return "spell_cleanse_you_on"
            elif re.fullmatch(r"^You are in the grip of darkness\.$", line) is not None:
                return "spell_clinging_darkness_you_on"
            elif (
                re.fullmatch(
                    r"^You have been poisoned\.  You begin to feel very dizzy(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_clockwork_poison_you_on"
            elif re.fullmatch(r"^You no longer feel dizzy\.$", line) is not None:
                return "spell_clockwork_poison_you_off"
            elif re.fullmatch(r"^You come into focus\.$", line) is not None:
                return "spell_line_enc_ac_you_off"
                # return "spell_cloud_you_off"
                # return "spell_haze_you_off"
                # return "spell_mist_you_off"
                # return "spell_obscure_you_off"
                # return "spell_shade_off"
                # return "spell_shadow_off"
                # return "spell_umbra_off"
            elif (
                re.fullmatch(
                    r"^You feel your skin freeze(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_line_skin_freeze_you_on"
                # return "spell_cloud_of_disempowerment_you_on"
                # return "spell_frost_shards_you_on"
                # return "spell_frost_shock_you_on"
                # return "spell_ice_comet_you_on"
                # return "spell_shock_of_frost_you_on"
                # return "spell_silver_breath_you_on"
            elif re.fullmatch(r"^You are in a cloud of silence\.$", line) is not None:
                return "spell_line_raid_silence_you_on"
                # return "spell_cloud_of_silence_you_on"
                # return "spell_mesmerizing_breath_you_on"
            elif (
                re.fullmatch(
                    r"^You are immolated by flame(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_column_of_fire_you_on"
            elif (
                re.fullmatch(
                    r"^You are encased in frost(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_line_frost_you_on"
                # return "spell_column_of_frost_you_on"
                # return "spell_ice_you_on"
            elif (
                re.fullmatch(
                    r"^You are engulfed by lightning(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_column_of_lightning_you_on"
            elif (
                re.fullmatch(
                    r"^You feel your skin combust(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_line_combust_you_on"
                # return "spell_combust_you_on"
                # return "spell_conflagration_you_on"
                # return "spell_flame_shock_you_on"
                # return "spell_shock_of_fire_you_on"
            elif re.fullmatch(r"^You summon a companion spirit\.\.$", line) is not None:
                return "spell_companion_spirit_you_on"
            elif re.fullmatch(r"^You are completely healed\.$", line) is not None:
                return "spell_complete_healing_you_on"
                # return "spell_complete_heal_you_on"
            elif (
                re.fullmatch(r"^You stagger from a blow to the head\.$", line)
                is not None
            ):
                return "spell_concussion_you_on"
            elif (
                re.fullmatch(
                    r"^You feel your bones harden and crack from the frost\.$", line
                )
                is not None
            ):
                return "spell_conglaciation_of_bone_you_on"
            elif re.fullmatch(r"^You feel a rush of courage\.$", line) is not None:
                return "spell_courage_you_on"
            elif re.fullmatch(r"^You feel less courageous\.$", line) is not None:
                return "spell_courage_you_off"
            elif (
                re.fullmatch(r"^You feel the pain of a thousand stings\.$", line)
                is not None
            ):
                return "spell_line_swarms_you_on"
                # return "spell_creeping_crud_you_on"
                # return "spell_drifting_death_you_on"
                # return "spell_drones_of_doom_you_on"
                # return "spell_stinging_swarm_you_on"
            elif re.fullmatch(r"^You have been crippled\.$", line) is not None:
                return "spell_cripple_you_on"
            elif re.fullmatch(r"^You feel your strength return\.$", line) is not None:
                return "spell_line_debuff_you_off"
                # return "spell_cripple_you_off"
                # return "spell_disempower_you_off"
                # return "spell_frenzied_strength_you_off"
                # return "spell_incapacitate_you_off"
                # return "spell_listless_power_you_off"
                # return "spell_reckless_strength_you_off"
                # return "spell_resurrection_effects_you_off"
                # return "spell_surge_of_enfeeblement_you_off"
                # return "spell_wave_of_enfeeblement_you_off"
            elif re.fullmatch(r"^You send forth music\.$", line) is not None:
                return "spell_crissions_pixie_strike_you_on"
            elif re.fullmatch(r"^You feel stupid\.$", line) is not None:
                return "spell_curse_of_the_simple_mind_you_on"
            elif re.fullmatch(r"^You feel less stupid\.$", line) is not None:
                return "spell_curse_of_the_simple_mind_you_off"
            elif re.fullmatch(r"^You feel daring\.$", line) is not None:
                return "spell_daring_you_on"
            elif re.fullmatch(r"^You no longer feel daring\.$", line) is not None:
                return "spell_daring_you_off"
            elif (
                re.fullmatch(
                    r"^You stagger as the light of dawn washes over you\.$", line
                )
                is not None
            ):
                return "spell_dawncall_you_on"
            elif re.fullmatch(r"^You are mesmerized\.$", line) is not None:
                return "spell_line_mez_you_on"
                # return "spell_dazzle_you_on"
                # return "spell_mesmerization_you_on"
                # return "spell_mesmerize_you_on"
                # return "spell_sathirs_mesmerization_you_on"
            elif re.fullmatch(r"^You are no longer mesmerized\.$", line) is not None:
                return "spell_line_mez_you_off"
                # return "spell_dazzle_you_off"
                # return "spell_glamour_of_kintaz_you_off"
                # return "spell_mesmerization_you_off"
                # return "spell_mesmerize_you_off"
                # return "spell_sathirs_mesmerization_you_off"
            elif re.fullmatch(r"^You become like the dead\.$", line) is not None:
                return "spell_dead_man_floating_you_on"
                # return "spell_dead_men_floating_you_on"
            elif re.fullmatch(r"^You return to life\.$", line) is not None:
                return "spell_dead_man_floating_you_off"
                # return "spell_dead_men_floating_you_off"
            elif re.fullmatch(r"^You feel a tugging at your soul\.$", line) is not None:
                return "spell_deadly_lifetap_you_on"
            elif (
                re.fullmatch(
                    r"^You have been poisoned(\.  You have taken \d+ point(s|) of damage)\.$",
                    line,
                )
                is not None
            ):
                return "spell_line_poison_you_on"
                # return "spell_deadly_poison_you_on"
                # return "spell_envenomed_bolt_you_on"
                # return "spell_envenomed_breath_you_on"
                # return "spell_feeble_poison_you_on"
                # return "spell_froglok_poison_you_on"
                # return "spell_ikatiars_revenge_you_on"
                # return "spell_manticore_poison_you_on"
                # return "spell_poison_you_on"
                # return "spell_poison_bolt_you_on"
                # return "spell_strong_poison_you_on"
                # return "spell_tainted_breath_you_on"
                # return "spell_venom_of_the_snake_you_on"
                # return "spell_weak_poison_you_on"
            elif (
                re.fullmatch(r"^You are wracked by deadly velium poison\.$", line)
                is not None
            ):
                return "spell_deadly_velium_poison_you_on"
            elif (
                re.fullmatch(r"^You are surrounded by a foreboding aura.$", line)
                is not None
            ):
                return "spell_death_pact_you_on"
            elif re.fullmatch(r"^You no longer appear dead\.$", line) is not None:
                return "spell_feign_death_you_off"
                # return "spell_death_peace_you_off"
            elif re.fullmatch(r"^You feel dexterous\.$", line) is not None:
                return "spell_line_dexterity_you_on"
                # return "spell_deftness_you_on"
                # return "spell_dexterity_you_on"
                # return "spell_dexterous_aura_you_on"
                # return "spell_rising_dexterity_aura_you_on"
            elif re.fullmatch(r"^You feel deliriously nimble\.$", line) is not None:
                return "spell_deliriously_nimble_you_on"
            elif (
                re.fullmatch(
                    r"^You throw your head back and loose a desperate dirge\.$", line
                )
                is not None
            ):
                return "spell_denons_desperate_dirge_you_cast"
            elif (
                re.fullmatch(r"^You are engulfed in devouring darkness\.$", line)
                is not None
            ):
                return "spell_devouring_darkness_you_on"
            elif (
                re.fullmatch(r"^You feel part of your mind melt away\.$", line)
                is not None
            ):
                return "spell_discordant_mind_you_on"
            elif (
                re.fullmatch(
                    r"^You have been diseased(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_line_npc_disease_you_on"
                # return "spell_disease_you_on"
                # return "spell_plagueratdisease_you_on"
                # return "spell_rabies_you_on"
                # return "spell_strong_disease_you_on"
            elif re.fullmatch(r"^You are no longer diseased\.$", line) is not None:
                return "spell_line_npc_disease_you_off"
                # return "spell_disease_you_off"
                # return "spell_plagueratdisease_you_off"
                # return "spell_rabies_you_off"
                # return "spell_strong_disease_you_off"
            elif (
                re.fullmatch(r"^You breathe out a cloud of corruption\.$", line)
                is not None
            ):
                return "spell_diseased_cloud_you_cast"
            elif re.fullmatch(r"^You feel frail\.$", line) is not None:
                return "spell_line_debuff_you_on"
                # return "spell_disempower_you_on"
                # return "spell_incapacitate_you_on"
                # return "spell_listless_power_you_on"
            elif (
                re.fullmatch(r"^You notice something shiny over to your left\.$", line)
                is not None
            ):
                return "spell_distraction_you_on"
            elif (
                re.fullmatch(r"^You are surrounded by a divine barrier\.$", line)
                is not None
            ):
                return "spell_divine_barrier_you_on"
            elif (
                re.fullmatch(
                    r"^You are surrounded by an aura of Divine Favor\.\.$", line
                )
                is not None
            ):
                return "spell_divine_favor_you_on"
            elif (
                re.fullmatch(r"^You begin to radiate with divine glory\.$", line)
                is not None
            ):
                return "spell_divine_glory_you_on"
            elif (
                re.fullmatch(
                    r"^You feel the watchful eyes of the gods upon you\.$", line
                )
                is not None
            ):
                return "spell_divine_intervention_you_on"
            elif re.fullmatch(r"^You are no longer watched\.$", line) is not None:
                return "spell_divine_intervention_you_off"
            elif (
                re.fullmatch(r"^You invoke the presence of the gods\.$", line)
                is not None
            ):
                return "spell_divine_intervention_you_cast"
            elif (
                re.fullmatch(r"^You are bathed in a divine light\.$", line) is not None
            ):
                return "spell_divine_light_you_on"
            elif (
                re.fullmatch(
                    r"^You have been struck by a surge of Divine Might\.$", line
                )
                is not None
            ):
                return "spell_divine_might_effect_you_on"
            elif (
                re.fullmatch(r"^You begin to radiate with divine strength\.$", line)
                is not None
            ):
                return "spell_divine_strength_you_on"
            elif (
                re.fullmatch(
                    r"^You are stunned(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_line_stun_you_on"
                # return "spell_divine_wrath_you_on"
                # return "spell_force_you_on"
                # return "spell_holy_might_you_on"
                # return "spell_markars_clash_you_on"
                # return "spell_markars_discord_you_on"
                # return "spell_sound_of_force_you_on"
                # return "spell_stun_you_on"
                # return "spell_stun_command_you_on"
                # return "spell_tishans_clash_you_on"
                # return "spell_tishans_discord_you_on"
            elif re.fullmatch(r"^You are no longer stunned\.$", line) is not None:
                return "spell_line_stun_you_off"
                # return "spell_divine_wrath_you_off"
                # return "spell_enforced_reverence_you_off"
                # return "spell_force_you_off"
                # return "spell_holy_might_you_off"
                # return "spell_markars_clash_you_off"
                # return "spell_markars_discord_you_off"
                # return "spell_shrieking_howl_you_off"
                # return "spell_sound_of_force_you_off"
                # return "spell_stun_you_off"
                # return "spell_stun_command_you_off"
                # return "spell_stunning_blow_you_off"
                # return "spell_tishans_clash_you_off"
                # return "spell_tishans_discord_you_off"
                # return "spell_verlekarnorms_disaster_you_off"
            elif (
                re.fullmatch(r"^You feel dizzy as poison seeps through you\.$", line)
                is not None
            ):
                return "spell_dizzy_i_you_on"
            elif (
                re.fullmatch(r"^You feel dizzy as poison spreads through you.$", line)
                is not None
            ):
                return "spell_line_dizzy_you_on"
                # return "spell_dizzy_ii_you_on"
                # return "spell_dizzy_iii_you_on"
            elif (
                re.fullmatch(
                    r"^You feel dizzy as poison seeps through your skin\.$", line
                )
                is not None
            ):
                return "spell_dizzy_iv_you_on"
            elif (
                re.fullmatch(r"^You are encased in a cone of icy rage.$", line)
                is not None
            ):
                return "spell_doljons_rage_you_on"
            elif re.fullmatch(r"^You flee in terror\.$", line) is not None:
                return "spell_dragon_roar_you_on"
            elif (
                re.fullmatch(r"^You are caught in a torrent of fire\.$", line)
                is not None
            ):
                return "spell_draught_of_fire_you_on"
            elif (
                re.fullmatch(r"^You are caught in a torrent of jagged ice\.$", line)
                is not None
            ):
                return "spell_draught_of_ice_you_on"
            elif (
                re.fullmatch(r"^You are caught in a torrent of reckless magic\.$", line)
                is not None
            ):
                return "spell_draught_of_jiva_you_on"
            elif re.fullmatch(r"^You feel drowsy\.$", line) is not None:
                return "spell_line_slow_you_on"
                # return "spell_drowsy_you_on"
                # return "spell_tagars_insects_you_on"
                # return "spell_tigirs_insects_you_on"
                # return "spell_turgurs_insects_you_on"
                # return "spell_walking_sleep_you_on"
            elif re.fullmatch(r"^You feel less drowsy\.$", line) is not None:
                return "spell_line_slow_you_off"
                # return "spell_drowsy_you_off"
                # return "spell_tagars_insects_you_off"
                # return "spell_tigirs_insects_you_off"
                # return "spell_turgurs_insects_you_off"
                # return "spell_walking_sleep_you_off"
            elif (
                re.fullmatch(
                    r"^You feel your skin smolder(\.  You have taken \d+ point(s|) of damage)\.$",
                    line,
                )
                is not None
            ):
                return "spell_drybonefireburst_you_on"
            elif re.fullmatch(r"^You cast Smolder\.$", line) is not None:
                return "spell_line_npc_fire_you_cast"
                # return "spell_drybonefireburst_you_cast"
                # return "spell_smolder_you_cast"
                # return "spell_snakeelefireburst_you_cast"
            elif re.fullmatch(r"^You feel a rush of adrenaline\.$", line) is not None:
                return "spell_dulsehound_you_on"
            elif (
                re.fullmatch(
                    r"^You feel the ground shake(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_earthquake_you_on"
            elif re.fullmatch(r"^You feel weaker\.$", line) is not None:
                return "spell_line_strength_debuff_you_on"
                # return "spell_ebbing_strength_you_on"
                # return "spell_weaken_you_on"
            elif re.fullmatch(r"^You feel infused with echinacea\.$", line) is not None:
                return "spell_echinacea_infusion_you_on"
            elif (
                re.fullmatch(r"^You feel protected from fire and ice\.$", line)
                is not None
            ):
                return "spell_line_int_resists_you_on"
                # return "spell_elemental_armor_you_on"
                # return "spell_elemental_shield_you_on"
            elif re.fullmatch(r"^You are snared by vines of kelp\.$", line) is not None:
                return "spell_embrace_of_the_kelpmaiden_you_on"
            elif re.fullmatch(r"^You break free of the kelp\.$", line) is not None:
                return "spell_embrace_of_the_kelpmaiden_you_off"
            elif re.fullmatch(r"^You feel protected from cold\.$", line) is not None:
                return "spell_line_cold_resist_you_on"
                # return "spell_endure_cold_you_on"
                # return "spell_psalm_of_warmth_you_on"
            elif re.fullmatch(r"^You feel protected from disease\.$", line) is not None:
                return "spell_line_disease_resist_you_on"
                # return "spell_endure_disease_you_on"
                # return "spell_psalm_of_vitality_you_on"
            elif re.fullmatch(r"^You feel protected from fire\.$", line) is not None:
                return "spell_line_fire_resist_you_on"
                # return "spell_endure_fire_you_on"
                # return "spell_psalm_of_cooling_you_on"
            elif re.fullmatch(r"^You feel protected from magic\.$", line) is not None:
                return "spell_line_magic_resist_you_on"
                # return "spell_endure_magic_you_on"
                # return "spell_group_resist_magic_you_on"
                # return "spell_psalm_of_mystic_shielding_you_on"
            elif re.fullmatch(r"^You feel protected from poison\.$", line) is not None:
                return "spell_line_poison_resist_you_on"
                # return "spell_endure_poison_you_on"
                # return "spell_psalm_of_purity_you_on"
            elif re.fullmatch(r"^You feel no need to breathe\.$", line) is not None:
                return "spell_line_enduring_breath_you_on"
                # return "spell_enduring_breath_you_on"
                # return "spell_everlasting_breath_you_on"
            elif (
                re.fullmatch(r"^You feel energy draining from your body\.$", line)
                is not None
            ):
                return "spell_energy_sap_you_on"
            elif re.fullmatch(r"^You execute an energy sap\.$", line) is not None:
                return "spell_energy_sap_you_cast"
            elif re.fullmatch(r"^You feel enfeebled\.$", line) is not None:
                return "spell_enfeeblement_you_on"
            elif (
                re.fullmatch(r"^You are stunned with reverent awe\.$", line) is not None
            ):
                return "spell_enforced_reverence_you_on"
            elif re.fullmatch(r"^You have been enlightened\.$", line) is not None:
                return "spell_enlightenment_you_on"
            elif re.fullmatch(r"^You are ensnared\.$", line) is not None:
                return "spell_line_snare_you_on"
                # return "spell_ensnare_you_on"
                # return "spell_snare_you_on"
            elif re.fullmatch(r"^You are no longer ensnared\.$", line) is not None:
                return "spell_ensnare_you_off"
                # return "spell_snare_you_off"
            elif re.fullmatch(r"^You have been enthralled\.$", line) is not None:
                return "spell_enthrall_you_on"
            elif re.fullmatch(r"^You are no longer enthralled\.$", line) is not None:
                return "spell_enthrall_you_off"
            elif (
                re.fullmatch(r"^You succumb to the enticement of flame\.$", line)
                is not None
            ):
                return "spell_enticement_of_flame_you_on"
            elif (
                re.fullmatch(
                    r"^You feel an aura of elemental protection surrounding you\.$",
                    line,
                )
                is not None
            ):
                return "spell_elemental_rhythms_you_on"
            elif re.fullmatch(r"^You have been entranced\.$", line) is not None:
                return "spell_entrance_you_on"
            elif re.fullmatch(r"^You are no longer entranced\.$", line) is not None:
                return "spell_entrance_you_off"
            elif (
                re.fullmatch(r"^You feel your essence drain away\.$", line) is not None
            ):
                return "spell_essence_drain_you_on"
            elif re.fullmatch(r"^You feel your life drain away\.$", line) is not None:
                return "spell_essence_tap_you_on"
            elif re.fullmatch(r"^You feel confused\.$", line) is not None:
                return "spell_eye_of_confusion_you_on"
            elif re.fullmatch(r"^You are no longer confused\.$", line) is not None:
                return "spell_eye_of_confusion_you_off"
            elif re.fullmatch(r"^You fade out\.$", line) is not None:
                return "spell_fade_you_on"
            elif re.fullmatch(r"^You reappear\.$", line) is not None:
                return "spell_fade_you_off"
            elif (
                re.fullmatch(r"^You feel your skin burn with poison\.$", line)
                is not None
            ):
                return "spell_fangols_breath_you_on"
            elif (
                re.fullmatch(r"^You are fascinated by the pretty colors\.$", line)
                is not None
            ):
                return "spell_fascination_you_on"
            elif re.fullmatch(r"^You are no longer fascinated\.$", line) is not None:
                return "spell_fascination_you_off"
            elif re.fullmatch(r"^You feel your vigor drain away\.$", line) is not None:
                return "spell_fatigue_drain_you_on"
            elif re.fullmatch(r"^You cast Fear\.$", line) is not None:
                return "spell_fear_you_cast"
            elif (
                re.fullmatch(r"^You feel your life force drain away\.$", line)
                is not None
            ):
                return "spell_line_leach_you_on"
                # return "spell_feast_of_blood_you_on"
                # return "spell_lifedraw_you_on"
                # return "spell_soul_bond_you_on"
                # return "spell_soul_consumption_you_on"
                # return "spell_soul_well_you_on"
            elif re.fullmatch(r"^You feel weak\.$", line) is not None:
                return "spell_line_enc_debuff_you_on"
                # return "spell_feckless_might_you_on"
                # return "spell_insipid_weakness_you_on"
                # return "spell_weakness_you_on"
            elif (
                re.fullmatch(
                    r"^You feel your mind fuzz as poison spreads through your body\.$",
                    line,
                )
                is not None
            ):
                return "spell_line_feeble_mind_you_on"
                # return "spell_feeble_mind_i_you_on"
                # return "spell_feeble_mind_ii_you_on"
                # return "spell_feeble_mind_iii_you_on"
            elif (
                re.fullmatch(
                    r"^You feel your mind fuzz as poison permeates your body\.$", line
                )
                is not None
            ):
                return "spell_feeble_mind_iv_you_on"
            elif (
                re.fullmatch(r"^You are enveloped in blazing energy\.$", line)
                is not None
            ):
                return "spell_feedback_you_on"
            elif (
                re.fullmatch(r"^You are enveloped by an aura of fiery might\.$", line)
                is not None
            ):
                return "spell_fiery_might_you_on"
            elif (
                re.fullmatch(
                    r"^You are immolated in flame(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_line_fire_flame_you_on"
                # return "spell_fire_you_on"
                # return "spell_pillar_of_fire_you_on"
                # return "spell_supernova_you_on"
            elif (
                re.fullmatch(r"^You are blasted by blazing winds\.$", line) is not None
            ):
                return "spell_fire_spiral_of_alkabor_you_on"
            elif (
                re.fullmatch(
                    r"^You have been struck by the shocking Fist of Karana\.$", line
                )
                is not None
            ):
                return "spell_fist_of_karana_you_on"
            elif re.fullmatch(r"^You are gripped by pain\.$", line) is not None:
                return "spell_fist_of_sentience_you_on"
            elif re.fullmatch(r"^You are encased in water\.$", line) is not None:
                return "spell_fist_of_water_you_on"
            elif (
                re.fullmatch(
                    r"^You are surrounded by an outline of cold flame\.$", line
                )
                is not None
            ):
                return "spell_fixation_of_ro_you_on"
            elif (
                re.fullmatch(r"^You are surrounded by flickering flames\.$", line)
                is not None
            ):
                return "spell_flame_lick_you_on"
                # return "spell_obsidian_shatter_you_on"
            elif re.fullmatch(r"^You burn\.$", line) is not None:
                return "spell_flames_of_ro_you_on"
            elif re.fullmatch(r"^You no longer feel rotten\.$", line) is not None:
                return "spell_line_flesh_rot_you_off"
                # return "spell_flesh_rot_i_you_off"
                # return "spell_flesh_rot_ii_you_off"
                # return "spell_flesh_rot_iii_you_off"
            elif re.fullmatch(r"^You execute a flurry\.$", line) is not None:
                return "spell_flurry_you_off"
            elif re.fullmatch(r"^You feel focused\.$", line) is not None:
                return "spell_focus_of_spirit_you_on"
            elif (
                re.fullmatch(
                    r"^You have been force struck(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_line_force_strike_you_on"
                # return "spell_force_shock_you_on"
                # return "spell_force_strike_you_on"
                # return "spell_rage_of_the_sky_you_on"
            elif (
                re.fullmatch(r"^You are blasted by energy laden winds\.$", line)
                is not None
            ):
                return "spell_force_spiral_of_alkabor_you_on"
            elif re.fullmatch(r"^You slow down\.$", line) is not None:
                return "spell_line_enc_slow_you_on"
                # return "spell_forlorn_deeds_you_on"
                # return "spell_languid_pace_you_on"
                # return "spell_rejuvenation_pace_you_on"
                # return "spell_selos_accelerando_you_off"
                # return "spell_shiftless_deeds_you_on"
                # return "spell_tepid_deeds_you_on"
            elif re.fullmatch(r"^You are no longer a bear\.$", line) is not None:
                return "spell_form_of_the_great_bear_you_off"
            elif re.fullmatch(r"^You are now a wolf\.$", line) is not None:
                return "spell_line_wolf_form_you_on"
                # return "spell_form_of_the_great_wolf_you_on"
                # return "spell_form_of_the_howler_you_on"
                # return "spell_form_of_the_hunter_you_on"
                # return "spell_greater_wolf_form_you_on"
                # return "spell_share_wolf_form_you_on"
                # return "spell_wolf_form_you_on"
            elif re.fullmatch(r"^You are no longer a wolf\.$", line) is not None:
                return "spell_line_wolf_form_you_off"
                # return "spell_form_of_the_great_wolf_you_off"
                # return "spell_form_of_the_howler_you_off"
                # return "spell_form_of_the_hunter_you_off"
                # return "spell_greater_wolf_form_you_off"
                # return "spell_share_wolf_form_you_off"
                # return "spell_wolf_form_you_off"
            elif re.fullmatch(r"^You focus your concentration\.$", line) is not None:
                return "spell_fortitude_you_on"
            elif re.fullmatch(r"^You feel more agile\.$", line) is not None:
                return "spell_feet_like_cat_you_on"
            elif (
                re.fullmatch(r"^You exhale a freezing cone of cold\.$", line)
                is not None
            ):
                return "spell_freezing_breath_you_cast"
            elif re.fullmatch(r"^You summon a frenzied spirit\.$", line) is not None:
                return "spell_frenzied_spirit_you_on"
            elif re.fullmatch(r"^You go berserk\.$", line) is not None:
                return "spell_line_berserk_you_on"
                # return "spell_frenzy_you_on"
                # return "spell_fury_you_on"
                # return "spell_mcvaxius_berserker_crescendo_you_on"
            elif (
                re.fullmatch(r"^You are chilled by a bolt of frost\.$", line)
                is not None
            ):
                return "spell_frost_bolt_you_on"
            elif re.fullmatch(r"^You spout frost\.$", line) is not None:
                return "spell_frost_breath_you_cast"
            elif (
                re.fullmatch(
                    r"^You feel your skin numb as the frost rift strikes you(\.  You have taken \d+ point(s|) of damage)\.$",
                    line,
                )
                is not None
            ):
                return "spell_frost_rift_you_on"
            elif (
                re.fullmatch(r"^You are blasted by freezing winds\.$", line) is not None
            ):
                return "spell_line_wiz_alkabor_you_on"
                # return "spell_frost_spiral_of_alkabor_you_on"
                # return "spell_wrath_of_alkabor_you_on"
            elif (
                re.fullmatch(r"^You are assaulted  by a storm of frost\.$", line)
                is not None
            ):
                return "spell_frost_storm_you_on"
            elif re.fullmatch(r"^You are coverd in ice\.$", line) is not None:
                return "spell_frost_strike_you_on"
            elif re.fullmatch(r"^You are shredded by ice\.$", line) is not None:
                return "spell_frosty_death_you_on"
            elif (
                re.fullmatch(r"^You feel a static pulse engulf you\.$", line)
                is not None
            ):
                return "spell_fufils_curtailing_chant_you_on"
            elif (
                re.fullmatch(r"^You are covered by a sticky substance\.$", line)
                is not None
            ):
                return "spell_fungal_regrowth_you_on"
            elif re.fullmatch(r"^You inhale the fungus spores\.$", line) is not None:
                return "spell_fungus_spores_you_on"
            elif re.fullmatch(r"^You feel stronger\.$", line) is not None:
                return "spell_line_strength_you_on"
                # return "spell_furious_strength_you_on"
                # return "spell_impart_strength_you_on"
                # return "spell_spirit_strength_you_on"
                # return "spell_storm_strength_you_on"
                # return "spell_strength_of_earth_you_on"
                # return "spell_strength_of_stone_you_on"
                # return "spell_strength_of_the_kunzar_you_on"
                # return "spell_strengthen_you_on"
                # return "spell_tumultuous_strength_you_on"
            elif (
                re.fullmatch(r"^You are struck by a sudden burst of force\.$", line)
                is not None
            ):
                return "spell_furor_you_on"
            elif re.fullmatch(r"^You gather shadows about you\.$", line) is not None:
                return "spell_gather_shadows_you_on"
            elif (
                re.fullmatch(r"^You feel the strength of Karana infuse you\.$", line)
                is not None
            ):
                return "spell_girdle_of_karana_you_on"
            elif (
                re.fullmatch(r"^You are mesmerized by the Glamour of Kintaz\.$", line)
                is not None
            ):
                return "spell_glamour_of_kintaz_you_on"
            elif re.fullmatch(r"^You feel much better\.$", line) is not None:
                return "spell_line_healing_you_on"
                # return "spell_greater_healing_you_on"
                # return "spell_healing_you_on"
                # return "spell_invigorate_you_on"
                # return "spell_knights_blessing_you_on"
                # return "spell_natures_touch_you_on"
                # return "spell_superior_healing_you_on"
                # return "spell_word_of_healing_you_on"
                # return "spell_word_of_health_you_on"
            elif re.fullmatch(r"^You are no longer guarded\.$", line) is not None:
                return "spell_guardian_you_off"
            elif (
                re.fullmatch(
                    r"^You feel an aura of mystic protection surround you\.$", line
                )
                is not None
            ):
                return "spell_guardian_rhythms_you_on"
            elif re.fullmatch(r"^You summon a guardian spirit\.$", line) is not None:
                return "spell_guardian_spirit_you_on"
            elif re.fullmatch(r"^You no longer feel pain\.$", line) is not None:
                return "spell_harmshield_you_on"
            elif re.fullmatch(r"^You regain your will to fight\.$", line) is not None:
                return "spell_harpy_voice_you_off"
            elif (
                re.fullmatch(r"^You gather mana from your surroundings\.$", line)
                is not None
            ):
                return "spell_harvest_you_on"
            elif (
                re.fullmatch(r"^You check your plant for dead leaves\.$", line)
                is not None
            ):
                return "spell_harvest_leaves_you_on"
            elif re.fullmatch(r"^You feel healthy\.$", line) is not None:
                return "spell_health_you_on"
            elif re.fullmatch(r"^You feel heroic\.$", line) is not None:
                return "spell_line_heroic_valor_you_on"
                # return "spell_heroic_bond_you_on"
                # return "spell_heroism_you_on"
            elif (
                re.fullmatch(
                    r"^You feel the holy wrath of the heavens upon you\.\.$", line
                )
                is not None
            ):
                return "spell_holy_shock_you_on"
            elif re.fullmatch(r"^You hug your doll\.$", line) is not None:
                return "spell_hug_you_on"
            elif re.fullmatch(r"^You body thaws\.$", line) is not None:
                return "spell_ice_strike_you_off"
            elif re.fullmatch(r"^You are pelted by sleet\.$", line) is not None:
                return "spell_icestrike_you_on"
            elif re.fullmatch(r"^You feel different\.$", line) is not None:
                return "spell_line_illusion_you_on"
                # return "spell_illusion_air_elemental_you_on"
                # return "spell_illusion_barbarian_you_on"
                # return "spell_illusion_dark_elf_you_on"
                # return "spell_illusion_dry_bone_you_on"
                # return "spell_illusion_dwarf_you_on"
                # return "spell_illusion_earth_elemental_you_on"
                # return "spell_illusion_erudite_you_on"
                # return "spell_illusion_fire_elemental_you_on"
                # return "spell_illusion_gnome_you_on"
                # return "spell_illusion_halfelf_you_on"
                # return "spell_illusion_halfling_you_on"
                # return "spell_illusion_high_elf_you_on"
                # return "spell_illusion_human_you_on"
                # return "spell_illusion_iksar_you_on"
                # return "spell_illusion_ogre_you_on"
                # return "spell_illusion_skeleton_you_on"
                # return "spell_illusion_spirit_wolf_you_on"
                # return "spell_illusion_tree_you_on"
                # return "spell_illusion_troll_you_on"
                # return "spell_illusion_water_elemental_you_on"
                # return "spell_illusion_werewolf_you_on"
                # return "spell_illusion_wood_elf_you_on"
                # return "spell_minor_illusion_you_on"
            elif (
                re.fullmatch(r"^You are surrounded by blazing flames\.$", line)
                is not None
            ):
                return "spell_immolate_you_on"
            elif re.fullmatch(r"^You exhale a cloud of flame\.$", line) is not None:
                return "spell_immolating_breath_you_cast"
            elif re.fullmatch(r"^You vanish\.$", line) is not None:
                return "spell_line_invis_you_on"
                # return "spell_improved_invisibility_you_on"
                # return "spell_improved_superior_camouflage_you_on"
                # return "spell_invisibility_you_on"
                # return "spell_superior_camouflage_you_on"
            elif re.fullmatch(r"^You appear\.$", line) is not None:
                return "spell_line_invis_you_off"
                # return "spell_improved_invisibility_you_off"
                # return "spell_improved_superior_camouflage_you_off"
                # return "spell_invisibility_you_off"
                # return "spell_invisibility_cloak_you_off"
                # return "spell_superior_camouflage_you_off"
            elif (
                re.fullmatch(r"^You feel your skin ignite and char\.$", line)
                is not None
            ):
                return "spell_char_you_on"
            elif re.fullmatch(r"^You feel charismatic\.$", line) is not None:
                return "spell_line_charisma_you_on"
                # return "spell_charisma_you_on"
                # return "spell_glamour_you_on"
                # return "spell_solons_charismatic_concord_you_on"
            elif re.fullmatch(r"^You begin to run\.$", line) is not None:
                return "spell_chase_the_moon_you_on"
            elif re.fullmatch(r"^You stop\.$", line) is not None:
                return "spell_chase_the_moon_you_off"
            elif (
                re.fullmatch(r"^You feel your skin frost from your body\.$", line)
                is not None
            ):
                return "spell_chill_bones_you_on"
            elif (
                re.fullmatch(r"^You are immolated by raging energy\.$", line)
                is not None
            ):
                return "spell_circle_of_force_you_on"
            elif (
                re.fullmatch(r"^You feel your health begin to drain\.$", line)
                is not None
            ):
                return "spell_dark_pact_you_on"
            elif (
                re.fullmatch(
                    r"^You feel the blessing of ancient Coldain heroes\.$", line
                )
                is not None
            ):
                return "spell_frostreavers_blessing_you_on"
            elif re.fullmatch(r"^You can feel your legs again\.$", line) is not None:
                return "spell_gelatroot_you_off"
            elif (
                re.fullmatch(r"^You shriek as your bones are ablaze\.$", line)
                is not None
            ):
                return "spell_incinerate_bones_you_on"
            elif (
                re.fullmatch(r"^You burn within the inferno of Al'Kabor\.$", line)
                is not None
            ):
                return "spell_inferno_of_alkabor_you_on"
            elif re.fullmatch(r"^You are enveloped in flame\.$", line) is not None:
                return "spell_line_low_mag_ds_you_on"
                # return "spell_inferno_shield_you_on"
                # return "spell_shield_of_flame_you_on"
            elif re.fullmatch(r"^You are healed\.$", line) is not None:
                return "spell_infusion_you_on"
            elif (
                re.fullmatch(r"^You feel a fever settle upon you\.$", line) is not None
            ):
                return "spell_line_shm_insidious_you_on"
                # return "spell_insidious_decay_you_on"
                # return "spell_insidious_fever_you_on"
                # return "spell_insidious_malady_you_on"
            elif (
                re.fullmatch(
                    r"^You feel gravity reverse(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_invert_gravity_you_on"
            elif (
                re.fullmatch(
                    r"^You vanish amidst the sound of whirrs and clicks\.$", line
                )
                is not None
            ):
                return "spell_invisibility_cloak_you_on"
            elif re.fullmatch(r"^You feel your skin tingle\.$", line) is not None:
                return "spell_line_invis_undead_you_on"
                # return "spell_invisibility_to_undead_you_on"
                # return "spell_invisibility_versus_undead_you_on"
                # return "spell_sunskin_you_on"
            elif re.fullmatch(r"^You feel inspired\.$", line) is not None:
                return "spell_jonthans_inspiration_you_on"
            elif re.fullmatch(r"^You feel provoked\.$", line) is not None:
                return "spell_jonthans_provocation_you_on"
            elif re.fullmatch(r"^You whistle an ancient warsong\.$", line) is not None:
                return "spell_jonthans_whistling_warsong_you_on"
            elif re.fullmatch(r"^You stop whistling\.$", line) is not None:
                return "spell_jonthans_whistling_warsong_you_off"
            elif re.fullmatch(r"^You no longer feel protected\.$", line) is not None:
                return "spell_kazumis_note_of_preservation_you_off"
            elif re.fullmatch(r"^You no longer feel sleepy\.$", line) is not None:
                return "spell_kelins_lucid_lullaby_you_off"
            elif re.fullmatch(r"^You feel a strong sense of loss\.$", line) is not None:
                return "spell_kelins_lugubrious_lament_you_on"
            elif re.fullmatch(r"^You no longer feel sad\.$", line) is not None:
                return "spell_kelins_lugubrious_lament_you_off"
            elif (
                re.fullmatch(r"^You send forth a burst of energy\.$", line) is not None
            ):
                return "spell_knockback_you_cast"
            elif re.fullmatch(r"^You spasm violently\.$", line) is not None:
                return "spell_kylies_venom_you_on"
            elif re.fullmatch(r"^You speed back up\.\.$", line) is not None:
                return "spell_line_enc_slow_you_off"
                # return "spell_languid_pace_you_off"
                # return "spell_rejuvenation_you_off"
            elif re.fullmatch(r"^You are very sad\.$", line) is not None:
                return "spell_largarns_lamentation_you_on"
            elif re.fullmatch(r"^You are no longer sad\.$", line) is not None:
                return "spell_largarns_lamentation_you_off"
            elif (
                re.fullmatch(r"^You feel your blood begin to leach away\.$", line)
                is not None
            ):
                return "spell_leach_you_on"
            elif (
                re.fullmatch(r"^You are surrounded by a thorny barrier\.$", line)
                is not None
            ):
                return "spell_line_dru_ds_you_on"
                # return "spell_legacy_of_spike_you_on"
                # return "spell_legacy_of_thorn_you_on"
                # return "spell_shield_of_barbs_you_on"
                # return "spell_shield_of_brambles_you_on"
                # return "spell_shield_of_spikes_you_on"
                # return "spell_shield_of_thistles_you_on"
                # return "spell_shield_of_thorns_you_on"
                # return "spell_thorny_shield_you_on"
            elif re.fullmatch(r"^You can no longer levitate\.$", line) is not None:
                return "spell_levitate_you_off"
                # return "spell_levitation_you_off"
            elif re.fullmatch(r"^You no longer sense the dead\.$", line) is not None:
                return "spell_locate_corpse_you_off"
            elif re.fullmatch(r"^You feel less aggressive\.$", line) is not None:
                return "spell_lull_you_on"
            elif (
                re.fullmatch(r"^You succumb to the lure of flame\.$", line) is not None
            ):
                return "spell_lure_of_flame_you_on"
            elif (
                re.fullmatch(r"^You succumb to the lure of frost\.$", line) is not None
            ):
                return "spell_lure_of_frost_you_on"
            elif re.fullmatch(r"^You succumb to the lure of ice\.$", line) is not None:
                return "spell_lure_of_ice_you_on"
            elif (
                re.fullmatch(r"^You succumb to the lure of lightning\.$", line)
                is not None
            ):
                return "spell_lure_of_lightning_you_on"
            elif re.fullmatch(r"^You lose the locating tune\.$", line) is not None:
                return "spell_lyssas_locating_lyric_you_on"
            elif re.fullmatch(r"^You have been Magi cursed\.$", line) is not None:
                return "spell_magi_curse_you_on"
            elif (
                re.fullmatch(r"^You are caught in a malevolent grasp\.$", line)
                is not None
            ):
                return "spell_malevolent_grasp_you_on"
            elif (
                re.fullmatch(
                    r"^You feel your life draining into your mind(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_mana_conversion_you_on"
            elif (
                re.fullmatch(r"^You feel your mental energies slip away\.$", line)
                is not None
            ):
                return "spell_mana_sieve_you_on"
            elif re.fullmatch(r"^You are no longer berserk\.$", line) is not None:
                return "spell_mcvaxius_berserker_crescendo_you_off"
            elif re.fullmatch(r"^You are more alert\.$", line) is not None:
                return "spell_mcvaxius_rousing_rondo_you_on"
            elif re.fullmatch(r"^You are no longer roused\.$", line) is not None:
                return "spell_mcvaxius_rousing_rondo_you_off"
            elif re.fullmatch(r"^You exhale a silent cloud\.$", line) is not None:
                return "spell_mesmerizing_breath_you_cast"
            elif re.fullmatch(r"^You feel a little better\.$", line) is not None:
                return "spell_minor_healing_you_on"
            elif (
                re.fullmatch(r"^You summon a familiar of the Mistwalker\.$", line)
                is not None
            ):
                return "spell_mistwalker_you_on"
            elif (
                re.fullmatch(
                    r"^You modulate(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_modulation_you_on"
            elif re.fullmatch(r"^You summon a spirit of nature\.$", line) is not None:
                return "spell_nature_walkers_behest_you_on"
            elif (
                re.fullmatch(
                    r"^You have been struck down by the wrath of nature\.$", line
                )
                is not None
            ):
                return "spell_natures_wrath_you_on"
            elif re.fullmatch(r"^You feel dispelled\.$", line) is not None:
                return "spell_nullify_magic_you_on"
                # return "spell_neutralize_magic_you_on"
            elif re.fullmatch(r"^You feel small\.$", line) is not None:
                return "spell_nillipus_march_of_the_wee_other_on"
            elif re.fullmatch(r"^You feel bigger\.$", line) is not None:
                return "spell_nillipus_march_of_the_wee_you_on"
            elif (
                re.fullmatch(r"^You feel an aura of protection engulf you.$", line)
                is not None
            ):
                return "spell_nivs_melody_of_preservation_you_on"
            elif re.fullmatch(r"^You feel stone cold\.$", line) is not None:
                return "spell_numbing_cold_you_on"
            elif re.fullmatch(r"^You begin to radiate\.$", line) is not None:
                return "spell_line_wiz_ds_you_on"
                # return "spell_okeils_flickering_flame_you_on"
                # return "spell_okeils_radiation_you_on"
            elif re.fullmatch(r"^You feel dazed\.$", line) is not None:
                return "spell_one_hundred_blows_you_off"
            elif (
                re.fullmatch(r"^You feel the spirit of wolf enter you\.$", line)
                is not None
            ):
                return "spell_spirit_of_wolf_you_on"
                # return "spell_pack_spirit_you_on"
            elif re.fullmatch(r"^You feel nimble\.$", line) is not None:
                return "spell_nimble_you_on"
            elif (
                re.fullmatch(
                    r"^You throw your head back and let loose a piercing blast\.$", line
                )
                is not None
            ):
                return "spell_occlusion_of_sound_you_cast"
            elif (
                re.fullmatch(r"^You begin to spin from one hundred blows\.\.$", line)
                is not None
            ):
                return "spell_one_hundred_blows_you_on"
            elif (
                re.fullmatch(
                    r"^You deftly manipulate the boxes lock and flip the tumblers\.$",
                    line,
                )
                is not None
            ):
                return "spell_open_black_box_you_on"
            elif (
                re.fullmatch(r"^You are adorned in an aura of radiant grace\.$", line)
                is not None
            ):
                return "spell_overwhelming_splendor_you_on"
            elif re.fullmatch(r"^You panic\.$", line) is not None:
                return "spell_panic_you_on"
            elif re.fullmatch(r"^You feel your muscles lock\.$", line) is not None:
                return "spell_line_paralyzing_poison_you_on"
                # return "spell_paralyzing_poison_i_you_on"
                # return "spell_paralyzing_poison_ii_you_on"
                # return "spell_paralyzing_poison_iii_you_on"
            elif (
                re.fullmatch(r"^You are covered in illusionary armor\.$", line)
                is not None
            ):
                return "spell_phantom_armor_you_on"
            elif (
                re.fullmatch(
                    r"^You are covered in illusionary platemail armor\.\.$", line
                )
                is not None
            ):
                return "spell_phantom_plate_you_on"
            elif re.fullmatch(r"^You feel very dispelled\.$", line) is not None:
                return "spell_line_enc_cancel_you_on"
                # return "spell_pillage_enchantment_you_on"
                # return "spell_strip_enchantment_you_on"
            elif (
                re.fullmatch(r"^You are encased within a pillar of frost\.$", line)
                is not None
            ):
                return "spell_pillar_of_frost_you_on"
            elif (
                re.fullmatch(
                    r"^You are immolated in a pillar of raging lightning\.$", line
                )
                is not None
            ):
                return "spell_pillar_of_lightning_you_on"
            elif (
                re.fullmatch(r"^You are sheathed in ice crystals\.$", line) is not None
            ):
                return "spell_pogonip_you_on"
            elif (
                re.fullmatch(r"^You have been injected with a chilling poison\.$", line)
                is not None
            ):
                return "spell_poisonous_chill_you_on"
            elif re.fullmatch(r"^You feel primeval\.$", line) is not None:
                return "spell_primal_essence_you_on"
            elif (
                re.fullmatch(r"^You are washed in a vibrant blue light\.$", line)
                is not None
            ):
                return "spell_prime_healers_blessing_you_on"
            elif re.fullmatch(r"^You feel sick\.$", line) is not None:
                return "spell_line_npc_sick_you_on"
                # return "spell_putrid_breath_you_on"
                # return "spell_rodricks_gift_you_on"
            elif (
                re.fullmatch(
                    r"^You are surrounded by the Quivering Veil of Xarn\.$", line
                )
                is not None
            ):
                return "spell_quivering_veil_of_xarn_you_on"
            elif re.fullmatch(r"^You feel radiant\.$", line) is not None:
                return "spell_radiant_visage_you_on"
            elif re.fullmatch(r"^You fly into a chaotic rage\.$", line) is not None:
                return "spell_rage_you_on"
            elif re.fullmatch(r"^You regain your strength\.$", line) is not None:
                return "spell_rage_of_vallon_you_off"
            elif re.fullmatch(r"^You swoonin raptured bliss\.$", line) is not None:
                return "spell_rapture_you_on"
            elif (
                re.fullmatch(
                    r"^You feel your enchantments being stripped away\.$", line
                )
                is not None
            ):
                return "spell_recant_magic_you_on"
            elif (
                re.fullmatch(
                    r"^You have been struck down by the judgement of the gods\.$", line
                )
                is not None
            ):
                return "spell_reckoning_you_on"
            elif (
                re.fullmatch(r"^You reclaim energy from your pet\.$", line) is not None
            ):
                return "spell_reclaim_energy_you_cast"
            elif (
                re.fullmatch(
                    r"^You scream as a magic force rends the skin from your body\.$",
                    line,
                )
                is not None
            ):
                return "spell_rend_you_on"
            elif re.fullmatch(r"^You feel resistant from cold\.$", line) is not None:
                return "spell_resist_cold_you_on"
            elif re.fullmatch(r"^You feel resistant from disease\.$", line) is not None:
                return "spell_resist_disease_you_on"
            elif re.fullmatch(r"^You feel resistant from fire\.$", line) is not None:
                return "spell_resist_fire_you_on"
            elif re.fullmatch(r"^You feel resistant from magic\.$", line) is not None:
                return "spell_resist_magic_you_on"
                # return "spell_resistance_to_magic_you_on"
            elif re.fullmatch(r"^You feel resistant from poison\.$", line) is not None:
                return "spell_resist_poison_you_on"
            elif re.fullmatch(r"^You feel resolute\.$", line) is not None:
                return "spell_resolution_you_on"
            elif re.fullmatch(r"^You are exhausted\.$", line) is not None:
                return "spell_resurrection_effects_you_on"
            elif (
                re.fullmatch(
                    r"^You have been struck by the wrath of the gods(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_retribution_you_on"
            elif re.fullmatch(r"^You begin to heal faster\.$", line) is not None:
                return "spell_rubicite_aura_you_on"
            elif (
                re.fullmatch(r"^You feel the spirit-scale of wolf enter you\.$", line)
                is not None
            ):
                return "spell_line_fragile_sow_you_on"
                # return "spell_scale_of_wolf_you_on"
                # return "spell_spirit_of_scale_you_on"
            elif re.fullmatch(r"^You grow scales\.$", line) is not None:
                return "spell_scale_skin_you_on"
            elif re.fullmatch(r"^You shed your scales\.$", line) is not None:
                return "spell_scale_skin_you_off"
            elif (
                re.fullmatch(r"^You smell the faint scent of darkness\.$", line)
                is not None
            ):
                return "spell_scent_of_darkness_you_on"
            elif (
                re.fullmatch(r"^You smell the faint scent of shadow\.$", line)
                is not None
            ):
                return "spell_scent_of_shadow_you_on"
            elif (
                re.fullmatch(r"^You smell the faint scent of Terris\.$", line)
                is not None
            ):
                return "spell_scent_of_terris_you_on"
            elif re.fullmatch(r"^You feel your skin melt\.$", line) is not None:
                return "spell_scoriae_you_on"
            elif (
                re.fullmatch(
                    r"^You feel a surge of strength as you let forth a loud scream\.$",
                    line,
                )
                is not None
            ):
                return "spell_screaming_mace_you_on"
            elif re.fullmatch(r"^You begin to scream\.$", line) is not None:
                return "spell_screaming_terror_you_on"
            elif re.fullmatch(r"^You stop screaming\.$", line) is not None:
                return "spell_screaming_terror_you_off"
            elif (
                re.fullmatch(r"^You are burnt by the Seeking Flame of Seukor\.$", line)
                is not None
            ):
                return "spell_seeking_flame_of_seukor_you_on"
            elif (
                re.fullmatch(r"^You feel your body filled by fury\.$", line) is not None
            ):
                return "spell_seething_fury_you_on"
            elif re.fullmatch(r"^You land\.$", line) is not None:
                return "spell_selos_song_of_travel_you_off"
            elif (
                re.fullmatch(r"^You sense that you are being watched\.$", line)
                is not None
            ):
                return "spell_sentinel_you_on"
            elif re.fullmatch(r"^You feel a shadow pass over you\.$", line) is not None:
                return "spell_shadow_vortex_you_on"
            elif re.fullmatch(r"^You become visible\.$", line) is not None:
                return "spell_shauris_sonorous_clouding_you_off"
            elif (
                re.fullmatch(
                    r"^You are surrounded by a thorny barrier of blades\.\.$", line
                )
                is not None
            ):
                return "spell_shield_of_blades_you_on"
            elif (
                re.fullmatch(r"^You are surrounded by a shield of song\.$", line)
                is not None
            ):
                return "spell_shield_of_song_you_on"
            elif re.fullmatch(r"^You are no longer shielded\.$", line) is not None:
                return "spell_shifting_shield_you_off"
            elif re.fullmatch(r"^You shift your sight\.$", line) is not None:
                return "spell_shifting_sight_you_on"
            elif (
                re.fullmatch(
                    r"^You have been lacerated(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_line_mag_shock_you_on"
                # return "spell_shock_of_blades_you_on"
                # return "spell_shock_of_spikes_you_on"
                # return "spell_shock_of_swords_you_on"
            elif (
                re.fullmatch(r"^You convulse as lightning arcs through you\.$", line)
                is not None
            ):
                return "spell_shock_of_lightning_you_on"
            elif (
                re.fullmatch(
                    r"^You feel your skin burn as poison seeps through your skin(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_shock_of_poison_you_on"
            elif (
                re.fullmatch(r"^You have been lacerated by deadly steel\.$", line)
                is not None
            ):
                return "spell_shock_of_steel_you_on"
            elif (
                re.fullmatch(
                    r"^You are blasted by static winds(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_shock_spiral_of_alkabor_you_on"
            elif re.fullmatch(r"^You are deafened\.$", line) is not None:
                return "spell_shrieking_howl_you_on"
            elif re.fullmatch(r"^You feel a gutwrenching hatred\.$", line) is not None:
                return "spell_shroud_of_hate_you_on"
            elif re.fullmatch(r"^You are no longer shrouded\.$", line) is not None:
                return "spell_shroud_of_the_spirits_you_off"
            elif re.fullmatch(r"^You feel your strength dwindle\.$", line) is not None:
                return "spell_line_siphon_strength_you_on"
                # return "spell_siphon_strength_you_on"
                # return "spell_surge_of_enfeeblement_you_on"
                # return "spell_wave_of_enfeeblement_you_on"
            elif re.fullmatch(r"^You feel your strength grow\.$", line) is not None:
                return "spell_line_siphon_strength_you_on"
                # return "spell_siphon_strength_recourse_you_on"
                # return "spell_steal_strength_you_on"
            elif (
                re.fullmatch(r"^You have been sprayed with skunk musk\.$", line)
                is not None
            ):
                return "spell_skunkspray_you_on"
            elif re.fullmatch(r"^You no longer smell of skunk\.$", line) is not None:
                return "spell_skunkspray_you_off"
            elif re.fullmatch(r"^You spray your target\.$", line) is not None:
                return "spell_skunkspray_you_cast"
            elif (
                re.fullmatch(
                    r"^You have been smitten(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_smite_you_on"
            elif (
                re.fullmatch(r"^You are captivated by the bewitching tune\.$", line)
                is not None
            ):
                return "spell_solons_bewitching_bravura_you_on"
            elif re.fullmatch(r"^You are no longer captivated\.$", line) is not None:
                return "spell_line_brd_charm_you_off"
                # return "spell_solons_bewitching_bravura_you_off"
                # return "spell_solons_song_of_the_sirens_you_off"
            elif (
                re.fullmatch(r"^You are captivated by the haunting tune\.$", line)
                is not None
            ):
                return "spell_solons_song_of_the_sirens_you_on"
            elif re.fullmatch(r"^You play the song of dawn\.$", line) is not None:
                return "spell_song_of_dawn_you_cast"
            elif re.fullmatch(r"^You are no longer terrified\.$", line) is not None:
                return "spell_song_of_midnight_you_off"
            elif (
                re.fullmatch(
                    r"^You feel the ground scream and heave(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_upheaval_you_on"
            elif re.fullmatch(r"^You hear the music of twilight\.$", line) is not None:
                return "spell_song_of_twilight_you_on"
            elif re.fullmatch(r"^You play the music of twilight\.$", line) is not None:
                return "spell_song_of_twilight_you_cast"
            elif (
                re.fullmatch(r"^You feel your soul being consumed\.$", line) is not None
            ):
                return "spell_soul_devour_you_on"
            elif (
                re.fullmatch(r"^You feel your soul draining away\.$", line) is not None
            ):
                return "spell_soul_leech_you_on"
            elif (
                re.fullmatch(r"^You feel the spirit of bear enter you\.$", line)
                is not None
            ):
                return "spell_spirit_of_bear_you_on"
            elif (
                re.fullmatch(r"^You feel the spirit of cat enter you\.$", line)
                is not None
            ):
                return "spell_spirit_of_cat_you_on"
            elif (
                re.fullmatch(r"^You feel the spirit of cheetah enter you\.\.$", line)
                is not None
            ):
                return "spell_spirit_of_cheetah_you_on"
            elif (
                re.fullmatch(r"^You feel the spirit of monkey enter you\.$", line)
                is not None
            ):
                return "spell_spirit_of_monkey_you_on"
            elif re.fullmatch(r"^You have taken root\.$", line) is not None:
                return "spell_line_dru_tree_you_on"
                # return "spell_spirit_of_oak_you_on"
                # return "spell_treeform_you_on"
            elif re.fullmatch(r"^You are no longer a tree\.$", line) is not None:
                return "spell_line_dru_tree_you_off"
                # return "spell_spirit_of_oak_you_off"
                # return "spell_treeform_you_off"
            elif (
                re.fullmatch(r"^You feel the spirit of ox enter you\.$", line)
                is not None
            ):
                return "spell_spirit_of_ox_you_on"
            elif (
                re.fullmatch(r"^You feel the spirit of snake enter you\.$", line)
                is not None
            ):
                return "spell_spirit_of_snake_you_on"
            elif re.fullmatch(r"^You summon a howling spirit\.$", line) is not None:
                return "spell_spirit_of_the_howler_you_on"
            elif re.fullmatch(r"^You feel robust\.$", line) is not None:
                return "spell_stamina_you_on"
            elif (
                re.fullmatch(r"^You feel the glare of the heavens\.$", line) is not None
            ):
                return "spell_starfire_you_on"
            elif (
                re.fullmatch(r"^You are consumed in a magic pulse\.$", line) is not None
            ):
                return "spell_static_you_on"
            elif re.fullmatch(r"^You stagger back\.$", line) is not None:
                return "spell_static_strike_you_on"
            elif re.fullmatch(r"^You spout acid\.$", line) is not None:
                return "spell_stream_of_acid_you_cast"
            elif re.fullmatch(r"^You feel strong\.$", line) is not None:
                return "spell_strength_you_on"
            elif re.fullmatch(r"^You have been Struck\.$", line) is not None:
                return "spell_strike_you_on"
            elif re.fullmatch(r"^You scream\.$", line) is not None:
                return "spell_stun_breath_you_cast"
            elif re.fullmatch(r"^You gasp for breath\.$", line) is not None:
                return "spell_suffocating_sphere_you_on"
            elif re.fullmatch(r"^You stop gasping\.$", line) is not None:
                return "spell_suffocating_sphere_you_off"
            elif (
                re.fullmatch(r"^You summon your companion to your side\.$", line)
                is not None
            ):
                return "spell_summon_companion_you_on"
            elif re.fullmatch(r"^You are blinded by a sunbeam\.$", line) is not None:
                return "spell_sunbeam_you_on"
            elif re.fullmatch(r"^You reel from a stunning blow\.$", line) is not None:
                return "spell_stunning_blow_you_on"
            elif (
                re.fullmatch(r"^You feel the pain of a million stings\.\.$", line)
                is not None
            ):
                return "spell_swarm_of_retribution_you_on"
            elif (
                re.fullmatch(
                    r"^You feel the pain unbearable pain of a thousand stings\.$", line
                )
                is not None
            ):
                return "spell_swarming_pain_you_on"
            elif (
                re.fullmatch(r"^You feel a warm aura surround you\.$", line) is not None
            ):
                return "spell_sympathetic_aura_you_on"
            elif re.fullmatch(r"^You feel at peace\.$", line) is not None:
                return "spell_symphonic_harmony_you_on"
            elif (
                re.fullmatch(r"^You feel a static pulse wash through you\.$", line)
                is not None
            ):
                return "spell_syvelians_antimagic_aria_you_on"
            elif re.fullmatch(r"^You are no longer poisoned\.$", line) is not None:
                return "spell_tainted_breath_you_off"
            elif re.fullmatch(r"^You feel tough\.$", line) is not None:
                return "spell_line_shm_hp_you_on"
                # return "spell_talisman_of_altuna_you_on"
                # return "spell_talisman_of_kragg_you_on"
                # return "spell_talisman_of_tnarg_you_on"
            elif (
                re.fullmatch(
                    r"^You have been protected by the Talisman of Jasinth\.$", line
                )
                is not None
            ):
                return "spell_talisman_of_jasinth_you_on"
            elif (
                re.fullmatch(
                    r"^You have been protected by the Talisman of Shadoo\.$", line
                )
                is not None
            ):
                return "spell_talisman_of_shadoo_you_on"
            elif (
                re.fullmatch(
                    r"^You feel the spirit of the brute channel through you\.$", line
                )
                is not None
            ):
                return "spell_talisman_of_the_brute_you_on"
            elif (
                re.fullmatch(
                    r"^You feel the spirit of the cat channel through you\.$", line
                )
                is not None
            ):
                return "spell_talisman_of_the_cat_you_on"
            elif (
                re.fullmatch(
                    r"^You feel the spirit of the raptor channel through you\.$", line
                )
                is not None
            ):
                return "spell_talisman_of_the_raptor_you_on"
            elif (
                re.fullmatch(
                    r"^You feel the spirit of the rhino channel through you\.$", line
                )
                is not None
            ):
                return "spell_talisman_of_the_rhino_you_on"
            elif (
                re.fullmatch(
                    r"^You feel the spirit of the serpent channel through you\.$", line
                )
                is not None
            ):
                return "spell_talisman_of_the_serpent_you_on"
            elif re.fullmatch(r"^You hear the barking of Tashan\.$", line) is not None:
                return "spell_tashan_you_on"
            elif (
                re.fullmatch(r"^You hear the barking of the Tashani\.$", line)
                is not None
            ):
                return "spell_line_low_tash_you_on"
                # return "spell_tashani_you_on"
                # return "spell_wind_of_tishani_you_on"
            elif (
                re.fullmatch(r"^You hear the barking of Tashania\.$", line) is not None
            ):
                return "spell_line_tash_you_on"
                # return "spell_tashanian_you_on"
                # return "spell_wind_of_tishanian_you_on"
            elif re.fullmatch(r"^You peer through the telescope\.$", line) is not None:
                return "spell_telescope_you_on"
            elif re.fullmatch(r"^You put the telescope down\.$", line) is not None:
                return "spell_telescope_you_off"
            elif (
                re.fullmatch(r"^You feel your mental energies drain away\.$", line)
                is not None
            ):
                return "spell_theft_of_thought_you_on"
            elif (
                re.fullmatch(
                    r"^You have been thunder struck(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_thunder_strike_you_on"
            elif re.fullmatch(r"^You have been thunder stunned\.$", line) is not None:
                return "spell_thunderbold_you_on"
            elif re.fullmatch(r"^You fall into a state of torpor\.$", line) is not None:
                return "spell_torpor_you_on"
            elif re.fullmatch(r"^You no longer track the dead\.$", line) is not None:
                return "spell_track_corpse_you_off"
            elif re.fullmatch(r"^You feel the ground rumble\.$", line) is not None:
                return "spell_tremor_you_on"
            elif re.fullmatch(r"^You spin to face north\.$", line) is not None:
                return "spell_true_north_you_on"
            elif (
                re.fullmatch(
                    r"^You stagger as the light of divine words enter your mind\.$",
                    line,
                )
                is not None
            ):
                return "spell_turning_of_the_unnatural_you_on"
            elif re.fullmatch(r"^You begin to chant\.$", line) is not None:
                return "spell_line_brd_tuyen_you_on"
                # return "spell_tuyens_chant_of_flame_you_on"
                # return "spell_tuyens_chant_of_frost_you_on"
            elif re.fullmatch(r"^You feel valorous\.$", line) is not None:
                return "spell_valor_you_on"
            elif (
                re.fullmatch(r"^You are blasted by the vengeance of Al\'Kabor\.$", line)
                is not None
            ):
                return "spell_vengeance_of_alkabor_you_on"
            elif (
                re.fullmatch(r"^You are struck by a sudden force\.$", line) is not None
            ):
                return "spell_verlekarnorms_disaster_you_on"
            elif re.fullmatch(r"^You summon a vigilant spirit\.$", line) is not None:
                return "spell_vigilant_spirit_you_on"
            elif (
                re.fullmatch(r"^You experience visions of grandeur\.$", line)
                is not None
            ):
                return "spell_visions_of_grandeur_you_on"
            elif (
                re.fullmatch(r"^You lose yourself in your rage and go berserk\.$", line)
                is not None
            ):
                return "spell_voice_of_the_berserker_you_on"
            elif re.fullmatch(r"^You call out to Karana\.$", line) is not None:
                return "spell_wake_of_karana_you_on"
            elif (
                re.fullmatch(r"^You forget what you were supposed to be\.$", line)
                is not None
            ):
                return "spell_wandering_mind_you_on"
            elif re.fullmatch(r"^You remember where you are\.$", line) is not None:
                return "spell_wandering_mind_you_off"
            elif (
                re.fullmatch(r"^You are singed by a wave of fire\.$", line) is not None
            ):
                return "spell_wave_of_fire_you_on"
            elif re.fullmatch(r"^You appear in a gust of wind\.$", line) is not None:
                return "spell_line_dru_skyfire_or_ej_you_on"
                # return "spell_wind_of_the_north_you_on"
                # return "spell_wind_of_the_south_you_on"
            elif (
                re.fullmatch(r"^You feel the pain of a million stings\.$", line)
                is not None
            ):
                return "spell_winged_death_you_on"
            elif (
                re.fullmatch(r"^You begin to move with wonderous rapidity\.$", line)
                is not None
            ):
                return "spell_wonderous_rapidity_you_on"
            elif (
                re.fullmatch(
                    r"^You are wracked with pain(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_line_word_you_on"
                # return "spell_word_divine_you_on"
                # return "spell_word_of_pain_you_on"
                # return "spell_word_of_shadow_you_on"
                # return "spell_word_of_souls_you_on"
                # return "spell_word_of_spirit_you_on"
            elif (
                re.fullmatch(r"^You feel the touch of Redemption\.$", line) is not None
            ):
                return "spell_word_of_redemption:_you_on"
            elif re.fullmatch(r"^You feel restored\.$", line) is not None:
                return "spell_word_of_restoration_you_on"
            elif re.fullmatch(r"^You feel vigorous\.$", line) is not None:
                return "spell_word_of_vigor_you_on"
            elif (
                re.fullmatch(
                    r"^You have been struck down by wrath(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_wrath_you_on"
            elif (
                re.fullmatch(r"^You are gripped by nature's wrath\.$", line) is not None
            ):
                return "spell_wrath_of_nature_you_on"
            elif (
                re.fullmatch(
                    r"^You feel a surge of strength as you let forth a mighty yaulp\.$",
                    line,
                )
                is not None
            ):
                return "spell_line_yaulp_you_on"
                # return "spell_yaulp_you_on"
                # return "spell_yaulp_ii_you_on"
                # return "spell_yaulp_iii_you_on"
                # return "spell_yaulp_iv_you_on"
            elif (
                re.fullmatch(r"^You have been struck by the force of Ykesha\.$", line)
                is not None
            ):
                return "spell_ykesha_you_on"
            elif re.fullmatch(r"^You call forth fire\.$", line) is not None:
                return "spell_call_of_flame_you_cast"
            elif (
                re.fullmatch(
                    r"^You stagger in pain as every bone in your body pulses\.$", line
                )
                is not None
            ):
                return "spell_denons_desperate_dirge_you_on"
            elif re.fullmatch(r"^You feel quite drowsy\.$", line) is not None:
                return "spell_kelins_lucid_lullaby_you_on"
            elif (
                re.fullmatch(
                    r"^You are seared by the basilisk's lava breath\.\.$", line
                )
                is not None
            ):
                return "spell_lava_breath_you_on"
            elif re.fullmatch(r"^You feel very vulnerable\.$", line) is not None:
                return "spell_line_malo_you_on"
                # return "spell_mala_you_on"
                # return "spell_malo_you_on"
                # return "spell_malosi_you_on"
                # return "spell_malosini_you_on"
            elif (
                re.fullmatch(r"^You are filled with maniacal strength\.$", line)
                is not None
            ):
                return "spell_maniacal_strength_you_on"
            elif (
                re.fullmatch(r"^You feel the holy wrath of nature upon you\.$", line)
                is not None
            ):
                return "spell_natures_holy_wrath_you_on"
            elif (
                re.fullmatch(
                    r"^You are covered in illusionary chainmail armor\.$", line
                )
                is not None
            ):
                return "spell_phantom_chain_you_on"
            elif (
                re.fullmatch(r"^You are covered in illusionary leather armor\.$", line)
                is not None
            ):
                return "spell_phantom_leather_you_on"
            elif (
                re.fullmatch(
                    r"^You feel an aura of vigorous protection surround you\.$", line
                )
                is not None
            ):
                return "spell_purifying_rhythms_you_on"
            elif (
                re.fullmatch(r"^You are frozen by the retribution of Al'Kabor\.$", line)
                is not None
            ):
                return "spell_retribution_of_alkabor_you_on"
            elif (
                re.fullmatch(r"^You are filled with a savage spirit\.$", line)
                is not None
            ):
                return "spell_savage_spirit_you_on"
            elif (
                re.fullmatch(r"^You smell the faint scent of dusk\.$", line) is not None
            ):
                return "spell_scent_of_dusk_you_on"

        ### Spell Specific Your
        elif re.fullmatch(r"^Your .+", line) is not None:
            if re.fullmatch(r"^Your speed returns to normal\.$", line) is not None:
                return "spell_line_haste_you_off"
                # return "spell_aanyas_quickening_you_off"
                # return "spell_blessing_of_the_grove_you_off"
                # return "spell_alacrity_you_off"
                # return "spell_celerity_you_off"
                # return "spell_haste_you_off"
                # return "spell_quickness_you_off"
                # return "spell_swift_like_the_wind_you_off"
                # return "spell_swift_spirit_you_off"
                # return "spell_wonderous_rapidity_you_off"
            elif re.fullmatch(r"^Your enchantments fade\.$", line) is not None:
                return "spell_abolish_enchantment_you_on"
            elif re.fullmatch(r"^Your knees buckle\.$", line) is not None:
                return "spell_avatar_snare_you_on"
            elif re.fullmatch(r"^Your legs regain strength\.$", line) is not None:
                return "spell_avatar_snare_you_off"
            elif re.fullmatch(r"^Your eyes tingle\.$", line) is not None:
                return "spell_line_see_invis_you_on"
                # return "spell_acumen_you_on"
                # return "spell_chill_sight_you_on"
                # return "spell_heat_sight_you_on"
                # return "spell_plainsight_you_on"
                # return "spell_see_invisible_you_on"
                # return "spell_serpent_sight_you_on"
                # return "spell_spirit_sight_you_on"
                # return "spell_ultravision_you_on"
            elif re.fullmatch(r"^Your eyes stop tingling\.$", line) is not None:
                return "spell_line_see_invis_you_off"
                # return "spell_acumen_you_off"
                # return "spell_see_invisible_you_off"
                # return "spell_spirit_sight_you_off"
            elif re.fullmatch(r"^Your grace fades\.$", line) is not None:
                return "spell_line_enc_charisma_you_off"
                # return "spell_adorning_grace_you_off"
                # return "spell_overwhelming_splendor_you_off"
            elif re.fullmatch(r"^Your aegolism fades\.$", line) is not None:
                return "spell_aegolism_you_off"
            elif re.fullmatch(r"^Your fever has broken\.$", line) is not None:
                return "spell_line_dot_disease_you_off"
                # return "spell_affliction_you_off"
                # return "spell_insidious_decay_you_off"
                # return "spell_insidious_fever_you_off"
                # return "spell_insidious_malady_you_off"
                # return "spell_plague_you_off"
                # return "spell_scourge_you_off"
                # return "spell_sebilite_pox_you_off"
                # return "spell_sicken_you_off"
            elif re.fullmatch(r"^Your agility fades\.$", line) is not None:
                return "spell_line_agility_you_off"
                # return "spell_agility_you_off"
                # return "spell_deliriously_nimble_you_off"
                # return "spell_nimble_you_off"
                # return "spell_feet_like_cat_you_off"
            elif re.fullmatch(r"^Your aura fades\.$", line) is not None:
                return "spell_line_aura_you_off"
                # return "spell_alluring_aura_you_off"
                # return "spell_psalm_of_cooling_you_off"
                # return "spell_psalm_of_mystic_shielding_you_off"
                # return "spell_psalm_of_purity_you_off"
                # return "spell_psalm_of_vitality_you_off"
                # return "spell_psalm_of_warmth_you_off"
            elif (
                re.fullmatch(r"^Your world dissolves into anarchy.$", line) is not None
            ):
                return "spell_anarchy_you_on"
            elif re.fullmatch(r"^Your life force drains away\.$", line) is not None:
                return "spell_ancient_breath_you_on"
            elif re.fullmatch(r"^Your surge of strength fades\.$", line) is not None:
                return "spell_line_strength_burst_you_off"
                # return "spell_anthem_de_arms_you_off"
                # return "spell_screaming_mace_you_off"
                # return "spell_yaulp_you_off"
                # return "spell_yaulp_ii_you_off"
                # return "spell_yaulp_iii_you_off"
                # return "spell_yaulp_iv_you_off"
            elif re.fullmatch(r"^Your flesh returns\.$", line) is not None:
                return "spell_line_nec_regen_you_off"
                # return "spell_arch_lich_you_off"
                # return "spell_call_of_bones_you_off"
                # return "spell_demi_lich_you_off"
                # return "spell_lich_you_off"
            elif re.fullmatch(r"^Your shielding fades\.$", line) is not None:
                return "spell_line_int_caster_shield_you_off"
                # return "spell_arch_shielding_you_off"
                # return "spell_greater_shielding_you_off"
                # return "spell_lesser_shielding_you_off"
                # return "spell_major_shielding_you_off"
            elif re.fullmatch(r"^Your protection fades\.$", line) is not None:
                return "spell_line_protection_you_off"
                # return "spell_armor_of_protection_you_off"
                # return "spell_nivs_melody_of_preservation_you_off"
                # return "spell_protect_you_off"
                # return "spell_group_resist_magic_you_off"
            elif (
                re.fullmatch(r"^Your spirit drifts from your body\.$", line) is not None
            ):
                return "spell_line_target_vision_you_on"
                # return "spell_assiduous_vision_you_on"
                # return "spell_vision_vision_you_on"
            elif re.fullmatch(r"^Your heart stops\.$", line) is not None:
                return "spell_asystole_you_on"
            elif re.fullmatch(r"^Your heartbeat resumes\.$", line) is not None:
                return "spell_asystole_you_off"
            elif re.fullmatch(r"^Your feet come free\.$", line) is not None:
                return "spell_line_root_you_off"
                # return "spell_atols_spectral_shackles_you_off"
                # return "spell_enstill_you_off"
                # return "spell_bonds_of_force_you_off"
                # return "spell_bonds_of_tunare_you_off"
                # return "spell_earthelementalattack_you_off"
                # return "spell_enstill_you_off"
                # return "spell_fetter_you_off"
                # return "spell_immobilize_you_off"
                # return "spell_paralyzing_earth_you_off"
                # return "spell_paralyzing_poison_i_you_off"
                # return "spell_paralyzing_poison_ii_you_off"
                # return "spell_paralyzing_poison_iii_you_off"
                # return "spell_root_you_off"
                # return "spell_vengeance_of_the_glades_you_off"
            elif re.fullmatch(r"^Your wounds begin to heal\.$", line) is not None:
                return "spell_line_hot_you_on"
                # return "spell_aura_of_marr_you_on"
                # return "spell_hymn_of_restoration_you_on"
                # return "spell_pact_of_shadow_you_on"
                # return "spell_shadow_compact_you_on"
                # return "spell_shadowbond_you_on"
            elif (
                re.fullmatch(r"^Your body screams with the power of an Avatar\.$", line)
                is not None
            ):
                return "spell_avatar_you_on"
                # return "spell_primal_avatar_you_on"
            elif (
                re.fullmatch(r"^Your veins fill with deadly poison\.$", line)
                is not None
            ):
                return "spell_bane_of_nife_you_on"
            elif re.fullmatch(r"^Your skin returns to normal\.$", line) is not None:
                return "spell_line_skin_you_off"
                # return "spell_barbcoat_you_off"
                # return "spell_bladecoat_you_off"
                # return "spell_bobbing_corpse_you_off"
                # return "spell_bramblecoat_you_off"
                # return "spell_diamondskin_you_off"
                # return "spell_leatherskin_you_off"
                # return "spell_manasink_you_off"
                # return "spell_manaskin_you_off"
                # return "spell_natureskin_you_off"
                # return "spell_protection_of_the_glades_you_off"
                # return "spell_shieldskin_you_off"
                # return "spell_skin_like_diamond_you_off"
                # return "spell_skin_like_nature_you_off"
                # return "spell_skin_like_rock_you_off"
                # return "spell_skin_like_steel_you_off"
                # return "spell_skin_like_wood_you_off"
                # return "spell_skin_of_the_shadow_you_off"
                # return "spell_spikecoat_you_off"
                # return "spell_steelskin_you_off"
                # return "spell_thistlecoat_you_off"
                # return "spell_thorncoat_you_off"
            elif (
                re.fullmatch(
                    r"^Your goggles are imbued with bursts of battery powered sight\.$",
                    line,
                )
                is not None
            ):
                return "spell_battery_vision_you_on"
            elif re.fullmatch(r"^Your magic batteries dim\.$", line) is not None:
                return "spell_battery_vision_you_off"
            elif re.fullmatch(r"^Your eyes gleam with bedlam\.$", line) is not None:
                return "spell_bedlam_you_on"
            elif re.fullmatch(r"^Your bedlam fades\.$", line) is not None:
                return "spell_bedlam_you_off"
            elif (
                re.fullmatch(r"^Your spirit screams with berserker strength\.$", line)
                is not None
            ):
                return "spell_berserker_spirit_you_on"
            elif (
                re.fullmatch(r"^Your muscles bulge with berserker strength\.$", line)
                is not None
            ):
                return "spell_berserker_strength_you_on"
            elif re.fullmatch(r"^Your sight is bound\.$", line) is not None:
                return "spell_bind_sight_you_on"
            elif re.fullmatch(r"^Your binding ends\.$", line) is not None:
                return "spell_bind_sight_you_off"
            elif re.fullmatch(r"^Your skin goes numb\.$", line) is not None:
                return "spell_blast_of_cold_you_on"
            elif (
                re.fullmatch(r"^Your body is wracked by shocks of poison\.$", line)
                is not None
            ):
                return "spell_line_shm_dis_dd_you_on"
                # return "spell_blast_of_poison_you_on"
                # return "spell_shock_of_the_tainted_you_on"
            elif (
                re.fullmatch(r"^Your body is surrounded by an aura of nature\.$", line)
                is not None
            ):
                return "spell_blessing_of_nature_you_on"
            elif re.fullmatch(r"^Your sight returns\.$", line) is not None:
                return "spell_line_blind_you_off"
                # return "spell_blinding_luminance_you_off"
                # return "spell_flash_of_light_you_off"
                # return "spell_blinding_poison_i_you_off"
                # return "spell_blinding_poison_iii_you_off"
                # return "spell_sunbeam_you_off"
            elif re.fullmatch(r"^Your eyes begin to burn\.$", line) is not None:
                return "spell_line_blinding_poison_you_on"
                # return "spell_blinding_poison_i_you_on"
                # return "spell_blinding_poison_iii_you_on"
            elif re.fullmatch(r"^Your skin shrivels\.$", line) is not None:
                return "spell_bobbing_corpse_you_on"
            elif re.fullmatch(r"^Your blood boils\.$", line) is not None:
                return "spell_boil_blood_you_on"
                # return "spell_boiling_blood_you_on"
            elif re.fullmatch(r"^Your blood cools\.$", line) is not None:
                return "spell_line_boil_blood_you_off"
                # return "spell_boil_blood_you_off"
                # return "spell_boiling_blood_you_off"
                # return "spell_heat_blood_you_off"
                # return "spell_ignite_blood_you_off"
                # return "spell_pyrocruor_you_off"
            elif re.fullmatch(r"^Your illusion fades\.$", line) is not None:
                return "spell_line_illusion_you_off"
                # return "spell_boon_of_the_garou_you_off"
                # return "spell_illusion_air_elemental_you_off"
                # return "spell_illusion_barbarian_you_off"
                # return "spell_illusion_dark_elf_you_off"
                # return "spell_illusion_dry_bone_you_off"
                # return "spell_illusion_dwarf_you_off"
                # return "spell_illusion_earth_elemental_you_off"
                # return "spell_illusion_erudite_you_off"
                # return "spell_illusion_fire_elemental_you_off"
                # return "spell_illusion_gnome_you_off"
                # return "spell_illusion_halfelf_you_off"
                # return "spell_illusion_halfling_you_off"
                # return "spell_illusion_high_elf_you_off"
                # return "spell_illusion_human_you_off"
                # return "spell_illusion_iksar_you_off"
                # return "spell_illusion_ogre_you_off"
                # return "spell_illusion_skeleton_you_off"
                # return "spell_illusion_spirit_wolf_you_off"
                # return "spell_illusion_tree_you_off"
                # return "spell_illusion_troll_you_off"
                # return "spell_illusion_water_elemental_you_off"
                # return "spell_illusion_werewolf_you_off"
                # return "spell_illusion_wood_elf_you_off"
                # return "spell_minor_illusion_you_off"
            elif re.fullmatch(r"^Your bravery fades\.$", line) is not None:
                return "spell_bravery_you_off"
            elif re.fullmatch(r"^Your mind clears\.$", line) is not None:
                return "spell_line_mind_clears_you_on"
                # return "spell_brilliance_you_on"
                # return "spell_cassindras_chant_of_clarity_you_on"
                # return "spell_envenomed_heal_you_off"
            elif re.fullmatch(r"^Your brilliance fades\.$", line) is not None:
                return "spell_brilliance_you_off"
            elif (
                re.fullmatch(r"^Your heart begins to race and you feel weaker\.$", line)
                is not None
            ):
                return "spell_line_brittle_haste_you_on"
                # return "spell_brittle_haste_ii_you_on"
                # return "spell_brittle_haste_iii_you_on"
                # return "spell_brittle_haste_iv_you_on"
            elif re.fullmatch(r"^Your skin burns\.$", line) is not None:
                return "spell_burning_vengeance_you_on"
            elif (
                re.fullmatch(
                    r"^You feel your skin singe as the Burst of Flame hits you\.$", line
                )
                is not None
            ):
                return "spell_burst_of_flame_you_on"
            elif (
                re.fullmatch(r"^Your muscles scream with strength\.$", line) is not None
            ):
                return "spell_burst_of_strength_you_on"
            elif re.fullmatch(r"^Your strength fades\.$", line) is not None:
                return "spell_line_strength_you_off"
                # return "spell_burst_of_strength_you_off"
                # return "spell_furious_strength_you_off"
                # return "spell_maniacal_strength_you_off"
                # return "spell_spirit_strength_you_off"
                # return "spell_storm_strength_you_off"
                # return "spell_strength_you_off"
                # return "spell_strength_of_earth_you_off"
                # return "spell_strength_of_stone_you_off"
                # return "spell_strength_of_the_kunzar_you_off"
                # return "spell_strengthen_you_off"
                # return "spell_tumultuous_strength_you_off"
            elif re.fullmatch(r"^Your skin blisters and burns\.$", line) is not None:
                return "spell_calefaction_you_on"
                # return "spell_fist_of_fire_you_on"
            elif re.fullmatch(r"^Your body fades away\.$", line) is not None:
                return "spell_camouflage_you_on"
            elif (
                re.fullmatch(
                    r"^Your body aches as your mind clears\. You have taken \d+ point(s|) of damage.$",
                    line,
                )
                is not None
            ):
                return "spell_line_cannibalize_you_on"
                # return "spell_cannibalize_you_on"
                # return "spell_cannibalize_ii_you_on"
                # return "spell_cannibalize_iii_you_on"
                # return "spell_cannibalize_iv_you_on"
            elif re.fullmatch(r"^Your mind begins to clear\.$", line) is not None:
                return "spell_cassindras_chorus_of_clarity_other_on"
            elif re.fullmatch(r"^Your clarity of mind fades\.$", line) is not None:
                return "spell_cassindras_chorus_of_clarity_you_on"
            elif re.fullmatch(r"^Your mind sharpens\.$", line) is not None:
                return "spell_cassindras_elegy_other_on"
            elif re.fullmatch(r"^Your insight fades\.$", line) is not None:
                return "spell_cassindras_elegy_you_on"
            elif re.fullmatch(r"^Your casting ends.$", line) is not None:
                return "spell_cast_sight_you_off"
            elif (
                re.fullmatch(
                    r"^Your blade strikes deep, shearing off a chip of bone\.$", line
                )
                is not None
            ):
                return "spell_boneshear_you_on"
            elif re.fullmatch(r"^Your sense of center fades\.$", line) is not None:
                return "spell_center_you_off"
            elif re.fullmatch(r"^Your blood resumes movement\.$", line) is not None:
                return "spell_cessation_of_cor_you_off"
            elif (
                re.fullmatch(
                    r"^Your legs lock in pain as you choke on the noxious poison(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_ceticious_cloud_you_on"
            elif re.fullmatch(r"^Your battle fury fades\.$", line) is not None:
                return "spell_chant_of_battle_you_on"
            elif (
                re.fullmatch(
                    r"^Your world goes mad as chaos flows through you\.$", line
                )
                is not None
            ):
                return "spell_chaos_flux_you_on"
            elif re.fullmatch(r"^Your brain begins to smolder\.$", line) is not None:
                return "spell_chaotic_feedback_you_on"
            elif re.fullmatch(r"^Your charisma fades\.$", line) is not None:
                return "spell_line_charisma_you_off"
                # return "spell_charisma_you_off"
                # return "spell_glamour_you_off"
                # return "spell_solons_charismatic_concord_you_off"
                # return "spell_unfailing_reverence_you_off"
            elif re.fullmatch(r"^Your ultravision fades\.$", line) is not None:
                return "spell_line_ultravision_you_off"
                # return "spell_chill_sight_you_off"
                # return "spell_ultravision_you_off"
            elif re.fullmatch(r"^Your head snaps back\.$", line) is not None:
                return "spell_line_rng_aggro_you_on"
                # return "spell_cinder_jolt_you_on"
                # return "spell_jolt_you_on"
            elif re.fullmatch(r"^Your summer haze clears\.$", line) is not None:
                return "spell_circle_of_summer_you_off"
            elif re.fullmatch(r"^Your winter haze clears\.$", line) is not None:
                return "spell_circle_of_winter_you_off"
            elif re.fullmatch(r"^Your image clouds\.$", line) is not None:
                return "spell_cloud_you_on"
            elif re.fullmatch(r"^Your mind is wracked by fear\.$", line) is not None:
                return "spell_cloud_of_fear_you_on"
            elif re.fullmatch(r"^Your cogs squeal and slow\.$", line) is not None:
                return "spell_cog_boost_you_off"
            elif re.fullmatch(r"^Your eyes begin to focus\.$", line) is not None:
                return "spell_creeping_vision_you_on"
            elif re.fullmatch(r"^Your focus fades\.$", line) is not None:
                return "spell_focus_of_spirit_you_off"
                # return "spell_creeping_vision_you_off"
            elif (
                re.fullmatch(
                    r"^Your body is consumed by the raging spirits of the land\.$", line
                )
                is not None
            ):
                return "spell_curse_of_the_spirits_you_on"
            elif re.fullmatch(r"^Your combat prowess lessens\.$", line) is not None:
                return "spell_dance_of_the_blade_you_off"
            elif re.fullmatch(r"^Your wounds disappear\.$", line) is not None:
                return "spell_dark_empathy_you_on"
            elif re.fullmatch(r"^Your vision shifts\.$", line) is not None:
                return "spell_line_infravision_you_on"
                # return "spell_deadeye_you_on"
                # return "spell_eyes_of_the_cat_you_on"
            elif re.fullmatch(r"^Your vision returns to normal\.$", line) is not None:
                return "spell_line_infravision_you_off"
                # return "spell_deadeye_you_off"
                # return "spell_eyes_of_the_cat_you_off"
            elif re.fullmatch(r"^Your dexterity fades\.$", line) is not None:
                return "spell_line_dexterity_you_off"
                # return "spell_deftness_you_off"
                # return "spell_dexterity_you_off"
                # return "spell_rising_dexterity_you_off"
            elif re.fullmatch(r"^Your magical dexterity fades\.$", line) is not None:
                return "spell_dexterous_aura_you_off"
            elif re.fullmatch(r"^Your skin becomes like diamond\.$", line) is not None:
                return "spell_diamondskin_you_on"
            elif (
                re.fullmatch(
                    r"^Your stomach begins to cramp(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_disease_cloud_you_on"
            elif re.fullmatch(r"^Your stomach feels better\.$", line) is not None:
                return "spell_disease_cloud_you_off"
            elif re.fullmatch(r"^Your body begins to rot\.$", line) is not None:
                return "spell_diseased_cloud_you_on"
            elif re.fullmatch(r"^Your invulnerability fades\.$", line) is not None:
                return "spell_line_invulnerable_you_off"
                # return "spell_divine_aura_you_off"
                # return "spell_harmshield_you_off"
                # return "spell_quivering_veil_of_xarn_you_off"
            elif re.fullmatch(r"^Your divine glory fades\.$", line) is not None:
                return "spell_divine_glory_you_off"
            elif (
                re.fullmatch(r"^Your hand begins to glow with divine might\.$", line)
                is not None
            ):
                return "spell_divine_might_you_on"
            elif re.fullmatch(r"^Your hands stop glowing\.$", line) is not None:
                return "spell_divine_might_you_off"
            elif re.fullmatch(r"^Your divine strength fades\.$", line) is not None:
                return "spell_divine_strength_you_off"
            elif re.fullmatch(r"^Your rage abates\.$", line) is not None:
                return "spell_draconic_rage_you_off"
            elif re.fullmatch(r"^Your adrenaline fades\.$", line) is not None:
                return "spell_line_npc_buff_you_off"
                # return "spell_dulsehound_you_off"
                # return "spell_graveyard_dust_you_off"
            elif re.fullmatch(r"^Your feet sink into the ground\.$", line) is not None:
                return "spell_earthelementalattack_you_on"
            elif re.fullmatch(r"^Your weakness fades\.$", line) is not None:
                return "spell_line_strength_debuff_you_off"
                # return "spell_ebbing_strength_you_off"
                # return "spell_weaken_you_off"
            elif re.fullmatch(r"^Your echinacea infusion fades\.$", line) is not None:
                return "spell_echinacea_infusion_you_off"
            elif (
                re.fullmatch(
                    r"^Your body is electrified as lightning strikes you\.$", line
                )
                is not None
            ):
                return "spell_electric_blast_you_on"
            elif re.fullmatch(r"^Your elemental armor fades\.$", line) is not None:
                return "spell_elemental_armor_you_off"
            elif (
                re.fullmatch(
                    r"^Your skin tears and melts as bolts of elemental power strike you\.$",
                    line,
                )
                is not None
            ):
                return "spell_elemental_maelstrom_you_on"
            elif re.fullmatch(r"^Your elemental shield fades\.$", line) is not None:
                return "spell_elemental_shield_you_off"
            elif re.fullmatch(r"^Your endurance to cold fades\.$", line) is not None:
                return "spell_endure_cold_you_off"
            elif re.fullmatch(r"^Your endurance to disease fades\.$", line) is not None:
                return "spell_endure_disease_you_off"
            elif re.fullmatch(r"^Your endurance to fire fades\.$", line) is not None:
                return "spell_endure_fire_you_off"
            elif re.fullmatch(r"^Your endurance to magic fades\.$", line) is not None:
                return "spell_endure_magic_you_off"
            elif re.fullmatch(r"^Your endurance to poison fades\.$", line) is not None:
                return "spell_endure_poison_you_off"
            elif (
                re.fullmatch(
                    r"^Your skin blisters as energy rains down from above\.$", line
                )
                is not None
            ):
                return "spell_energy_storm_you_on"
            elif re.fullmatch(r"^Your energy recovers\.$", line) is not None:
                return "spell_energy_sap_you_off"
            elif re.fullmatch(r"^Your strength returns\.$", line) is not None:
                return "spell_line_strength_debuff_you_off"
                # return "spell_enfeeblement_you_off"
                # return "spell_feckless_might_you_off"
                # return "spell_insipid_weakness_you_off"
                # return "spell_siphon_strength_you_off"
                # return "spell_weakness_you_off"
            elif re.fullmatch(r"^Your feet become entangled\.$", line) is not None:
                return "spell_engorging_roots_you_on"
            elif (
                re.fullmatch(
                    r"^Your feet become entwined(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_line_dru_root_you_on"
                # return "spell_engulfing_roots_you_on"
                # return "spell_ensnaring_roots_you_on"
                # return "spell_entrapping_roots_you_on"
                # return "spell_enveloping_roots_you_on"
                # return "spell_grasping_roots_you_on"
            elif re.fullmatch(r"^Your enlightenment fades\.$", line) is not None:
                return "spell_enlightenment_you_off"
            elif re.fullmatch(r"^Your feet adhere to the ground\.$", line) is not None:
                return "spell_line_root_you_on"
                # return "spell_enstill_you_on"
                # return "spell_fetter_you_on"
                # return "spell_immobilize_you_on"
                # return "spell_paralyzing_earth_you_on"
                # return "spell_root_you_on"
                # return "spell_vengeance_of_the_glades_you_on"
            elif (
                re.fullmatch(r"^Your mind reels as your body heals\.$", line)
                is not None
            ):
                return "spell_envenomed_heal_you_on"
            elif re.fullmatch(r"^Your body zings with energy\.$", line) is not None:
                return "spell_line_endurance_you_on"
                # return "spell_extinguish_fatigue_you_on"
                # return "spell_invigor_you_on"
            elif re.fullmatch(r"^Your extra eye departs\.$", line) is not None:
                return "spell_eye_of_tallon_you_off"
                # return "spell_eye_of_zomm_you_off"
            elif re.fullmatch(r"^Your mind fills with fear\.$", line) is not None:
                return "spell_line_fear_you_on"
                # return "spell_fear_you_on"
                # return "spell_inspire_fear_you_on"
                # return "spell_invoke_fear_you_on"
                # return "spell_wave_of_fear_you_on"
            elif re.fullmatch(r"^Your fist bursts into flame\.$", line) is not None:
                return "spell_firefist_you_on"
            elif re.fullmatch(r"^Your hand extinguishes\.$", line) is not None:
                return "spell_firefist_you_off"
            elif (
                re.fullmatch(
                    r"^Your skin blisters as fire rains down from above\.$", line
                )
                is not None
            ):
                return "spell_firestorm_you_on"
            elif (
                re.fullmatch(
                    r"^Your skin blisters as fire rains down from above\.\.$", line
                )
                is not None
            ):
                return "spell_lava_storm_you_on"
            elif (
                re.fullmatch(
                    r"^Your body is engulfed in a jet of flames(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_flame_jet_you_on"
            elif re.fullmatch(r"^Your skin erupts in flame\.$", line) is not None:
                return "spell_flame_of_the_efreeti_you_on"
            elif re.fullmatch(r"^Your body simmers with fury\.$", line) is not None:
                return "spell_fleeting_fury_you_on"
            elif re.fullmatch(r"^Your fury fades\.$", line) is not None:
                return "spell_line_fury_you_off"
                # return "spell_fleeting_fury_you_off"
                # return "spell_whirlwind_you_off"
            elif (
                re.fullmatch(
                    r"^Your flesh begins to rot(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_line_flesh_rot_you_on"
                # return "spell_flesh_rot_i_you_on"
                # return "spell_flesh_rot_ii_you_on"
                # return "spell_flesh_rot_iii_you_on"
                # return "spell_rotting_flesh_you_on"
            elif re.fullmatch(r"^Your speed returns\.$", line) is not None:
                return "spell_line_enc_slow_you_off"
                # return "spell_forlorn_deeds_you_off"
                # return "spell_shiftless_deeds_you_off"
                # return "spell_tepid_deeds_you_off"
            elif (
                re.fullmatch(r"^Your muscles erupt with frenzied strength\.$", line)
                is not None
            ):
                return "spell_frenzied_strength_you_on"
            elif re.fullmatch(r"^Your frenzy fades\.$", line) is not None:
                return "spell_line_berserk_you_off"
                # return "spell_frenzy_you_off"
                # return "spell_fury_you_off"
                # return "spell_voice_of_the_berserker_you_off"
            elif (
                re.fullmatch(
                    r"^Your blood freezes as you are iced by an intense cone of frost\.$",
                    line,
                )
                is not None
            ):
                return "spell_frost_you_on"
            elif (
                re.fullmatch(r"^Your body freezes as the frost hits you\.$", line)
                is not None
            ):
                return "spell_frost_breath_you_on"
            elif re.fullmatch(r"^Your fungus frenzy fades\.$", line) is not None:
                return "spell_fungus_spores_you_off"
            elif (
                re.fullmatch(
                    r"^Your skin blisters as poison rains down on you\.$", line
                )
                is not None
            ):
                return "spell_line_shm_poison_you_on"
                # return "spell_gale_of_poison_you_on"
                # return "spell_poison_storm_you_on"
            elif (
                re.fullmatch(
                    r"^Your body withers from the gangrenous touch of Zum\`uul\.$", line
                )
                is not None
            ):
                return "spell_gangrenous_touch_of_zumuul_you_on"
            elif re.fullmatch(r"^Your shadows fade\.$", line) is not None:
                return "spell_gather_shadows_you_off"
            elif (
                re.fullmatch(r"^Your mind fills with horrific visions\.$", line)
                is not None
            ):
                return "spell_gaze_you_on"
            elif re.fullmatch(r"^Your legs feel numb\.\.$", line) is not None:
                return "spell_gelatroot_you_on"
            elif re.fullmatch(r"^Your legs feel weak\.$", line) is not None:
                return "spell_ghoul_root_you_on"
            elif (
                re.fullmatch(r"^Your thoughts begin to race and flow faster\.$", line)
                is not None
            ):
                return "spell_line_enc_mana_buff_you_on"
                # return "spell_gift_of_brilliance_you_on"
                # return "spell_gift_of_insight_you_on"
                # return "spell_gift_of_magic_you_on"
            elif re.fullmatch(r"^Your gift of brilliance fades\.$", line) is not None:
                return "spell_gift_of_brilliance_you_off"
            elif re.fullmatch(r"^Your gift of insight fades\.$", line) is not None:
                return "spell_gift_of_insight_you_off"
            elif re.fullmatch(r"^Your gift of magic fades\.$", line) is not None:
                return "spell_gift_of_magic_you_off"
            elif re.fullmatch(r"^Your Karanic strength fades\.$", line) is not None:
                return "spell_girdle_of_karana_you_off"
            elif re.fullmatch(r"^Your eyes feel stronger\.$", line) is not None:
                return "spell_line_magnify_you_on"
                # return "spell_glimpse_you_on"
                # return "spell_magnify_you_on"
                # return "spell_sight_you_on"
            elif re.fullmatch(r"^Your vision fades\.$", line) is not None:
                return "spell_line_magnify_you_off"
                # return "spell_glimpse_you_off"
                # return "spell_magnify_you_off"
                # return "spell_sight_you_off"
            elif re.fullmatch(r"^Your body surges adrenaline\.$", line) is not None:
                return "spell_graveyard_dust_you_on"
            elif re.fullmatch(r"^Your armor slows\.$", line) is not None:
                return "spell_grease_injection_you_off"
            elif re.fullmatch(r"^Your image blurs\.$", line) is not None:
                return "spell_line_enc_ac_you_on"
                # return "spell_haze_you_on"
                # return "spell_mist_you_on"
            elif re.fullmatch(r"^Your health fades\.$", line) is not None:
                return "spell_line_shm_sta_you_off"
                # return "spell_health_you_off"
                # return "spell_riotous_health_you_off"
            elif (
                re.fullmatch(r"^Your heartbeat becomes irregular\.$", line) is not None
            ):
                return "spell_heart_flutter_you_on"
            elif re.fullmatch(r"^Your heartbeat steadies\.$", line) is not None:
                return "spell_heart_flutter_you_off"
            elif re.fullmatch(r"^Your blood simmers\.$", line) is not None:
                return "spell_heat_blood_you_on"
            elif re.fullmatch(r"^Your infravision fades\.$", line) is not None:
                return "spell_line_infravision_you_off"
                # return "spell_heat_sight_you_off"
                # return "spell_serpent_sight_you_off"
            elif re.fullmatch(r"^Your heroism fades\.$", line) is not None:
                return "spell_line_heroic_valor_you_off"
                # return "spell_heroic_bond_you_off"
                # return "spell_heroism_you_off"
            elif (
                re.fullmatch(r"^Your soul is assaulted by the ages\.$", line)
                is not None
            ):
                return "spell_porlos_fury_you_on"
                # return "spell_hsagras_wrath_you_on"
            elif re.fullmatch(r"^Your doll has forgotten you\.$", line) is not None:
                return "spell_hug_you_off"
            elif (
                re.fullmatch(r"^Your body is rent by freezing ice\.$", line) is not None
            ):
                return "spell_ice_rend_you_on"
            elif re.fullmatch(r"^Your skin freezes over\.$", line) is not None:
                return "spell_line_wiz_ice_you_on"
                # return "spell_ice_shock_you_on"
                # return "spell_shock_of_ice_you_on"
            elif re.fullmatch(r"^Your body freezes\.$", line) is not None:
                return "spell_ice_strike_you_on"
            elif re.fullmatch(r"^Your blood ignites\.$", line) is not None:
                return "spell_line_nec_fire_you_on"
                # return "spell_ignite_blood_you_on"
                # return "spell_pyrocruor_you_on"
            elif (
                re.fullmatch(r"^Your flesh is seared from your bones\.$", line)
                is not None
            ):
                return "spell_immolating_breath_you_on"
            elif re.fullmatch(r"^Your strength leaves you\.$", line) is not None:
                return "spell_impart_strength_you_off"
            elif re.fullmatch(r"^Your mind fills with wisdom\.$", line) is not None:
                return "spell_insight_you_on"
            elif re.fullmatch(r"^Your wisdom fades\.$", line) is not None:
                return "spell_insight_you_off"
            elif re.fullmatch(r"^Your skin stops tingling\.$", line) is not None:
                return "spell_line_invis_undead_you_off"
                # return "spell_invisibility_to_undead_you_off"
                # return "spell_invisibility_versus_undead_you_off"
                # return "spell_sunskin_you_off"
            elif re.fullmatch(r"^Your image returns\.$", line) is not None:
                return "spell_line_invis_animal_you_off"
                # return "spell_invisibility_versus_animal_you_off"
                # return "spell_invisibility_versus_animals_you_off"
            elif re.fullmatch(r"^Your inspiration fades\.$", line) is not None:
                return "spell_jonthans_inspiration_you_off"
            elif re.fullmatch(r"^[a-zA-Z`\s]+ rages\.$", line) is not None:
                return "spell_jonthans_provocation_other_on"
            elif re.fullmatch(r"^Your provocation fades\.$", line) is not None:
                return "spell_jonthans_provocation_you_off"
            elif re.fullmatch(r"^Your skin beings to steam\.$", line) is not None:
                return "spell_line_potion_ds_you_on"
                # return "spell_kilvas_skin_of_flame_you_on"
                # return "spell_scorching_skin_you_on"
            elif re.fullmatch(r"^Your skin cools down\.$", line) is not None:
                return "spell_line_potion_ds_you_off"
                # return "spell_kilvas_skin_of_flame_you_off"
                # return "spell_scorching_skin_you_off"
            elif re.fullmatch(r"^Your skin becomes like leather\.$", line) is not None:
                return "spell_leatherskin_you_on"
            elif re.fullmatch(r"^Your feet leave the ground\.$", line) is not None:
                return "spell_levitate_you_on"
                # return "spell_levitation_you_on"
            elif (
                re.fullmatch(
                    r"^Your body spasms as the lightning bolt arcs through you\.$", line
                )
                is not None
            ):
                return "spell_lightning_bolt_you_on"
            elif (
                re.fullmatch(
                    r"^Your skin blisters as lightning rains down from above\.$", line
                )
                is not None
            ):
                return "spell_lightning_storm_you_on"
            elif (
                re.fullmatch(
                    r"^Your body spasms as you are struck by lightning\.$", line
                )
                is not None
            ):
                return "spell_lightning_strike_you_on"
            elif (
                re.fullmatch(
                    r"^Your body feels frail as poison seeps in to you\.$", line
                )
                is not None
            ):
                return "spell_lower_resists_i_you_on"
            elif (
                re.fullmatch(
                    r"^Your body feels frail as poison seeps into your skin\.$", line
                )
                is not None
            ):
                return "spell_line_lower_resists_you_on"
                # return "spell_lower_resists_ii_you_on"
                # return "spell_lower_resists_iii_you_on"
                # return "spell_lower_resists_iv_you_on"
            elif re.fullmatch(r"^Your sight dulls\.$", line) is not None:
                return "spell_lyssas_veracious_concord_you_off"
            elif re.fullmatch(r"^Your mind clouds\.$", line) is not None:
                return "spell_mana_sink_you_on"
            elif (
                re.fullmatch(r"^Your skin gleams with an incandescent glow\.$", line)
                is not None
            ):
                return "spell_manaskin_you_on"
            elif (
                re.fullmatch(
                    r"^Your skin numbs as deadly mana rains down from above\.$", line
                )
                is not None
            ):
                return "spell_manastorm_you_on"
            elif (
                re.fullmatch(r"^Your skin gleams with a pure aura\.$", line) is not None
            ):
                return "spell_mark_of_karn_you_on"
            elif re.fullmatch(r"^Your features sharpen\.$", line) is not None:
                return "spell_mask_of_the_hunter_you_on"
            elif re.fullmatch(r"^Your features return to normal$", line) is not None:
                return "spell_mask_of_the_hunter_you_off"
            elif re.fullmatch(r"^Your shielding fades away\.$", line) is not None:
                return "spell_line_minor_shielding_you_off"
            elif (
                re.fullmatch(r"^Your muscles move with mortal deftness\.$", line)
                is not None
            ):
                return "spell_mortal_deftness_you_on"
            elif re.fullmatch(r"^Your deftness fades\.$", line) is not None:
                return "spell_mortal_deftness_you_off"
            elif (
                re.fullmatch(
                    r"^Your legs spasm as poison seeps through your veins\.$", line
                )
                is not None
            ):
                return "spell_line_muscle_lock_you_on"
                # return "spell_muscle_lock_i_you_on"
                # return "spell_muscle_lock_ii_you_on"
                # return "spell_muscle_lock_iii_you_on"
                # return "spell_muscle_lock_iv_you_on"
            elif re.fullmatch(r"^Your skin shimmers\.$", line) is not None:
                return "spell_line_dru_best_hp_you_on"
                # return "spell_natureskin_you_on"
                # return "spell_protection_of_the_glades_you_on"
            elif re.fullmatch(r"^Your image has been obscured\.$", line) is not None:
                return "spell_obscure_you_on"
            elif re.fullmatch(r"^Your pact has faded\.$", line) is not None:
                return "spell_line_nec_heal_you_off"
                # return "spell_pact_of_shadow_you_off"
                # return "spell_shadow_compact_you_off"
            elif re.fullmatch(r"^Your bones tingle\.$", line) is not None:
                return "spell_line_fear_undead_you_on"
                # return "spell_panic_the_dead_you_on"
                # return "spell_spook_the_dead_you_on"
            elif re.fullmatch(r"^Your illusionary armor fades\.$", line) is not None:
                return "spell_line_mag_armor_you_off"
                # return "spell_phantom_armor_you_off"
                # return "spell_phantom_chain_you_off"
                # return "spell_phantom_leather_you_off"
                # return "spell_phantom_plate_you_off"
            elif re.fullmatch(r"^Your plainsight fades\.$", line) is not None:
                return "spell_plainsight_you_off"
            elif (
                re.fullmatch(
                    r"^Your body writhes in agony as the spirits of the forest attack\.$",
                    line,
                )
                is not None
            ):
                return "spell_power_of_the_forests_you_on"
            elif (
                re.fullmatch(r"^Your skin erupts in purulent pock marks\.$", line)
                is not None
            ):
                return "spell_pox_of_bertoxxulous_you_on"
            elif re.fullmatch(r"^Your primal essence fades\.$", line) is not None:
                return "spell_primal_essence_you_off"
            elif re.fullmatch(r"^Your flesh begins to liquefy\.$", line) is not None:
                return "spell_putrefy_flesh_you_on"
            elif re.fullmatch(r"^Your radiance fades\.$", line) is not None:
                return "spell_radiant_visage_you_off"
            elif re.fullmatch(r"^Your rage ends\.$", line) is not None:
                return "spell_rage_you_off"
            elif (
                re.fullmatch(r"^Your mind is crushed by the Rage of Vallon\.$", line)
                is not None
            ):
                return "spell_rage_of_vallon_you_on"
            elif re.fullmatch(r"^Your soul stops burning\.$", line) is not None:
                return "spell_rage_of_zek_you_off"
            elif (
                re.fullmatch(r"^Your body surges with a sapping vitality\.$", line)
                is not None
            ):
                return "spell_reckless_health_you_on"
            elif re.fullmatch(r"^Your sapping vitality fades\.$", line) is not None:
                return "spell_reckless_health_you_off"
            elif (
                re.fullmatch(r"^Your muscles erupt with reckless strength\.\.$", line)
                is not None
            ):
                return "spell_reckless_strength_you_on"
            elif re.fullmatch(r"^Your wounds fade\.$", line) is not None:
                return "spell_remedy_you_on"
            elif re.fullmatch(r"^Your resist cold fades\.$", line) is not None:
                return "spell_resist_cold_you_off"
            elif re.fullmatch(r"^Your resist disease fades\.$", line) is not None:
                return "spell_resist_disease_you_off"
            elif re.fullmatch(r"^Your resist fire fades\.$", line) is not None:
                return "spell_resist_fire_you_off"
            elif re.fullmatch(r"^Your resist magic fades\.$", line) is not None:
                return "spell_resist_magic_you_off"
                # return "spell_resistance_to_magic_you_off"
            elif re.fullmatch(r"^Your resist poison fades\.$", line) is not None:
                return "spell_resist_poison_you_off"
            elif re.fullmatch(r"^Your skin shines\.$", line) is not None:
                return "spell_resistant_skin_you_on"
            elif re.fullmatch(r"^Your skin loses its luster\.$", line) is not None:
                return "spell_resistant_skin_you_off"
            elif re.fullmatch(r"^Your resolution fades\.$", line) is not None:
                return "spell_resolution_you_off"
            elif (
                re.fullmatch(r"^Your body shines with riotous health\.$", line)
                is not None
            ):
                return "spell_riotous_health_you_on"
            elif re.fullmatch(r"^Your increased healing fades\.$", line) is not None:
                return "spell_rubicite_aura_you_off"
            elif re.fullmatch(r"^Your vulnerability fades\.$", line) is not None:
                return "spell_line_malo_you_off"
                # return "spell_mala_you_off"
                # return "spell_malo_you_off"
                # return "spell_malosi_you_off"
                # return "spell_malosini_you_off"
            elif re.fullmatch(r"^Your skin blisters\.$", line) is not None:
                return "spell_sear_you_on"
            elif re.fullmatch(r"^Your feet move faster\.$", line) is not None:
                return "spell_selos_accelerando_you_on"
            elif (
                re.fullmatch(r"^Your voice binds chords into chains\.$", line)
                is not None
            ):
                return "spell_selos_consonant_chain_you_on"
            elif (
                re.fullmatch(r"^Your feet blur as they leave the ground\.$", line)
                is not None
            ):
                return "spell_selos_song_of_travel_you_on"
            elif re.fullmatch(r"^Your image fades\.$", line) is not None:
                return "spell_shade_you_on"
            elif re.fullmatch(r"^Your image fades into shadow\.$", line) is not None:
                return "spell_shadow_you_on"
            elif re.fullmatch(r"^Your shadow sight fades\.$", line) is not None:
                return "spell_shadow_sight_you_off"
            elif re.fullmatch(r"^Your pact fades\.$", line) is not None:
                return "spell_shadowbond_you_off"
            elif re.fullmatch(r"^Your skin is rent by shards\.$", line) is not None:
                return "spell_shards_of_sorrow_you_on"
            elif re.fullmatch(r"^Your shielding fades\.\.$", line) is not None:
                return "spell_shield_of_the_magi_you_off"
            elif re.fullmatch(r"^Your shifting ends\.$", line) is not None:
                return "spell_shifting_sight_you_off"
            elif (
                re.fullmatch(r"^Your skin takes on a silvery hue\.$", line) is not None
            ):
                return "spell_silver_skin_you_on"
            elif re.fullmatch(r"^Your stolen strength fades\.$", line) is not None:
                return "spell_line_siphon_strength_you_off"
                # return "spell_siphon_strength_recourse_you_off"
                # return "spell_steal_strength_you_off"
            elif (
                re.fullmatch(
                    r"^Your skin blisters as lava rains down from above\.$", line
                )
                is not None
            ):
                return "spell_sirocco_you_on"
            elif re.fullmatch(r"^Your skin turns hard as diamond\.$", line) is not None:
                return "spell_skin_like_diamond_you_on"
            elif (
                re.fullmatch(r"^Your skin shimmers with divine power\.$", line)
                is not None
            ):
                return "spell_skin_like_nature_you_on"
            elif re.fullmatch(r"^Your skin turns hard as stone\.$", line) is not None:
                return "spell_skin_like_rock_you_on"
            elif re.fullmatch(r"^Your skin turns hard as steel\.$", line) is not None:
                return "spell_skin_like_steel_you_on"
            elif re.fullmatch(r"^Your skin turns hard as wood\.$", line) is not None:
                return "spell_skin_like_wood_you_on"
            elif re.fullmatch(r"^Your skin becomes shadow\.$", line) is not None:
                return "spell_skin_of_the_shadow_you_on"
            elif (
                re.fullmatch(r"^Your body is covered in a fine mist of slime\.$", line)
                is not None
            ):
                return "spell_slime_mist_you_on"
            elif re.fullmatch(r"^Your mind snaps in terror\.$", line) is not None:
                return "spell_song_of_midnight_you_on"
            elif re.fullmatch(r"^Your fury of the sea fades\.$", line) is not None:
                return "spell_song_of_the_deep_seas_you_off"
            elif (
                re.fullmatch(
                    r"^Your body pulses with the spirit of the Shissar\.$", line
                )
                is not None
            ):
                return "spell_speed_of_the_shissar_you_on"
            elif re.fullmatch(r"^Your body slows\.$", line) is not None:
                return "spell_speed_of_the_shissar_you_off"
            elif re.fullmatch(r"^Your spiritual armor fades\.$", line) is not None:
                return "spell_spirit_armor_you_off"
            elif re.fullmatch(r"^Your body begins to splurt\.$", line) is not None:
                return "spell_splurt_you_on"
            elif re.fullmatch(r"^Your body does not splurt\.$", line) is not None:
                return "spell_splurt_you_off"
            elif re.fullmatch(r"^Your stalking probe stops\.$", line) is not None:
                return "spell_stalking_probe_you_off"
            elif (
                re.fullmatch(
                    r"^Your feet anchor to the ground as you begin to regenerate\.$",
                    line,
                )
                is not None
            ):
                return "spell_stalwart_regeneration_you_on"
            elif re.fullmatch(r"^Your stamina fades\.$", line) is not None:
                return "spell_stamina_you_off"
            elif (
                re.fullmatch(
                    r"^Your armor cranks harder as steam floods through it\.$", line
                )
                is not None
            ):
                return "spell_steam_overload_you_on"
            elif re.fullmatch(r"^Your steam overload dies out\.$", line) is not None:
                return "spell_steam_overload_you_off"
            elif re.fullmatch(r"^Your skin becomes like steel\.$", line) is not None:
                return "spell_steelskin_you_on"
            elif (
                re.fullmatch(r"^Your body is encased in solid stone\!$", line)
                is not None
            ):
                return "spell_stone_breath_you_on"
            elif (
                re.fullmatch(r"^Your body burns as the acid hits you\.$", line)
                is not None
            ):
                return "spell_stream_of_acid_you_on"
            elif (
                re.fullmatch(
                    r"^Your body is electrified as the lightning strikes you\.$", line
                )
                is not None
            ):
                return "spell_line_npc_thunder_you_on"
                # return "spell_strike_of_thunder_you_on"
                # return "spell_thunder_blast_you_on"
            elif re.fullmatch(r"^Your eardrums rupture\.$", line) is not None:
                return "spell_stun_breath_you_on"
            elif (
                re.fullmatch(
                    r"^Your body is consumed by the flames of the sun\.$", line
                )
                is not None
            ):
                return "spell_sunstrike_you_on"
            elif re.fullmatch(r"^Your sympathetic aura fades\.$", line) is not None:
                return "spell_sympathetic_aura_you_off"
            elif (
                re.fullmatch(r"^Your body spasms as poison runs through you\.$", line)
                is not None
            ):
                return "spell_system_shock_i_you_on"
            elif (
                re.fullmatch(
                    r"^Your body spasms as poison spreads through you\.$", line
                )
                is not None
            ):
                return "spell_line_system_shock_you_on"
                # return "spell_system_shock_ii_you_on"
                # return "spell_system_shock_iii_you_on"
                # return "spell_system_shock_iv_you_on"
            elif (
                re.fullmatch(
                    r"^Your body spasms as poison spreads through your body\.$", line
                )
                is not None
            ):
                return "spell_system_shock_v_you_on"
            elif re.fullmatch(r"^Your hit points fade\.$", line) is not None:
                return "spell_line_shm_hp_you_off"
                # return "spell_talisman_of_altuna_you_off"
                # return "spell_talisman_of_kragg_you_off"
                # return "spell_talisman_of_tnarg_you_off"
            elif re.fullmatch(r"^Your brute spirit fades\.$", line) is not None:
                return "spell_talisman_of_the_brute_you_off"
            elif re.fullmatch(r"^Your feline spirit fades\.$", line) is not None:
                return "spell_talisman_of_the_cat_you_off"
            elif re.fullmatch(r"^Your raptor spirit fades\.$", line) is not None:
                return "spell_talisman_of_the_raptor_you_off"
            elif re.fullmatch(r"^Your rhino spirit fades\.$", line) is not None:
                return "spell_talisman_of_the_rhino_you_off"
            elif re.fullmatch(r"^Your serpent spirit fades\.$", line) is not None:
                return "spell_talisman_of_the_serpent_you_off"
            elif (
                re.fullmatch(
                    r"^Your skin blisters as the tears of Druzzil rain down on you\.$",
                    line,
                )
                is not None
            ):
                return "spell_tears_of_druzzil_you_on"
            elif (
                re.fullmatch(
                    r"^Your skin blisters as the tears of Solusek rain down on you\.$",
                    line,
                )
                is not None
            ):
                return "spell_tears_of_solusek_you_on"
            elif re.fullmatch(r"^Your mind bleeds with wonder\.$", line) is not None:
                return "spell_the_unspoken_word_you_on"
            elif re.fullmatch(r"^Your wounds begin to burn\.$", line) is not None:
                return "spell_torment_you_on"
            elif re.fullmatch(r"^Your wounds stop burning\.$", line) is not None:
                return "spell_torment_you_off"
            elif (
                re.fullmatch(
                    r"^Your thoughts muddle from the Torment of Argli\.$", line
                )
                is not None
            ):
                return "spell_torment_of_argli_you_on"
            elif re.fullmatch(r"^Your torment has ended\.$", line) is not None:
                return "spell_torment_of_argli_you_on"
            elif (
                re.fullmatch(
                    r"^Your mind is filled by fear and terror from the shadows\.$", line
                )
                is not None
            ):
                return "spell_torment_of_shadows_you_on"
            elif re.fullmatch(r"^Your state of torpor ends\.$", line) is not None:
                return "spell_torpor_you_off"
            elif (
                re.fullmatch(
                    r"^Your skin steams and melts as poison rains down on you\.$", line
                )
                is not None
            ):
                return "spell_torrent_of_poison_you_on"
            elif (
                re.fullmatch(r"^Your lifeforce drains at the Touch of Night\.$", line)
                is not None
            ):
                return "spell_touch_of_night_you_on"
            elif re.fullmatch(r"^Your feet feel quick\.$", line) is not None:
                return "spell_travelerboots_you_on"
            elif re.fullmatch(r"^Your feet slow down\.$", line) is not None:
                return "spell_travelerboots_you_off"
            elif (
                re.fullmatch(r"^Your mind fills with trepidation\.$", line) is not None
            ):
                return "spell_trepidation_you_on"
            elif re.fullmatch(r"^Your chant ends\.$", line) is not None:
                return "spell_line_brd_tuyen_you_off"
                # return "spell_tuyens_chant_of_flame_you_off"
                # return "spell_tuyens_chant_of_frost_you_off"
            elif re.fullmatch(r"^Your image fades into the umbra\.$", line) is not None:
                return "spell_umbra_you_on"
            elif re.fullmatch(r"^Your valor fades\.$", line) is not None:
                return "spell_valor_you_off"
            elif re.fullmatch(r"^Your visions fade\.$", line) is not None:
                return "spell_visions_of_grandeur_you_off"
            elif re.fullmatch(r"^Your skin burns and crackles\.$", line) is not None:
                return "spell_wave_of_flame_you_on"
            elif (
                re.fullmatch(
                    r"^Your instincts take over as you turn aside every attack\.$", line
                )
                is not None
            ):
                return "spell_whirlwind_you_on"
            elif (
                re.fullmatch(
                    r"^Your skin ignites as wildfire courses over your body\.$", line
                )
                is not None
            ):
                return "spell_wildfire_you_on"

        ### Spell Specific The
        elif re.fullmatch(r"^The .+", line) is not None:
            if re.fullmatch(r"^The potion has worn off\.$", line) is not None:
                return "spell_line_potion_you_off"
                # return "spell_accuracy_you_off"
                # return "spell_adroitness_you_off"
                # return "spell_aura_of_antibody_you_off"
                # return "spell_aura_of_cold_you_off"
                # return "spell_aura_of_heat_you_off"
                # return "spell_aura_of_purity_you_off"
                # return "spell_cohesion_you_off"
                # return "spell_null_aura_you_off"
                # return "spell_power_you_off"
                # return "spell_stability_you_off"
                # return "spell_vigor_you_off"
            elif (
                re.fullmatch(
                    r"^The protection of the Di`Zok radiates around you\.$", line
                )
                is not None
            ):
                return "spell_aegis_of_bathezid_you_on"
            elif re.fullmatch(r"^The protection of Di`Zok fades\.$", line) is not None:
                return "spell_aegis_of_bathezid_you_off"
            elif re.fullmatch(r"^The Aegis dies down\.$", line) is not None:
                return "spell_aegis_of_ro_you_off"
            elif (
                re.fullmatch(r"^The aria lifts you into the air\.\.$", line) is not None
            ):
                return "spell_agilmentes_aria_of_eagles_you_on"
            elif re.fullmatch(r"^The aloe sweat fades\.$", line) is not None:
                return "spell_aloe_sweat_you_off"
            elif re.fullmatch(r"^The pulsing energy fades\.$", line) is not None:
                return "spell_haste_you_off"
                # return "spell_augment_you_off"
                # return "spell_augmentation_you_off"
            elif re.fullmatch(r"^The black petals drift away\.$", line) is not None:
                return "spell_aura_of_black_petals_you_off"
            elif re.fullmatch(r"^The blue petals drift away\.$", line) is not None:
                return "spell_aura_of_blue_petals_you_off"
            elif re.fullmatch(r"^The green petals drift away\.$", line) is not None:
                return "spell_aura_of_green_petals_you_off"
            elif re.fullmatch(r"^The Aura of Marr fades\.$", line) is not None:
                return "spell_aura_of_marr_you_off"
            elif re.fullmatch(r"^The red petals drift away\.$", line) is not None:
                return "spell_aura_of_red_petals_you_off"
            elif re.fullmatch(r"^The white petals drift away\.$", line) is not None:
                return "spell_aura_of_white_petals_you_off"
            elif re.fullmatch(r"^The Avatar departs\.$", line) is not None:
                return "spell_avatar_you_off"
                # return "spell_primal_avatar_you_off"
            elif re.fullmatch(r"^The poison has run its course\.$", line) is not None:
                return "spell_line_poison_you_off"
                # return "spell_bane_of_nife_you_off"
                # return "spell_dizzy_i_you_off"
                # return "spell_dizzy_ii_you_off"
                # return "spell_dizzy_iii_you_off"
                # return "spell_dizzy_iv_you_off"
                # return "spell_feeble_mind_i_you_off"
                # return "spell_feeble_mind_ii_you_off"
                # return "spell_feeble_mind_iii_you_off"
                # return "spell_feeble_mind_iv_you_off"
                # return "spell_feeble_poison_you_off"
                # return "spell_kylies_venom_you_off"
                # return "spell_deadly_poison_you_off"
                # return "spell_envenomed_bolt_you_off"
                # return "spell_envenomed_breath_you_off"
                # return "spell_froglok_poison_you_off"
                # return "spell_ikatiars_revenge_you_off"
                # return "spell_liquid_silver_i_you_off"
                # return "spell_lower_resists_i_you_off"
                # return "spell_lower_resists_ii_you_off"
                # return "spell_lower_resists_iii_you_off"
                # return "spell_lower_resists_iv_you_off"
                # return "spell_manticore_poison_you_off"
                # return "spell_muscle_lock_i_you_off"
                # return "spell_muscle_lock_ii_you_off"
                # return "spell_muscle_lock_iii_you_off"
                # return "spell_muscle_lock_iv_you_off"
                # return "spell_poison_you_off"
                # return "spell_poison_bolt_you_off"
                # return "spell_strong_poison_you_off"
                # return "spell_system_shock_i_you_off"
                # return "spell_system_shock_ii_you_off"
                # return "spell_system_shock_iii_you_off"
                # return "spell_system_shock_iv_you_off"
                # return "spell_system_shock_v_you_off"
                # return "spell_venom_of_the_snake_you_off"
                # return "spell_weak_poison_you_off"
            elif re.fullmatch(r"^The shrieking aura fades\.$", line) is not None:
                return "spell_banshee_aura_you_off"
            elif re.fullmatch(r"^The flames die down\.$", line) is not None:
                return "spell_line_fire_ds_you_off"
                # return "spell_barrier_of_combustion_you_off"
                # return "spell_boon_of_immolation_you_off"
                # return "spell_breath_of_ro_you_off"
                # return "spell_cadeau_of_flame_you_off"
                # return "spell_inferno_shield_you_off"
                # return "spell_obsidian_shatter_you_off"
                # return "spell_ros_fiery_sundering_you_off"
                # return "spell_shield_of_flame_you_off"
                # return "spell_shield_of_lava_you_off"
            elif re.fullmatch(r"^The berserker spirit fades\.", line) is not None:
                return "spell_berserker_spirit_you_off"
            elif re.fullmatch(r"^The maelstrom dissipates\.$", line) is not None:
                return "spell_barrier_of_force_you_off"
            elif re.fullmatch(r"^The aura fades\.$", line) is not None:
                return "spell_line_holy_ds_you_off"
                # return "spell_blessing_of_nature_you_off"
                # return "spell_death_pact_you_off"
                # return "spell_mark_of_karn_you_off"
            elif (
                re.fullmatch(r"^The blessing of the Blackstar surrounds you\.$", line)
                is not None
            ):
                return "spell_blessing_of_the_blackstar_you_on"
            elif re.fullmatch(r"^The power of your god fills you\.$", line) is not None:
                return "spell_blessing_of_the_theurgist_you_on"
            elif re.fullmatch(r"^The poison wears off\.$", line) is not None:
                return "spell_blood_claw_you_off"
            elif re.fullmatch(r"^The bond fades\.$", line) is not None:
                return "spell_line_nec_hp_you_off"
                # return "spell_bond_of_death_you_off"
                # return "spell_soul_bond_you_off"
                # return "spell_soul_consumption_you_off"
                # return "spell_soul_well_you_off"
            elif re.fullmatch(r"^The cool breeze fades\.$", line) is not None:
                return "spell_line_clarity_you_off"
                # return "spell_boon_of_the_clear_mind_you_off"
                # return "spell_clarity_you_off"
                # return "spell_flowing_thought_i_you_off"
                # return "spell_flowing_thought_ii_you_off"
                # return "spell_flowing_thought_iii_you_off"
                # return "spell_flowing_thought_iv_you_off"
            elif re.fullmatch(r"^The mist melts away\.$", line) is not None:
                return "spell_breath_of_the_sea_you_off"
            elif re.fullmatch(r"^The light breeze fades\.$", line) is not None:
                return "spell_breeze_you_off"
            elif re.fullmatch(r"^The portal shimmers and fades\.$", line) is not None:
                return "spell_line_group_portal_you_off"
                # return "spell_burningtouch_you_off"
                # return "spell_cazic_portal_you_off"
                # return "spell_circle_of_butcher_you_off"
                # return "spell_circle_of_cobalt_scar_you_off"
                # return "spell_circle_of_commons_you_off"
                # return "spell_circle_of_feerrott_you_off"
                # return "spell_circle_of_great_divide_you_off"
                # return "spell_circle_of_iceclad_you_off"
                # return "spell_circle_of_karana_you_off"
                # return "spell_circle_of_lavastorm_you_off"
                # return "spell_circle_of_misty_you_off"
                # return "spell_circle_of_ro_you_off"
                # return "spell_circle_of_steamfont_you_off"
                # return "spell_circle_of_the_combines_you_off"
                # return "spell_circle_of_toxxulia_you_off"
                # return "spell_circle_of_wakening_lands_you_off"
                # return "spell_cobalt_scar_portal_you_off"
                # return "spell_combine_portal_you_off"
                # return "spell_common_portal_you_off"
                # return "spell_evacuate_you_off"
                # return "spell_evacuate_fay_you_off"
                # return "spell_evacuate_nek_you_off"
                # return "spell_evacuate_north_you_off"
                # return "spell_evacuate_ro_you_off"
                # return "spell_evacuate_west_you_off"
                # return "spell_fay_portal_you_off"
                # return "spell_great_divide_portal_you_off"
                # return "spell_iceclad_portal_you_off"
                # return "spell_markars_relocation_you_off"
                # return "spell_nek_portal_you_off"
                # return "spell_ro_portal_you_off"
                # return "spell_succor_you_off"
                # return "spell_succor_butcher_you_off"
                # return "spell_succor_east_you_off"
                # return "spell_succor_lavastorm_you_off"
                # return "spell_succor_north_you_off"
                # return "spell_succor_ro_you_off"
                # return "spell_tishans_relocation_you_off"
                # return "spell_tox_portal_you_off"
                # return "spell_trakanons_touch_you_off"
                # return "spell_wakening_lands_portal_you_off"
                # return "spell_west_portal_you_off"
            elif re.fullmatch(r"^The scarab dies\.$", line) is not None:
                return "spell_burrowing_scarab_you_off"
            elif (
                re.fullmatch(
                    r"^The Call of Earth surrounds your body protectively\.$", line
                )
                is not None
            ):
                return "spell_call_of_earth_you_on"
            elif re.fullmatch(r"^The Call of Earth leaves\.$", line) is not None:
                return "spell_call_of_earth_you_off"
            elif (
                re.fullmatch(
                    r"^The Call of Sky fills your weapons with power\.\.$", line
                )
                is not None
            ):
                return "spell_call_of_sky_you_on"
            elif re.fullmatch(r"^The Call of Sky leaves\.$", line) is not None:
                return "spell_call_of_sky_you_off"
            elif (
                re.fullmatch(
                    r"^The spirit of the predator strengthens your attacks\.$", line
                )
                is not None
            ):
                return "spell_call_of_the_predator_you_on"
            elif re.fullmatch(r"^The predator's spirit departs\.$", line) is not None:
                return "spell_call_of_the_predator_you_off"
            elif re.fullmatch(r"^The quickening spirit departs\.$", line) is not None:
                return "spell_captain_nalots_quickening_you_off"
            elif re.fullmatch(r"^The celestial light fades\.$", line) is not None:
                return "spell_line_hot_you_off"
                # return "spell_celestial_cleansing_you_off"
                # return "spell_celestial_healing_you_off"
            elif (
                re.fullmatch(r"^The blood stops flowing in your veins\.$", line)
                is not None
            ):
                return "spell_cessation_of_cor_you_on"
            elif (
                re.fullmatch(r"^The chill of unlife wracks your body\.$", line)
                is not None
            ):
                return "spell_chill_of_unlife_you_on"
            elif re.fullmatch(r"^The chill subsides\.$", line) is not None:
                return "spell_chill_of_unlife_you_off"
            elif re.fullmatch(r"^The poison leaves.$", line) is not None:
                return "spell_chilling_embrace_you_off"
            elif re.fullmatch(r"^The soft breeze fades\.$", line) is not None:
                return "spell_line_clarity_ii_you_off"
                # return "spell_clarity_ii_you_off"
                # return "spell_gift_of_pure_thought_you_off"
            elif re.fullmatch(r"^The darkness fades\.$", line) is not None:
                return "spell_line_nec_snare_you_off"
                # return "spell_cascading_darkness_you_off"
                # return "spell_clinging_darkness_you_off"
                # return "spell_devouring_darkness_you_off"
                # return "spell_dooming_darkness_you_off"
                # return "spell_engulfing_darkness_you_off"
            elif (
                re.fullmatch(
                    r"^The cogs in your armor spin faster and faster and faster\.$",
                    line,
                )
                is not None
            ):
                return "spell_cog_boost_you_on"
            elif re.fullmatch(r"^The pretty colors fade\.$", line) is not None:
                return "spell_line_enc_stun_you_off"
                # return "spell_color_flux_you_off"
                # return "spell_color_slant_you_off"
                # return "spell_color_shift_you_off"
                # return "spell_color_skew_you_off"
            elif re.fullmatch(r"^The swarm departs\.$", line) is not None:
                return "spell_line_swarm_you_off"
                # return "spell_creeping_crud_you_off"
                # return "spell_drifting_death_you_off"
                # return "spell_drones_of_doom_you_off"
                # return "spell_stinging_swarm_you_off"
                # return "spell_swarm_of_retribution_you_off"
                # return "spell_swarming_pain_you_off"
                # return "spell_winged_death_you_off"
            elif re.fullmatch(r"^The spirits have subsided\.$", line) is not None:
                return "spell_curse_of_the_spirits_you_off"
            elif (
                re.fullmatch(r"^The edge of the blade sharpens your mind\.\.$", line)
                is not None
            ):
                return "spell_dance_of_the_blade_you_on"
            elif re.fullmatch(r"^The light of dawn retreats\.$", line) is not None:
                return "spell_dawncall_you_off"
            elif re.fullmatch(r"^The poison leaves\.$", line) is not None:
                return "spell_deadly_velium_poison_you_off"
            elif re.fullmatch(r"^The shield fades\.$", line) is not None:
                return "spell_desperate_hope_you_off"
            elif (
                re.fullmatch(r"^The gods have rendered you invulnerable\.$", line)
                is not None
            ):
                return "spell_divine_aura_you_on"
            elif re.fullmatch(r"^The barrier fades\.$", line) is not None:
                return "spell_divine_barrier_you_off"
            elif re.fullmatch(r"^The Divine Favor fades\.$", line) is not None:
                return "spell_divine_favor_you_off"
            elif re.fullmatch(r"^The divine flame leaves\.$", line) is not None:
                return "spell_divine_purpose_you_off"
            elif (
                re.fullmatch(
                    r"^The earth's call dulls your mind and slows your muscles\.$", line
                )
                is not None
            ):
                return "spell_earthcall_you_on"
            elif re.fullmatch(r"^The call of earth recedes\.$", line) is not None:
                return "spell_earthcall_you_off"
            elif re.fullmatch(r"^The winds sear your flesh\.$", line) is not None:
                return "spell_efreeti_fire_you_on"
            elif re.fullmatch(r"^The elemental storm departs\.$", line) is not None:
                return "spell_elemental_maelstrom_you_off"
            elif re.fullmatch(r"^The aura of protection fades\.$", line) is not None:
                return "spell_line_brd_resists_you_off"
                # return "spell_elemental_rhythms_you_off"
                # return "spell_guardian_rhythms_you_off"
                # return "spell_purifying_rhythms_you_off"
            elif re.fullmatch(r"^The roots fall from your feet\.$", line) is not None:
                return "spell_line_dru_root_you_off"
                # return "spell_engorging_roots_you_off"
                # return "spell_engulfing_roots_you_off"
                # return "spell_ensnaring_roots_you_off"
                # return "spell_entrapping_roots_you_off"
                # return "spell_enveloping_roots_you_off"
                # return "spell_grasping_roots_you_off"
            elif re.fullmatch(r"^The ice cracks\.$", line) is not None:
                return "spell_entomb_in_ice_you_off"
            elif re.fullmatch(r"^The energy flames die down\.$", line) is not None:
                return "spell_feedback_you_off"
            elif re.fullmatch(r"^The fellspine cracks\.$", line) is not None:
                return "spell_fellspine_you_off"
            elif re.fullmatch(r"^The aura  leaves you\.$", line) is not None:
                return "spell_fiery_might_you_off"
            elif re.fullmatch(r"^The pain leaves your mind\.$", line) is not None:
                return "spell_fist_of_sentience_you_off"
            elif re.fullmatch(r"^The flames die away\.$", line) is not None:
                return "spell_fixation_of_ro_you_off"
            elif re.fullmatch(r"^The flames extinguish\.$", line) is not None:
                return "spell_flame_lick_you_off"
            elif (
                re.fullmatch(r"^The spirit of the great bear blesses you\.$", line)
                is not None
            ):
                return "spell_form_of_the_great_bear_you_on"
            elif re.fullmatch(r"^The frost storm melts away\.$", line) is not None:
                return "spell_frost_storm_you_off"
            elif re.fullmatch(r"^The blessing leaves\.$", line) is not None:
                return "spell_frostreavers_blessing_you_off"
            elif re.fullmatch(r"^The pulse fades\.$", line) is not None:
                return "spell_fufils_curtailing_chant_you_off"
            elif re.fullmatch(r"^The ethereal mist disperses\.$", line) is not None:
                return "spell_garzicors_vengeance_you_off"
            elif re.fullmatch(r"^The horrific visions fade\.$", line) is not None:
                return "spell_gaze_you_off"
            elif re.fullmatch(r"^The glamour fades\.$", line) is not None:
                return "spell_glamour_of_tunare_you_off"
            elif re.fullmatch(r"^The green mist disperses\.$", line) is not None:
                return "spell_greenmist_you_on"
            elif re.fullmatch(r"^The grim aura fades\.$", line) is not None:
                return "spell_grim_aura_you_off"
            elif (
                re.fullmatch(
                    r"^The protective presence of a guardian spirit surrounds you\.$",
                    line,
                )
                is not None
            ):
                return "spell_guardian_you_on"
            elif (
                re.fullmatch(
                    r"^The voice of the Harpy drains your will to fight\.$", line
                )
                is not None
            ):
                return "spell_harpy_voice_you_on"
            elif re.fullmatch(r"^The shards depart\.$", line) is not None:
                return "spell_ice_breath_you_off"
            elif re.fullmatch(r"^The flames are extinguished\.$", line) is not None:
                return "spell_immolate_you_off"
            elif (
                re.fullmatch(r"^The bile wells up in your throat\.$", line) is not None
            ):
                return "spell_infectious_cloud_you_on"
            elif re.fullmatch(r"^The inner fire fades\.$", line) is not None:
                return "spell_inner_fire_you_off"
            elif re.fullmatch(r"^The strands of fade away\.$", line) is not None:
                return "spell_largos_absonant_binding_you_off"
            elif re.fullmatch(r"^The strands fade away.\¦$", line) is not None:
                return "spell_line_brd_strands_fade_you_off"
                # return "spell_largos_melodic_binding_you_off"
                # return "spell_lyssas_solidarity_of_vision_you_off"
            elif re.fullmatch(r"^The brambles fall away\.$", line) is not None:
                return "spell_line_dru_ds_you_off"
                # return "spell_legacy_of_spike_you_off"
                # return "spell_legacy_of_thorn_you_off"
                # return "spell_shield_of_barbs_you_off"
                # return "spell_shield_of_brambles_you_off"
                # return "spell_shield_of_spikes_you_off"
                # return "spell_shield_of_thistles_you_off"
                # return "spell_shield_of_thorns_you_off"
                # return "spell_thorny_shield_you_off"
            elif (
                re.fullmatch(
                    r"^The drake's breath showers you in painful sparks\.$", line
                )
                is not None
            ):
                return "spell_lightning_breath_you_on"
            elif (
                re.fullmatch(r"^The liquid silver burns your body\.$", line) is not None
            ):
                return "spell_line_liquid_silver_you_on"
                # return "spell_liquid_silver_ii_you_on"
                # return "spell_liquid_silver_iii_you_on"
            elif re.fullmatch(r"^The malevolent grasp fades\.$", line) is not None:
                return "spell_malevolent_grasp_you_off"
            elif re.fullmatch(r"^The orbs fade away\.$", line) is not None:
                return "spell_mana_flare_you_off"
            elif re.fullmatch(r"^The mellifluous melody fades\.$", line) is not None:
                return "spell_melanies_mellifluous_motion_you_off"
            elif re.fullmatch(r"^The inspiration fades\.$", line) is not None:
                return "spell_melody_of_ervaj_you_off"
            elif re.fullmatch(r"^The cloud departs\.$", line) is not None:
                return "spell_mind_cloud_you_off"
            elif re.fullmatch(r"^The mana infusion fades\.$", line) is not None:
                return "spell_mystic_precision_you_off"
            elif re.fullmatch(r"^The mystic symbol fades\.$", line) is not None:
                return "spell_naltrons_mark_you_off"
            elif (
                re.fullmatch(r"^The melody of nature strengthens your arms\.\.$", line)
                is not None
            ):
                return "spell_natures_melody_other_on"
            elif (
                re.fullmatch(r"^The melody of nature leaves your arms\.$", line)
                is not None
            ):
                return "spell_natures_melody_you_on"
            elif re.fullmatch(r"^The harmony surrounds you\.$", line) is not None:
                return "spell_nivs_harmonic_you_on"
            elif re.fullmatch(r"^The harmony fades\.$", line) is not None:
                return "spell_nivs_harmonic_you_off"
            elif re.fullmatch(r"^The radiation fades\.$", line) is not None:
                return "spell_line_wiz_ds_you_off"
                # return "spell_okeils_flickering_flame_you_off"
                # return "spell_okeils_radiation_you_off"
            elif re.fullmatch(r"^The spirit of wolf leaves you\.$", line) is not None:
                return "spell_spirit_of_wolf_you_off"
                # return "spell_pack_spirit_you_off"
            elif re.fullmatch(r"^The pox has run its course\.$", line) is not None:
                return "spell_pox_of_bertoxxulous_you_off"
            elif re.fullmatch(r"^The blue light fades\.$", line) is not None:
                return "spell_prime_healers_blessing_you_off"
            elif (
                re.fullmatch(r"^The Rage of Tallon guides your sword\.$", line)
                is not None
            ):
                return "spell_rage_of_tallon_you_on"
            elif (
                re.fullmatch(r"^The chaos of war consumes your soul\.$", line)
                is not None
            ):
                return "spell_rage_of_zek_you_on"
            elif re.fullmatch(r"^The rapture fades\.$", line) is not None:
                return "spell_rapture_you_off"
            elif re.fullmatch(r"^The shimmer of runes fade\.$", line) is not None:
                return "spell_line_rune_you_off"
                # return "spell_rune_i_you_off"
                # return "spell_rune_ii_you_off"
                # return "spell_rune_iii_you_off"
                # return "spell_rune_iv_you_off"
                # return "spell_rune_v_you_off"
            elif (
                re.fullmatch(r"^The spirit departs leaving you drained\.$", line)
                is not None
            ):
                return "spell_savage_spirit_you_off"
            elif re.fullmatch(r"^The spirit of scale leaves you\.$", line) is not None:
                return "spell_scale_of_wolf_you_off"
            elif re.fullmatch(r"^The scarabs die\.\.$", line) is not None:
                return "spell_scarab_storm_you_off"
            elif re.fullmatch(r"^The Scars of Sigil burn you\.$", line) is not None:
                return "spell_scars_of_sigil_you_on"
            elif re.fullmatch(r"^The scent of darkness fades\.$", line) is not None:
                return "spell_scent_of_darkness_you_off"
            elif re.fullmatch(r"^The scent of dusk fades\.$", line) is not None:
                return "spell_scent_of_dusk_you_off"
            elif re.fullmatch(r"^The scent of shadow fades\.$", line) is not None:
                return "spell_scent_of_shadow_you_off"
            elif re.fullmatch(r"^The scent of Terris fades\.$", line) is not None:
                return "spell_scent_of_terris_you_off"
            elif re.fullmatch(r"^The blistering stops\.$", line) is not None:
                return "spell_sear_you_off"
            elif re.fullmatch(r"^The fury fades\.$", line) is not None:
                return "spell_seething_fury_you_off"
            elif re.fullmatch(r"^The strands fade\.$", line) is not None:
                return "spell_selos_assonant_strane_you_off"
            elif re.fullmatch(r"^The chains disappear\.$", line) is not None:
                return "spell_selos_chords_of_cessation_you_off"
            elif re.fullmatch(r"^The musical chains fade\.$", line) is not None:
                return "spell_selos_consonant_chain_you_off"
            elif re.fullmatch(r"^The shadows fade\.$", line) is not None:
                return "spell_shadow_sight_you_on"
            elif re.fullmatch(r"^The vortex of shadows fades\.$", line) is not None:
                return "spell_shadow_vortex_you_off"
            elif re.fullmatch(r"^The blades fall away\.$", line) is not None:
                return "spell_shield_of_blades_you_off"
            elif re.fullmatch(r"^The hatred departs\.$", line) is not None:
                return "spell_shroud_of_hate_you_off"
            elif re.fullmatch(r"^The pain subsides\.$", line) is not None:
                return "spell_shroud_of_pain_you_off"
            elif re.fullmatch(r"^The silvery hue fades\.$", line) is not None:
                return "spell_silver_skin_you_off"
            elif (
                re.fullmatch(r"^The fury of the deep see fills your arms\.$", line)
                is not None
            ):
                return "spell_song_of_the_deep_seas_you_on"
            elif re.fullmatch(r"^The spirit of bear leaves you\.$", line) is not None:
                return "spell_spirit_of_bear_you_off"
            elif re.fullmatch(r"^The spirit of cat leaves you\.$", line) is not None:
                return "spell_spirit_of_cat_you_off"
            elif re.fullmatch(r"^The spirit of cheetah fades\.$", line) is not None:
                return "spell_spirit_of_cheetah_you_off"
            elif re.fullmatch(r"^The spirit of monkey leaves\.$", line) is not None:
                return "spell_spirit_of_monkey_you_off"
            elif re.fullmatch(r"^The spirit of ox leaves you$", line) is not None:
                return "spell_spirit_of_ox_you_off"
            elif re.fullmatch(r"^The spirit of scale leaves you$", line) is not None:
                return "spell_spirit_of_scale_you_off"
            elif re.fullmatch(r"^The spirit of snake leaves you$", line) is not None:
                return "spell_spirit_of_snake_you_off"
            elif re.fullmatch(r"^The Talisman fades\.$", line) is not None:
                return "spell_line_shm_dr_you_off"
                # return "spell_talisman_of_jasinth_you_off"
                # return "spell_talisman_of_shadoo_you_off"
            elif re.fullmatch(r"^The air crackles around you\.$", line) is not None:
                return "spell_taper_enchantment_you_on"
            elif re.fullmatch(r"^The bubbles disappear\.$", line) is not None:
                return "spell_tarews_aquatic_ayre_you_off"
            elif re.fullmatch(r"^The barking fades\.$", line) is not None:
                return "spell_line_tash_you_off"
                # return "spell_tashan_you_off"
                # return "spell_tashani_you_off"
                # return "spell_tashania_you_off"
                # return "spell_tashanian_you_off"
                # return "spell_wind_of_tishani_you_off"
                # return "spell_wind_of_tishanian_you_off"
            elif (
                re.fullmatch(
                    r"^The justice of Dain Frostreaver casts you into the pit\.$", line
                )
                is not None
            ):
                return "spell_the_dains_justice_you_on"
            elif re.fullmatch(r"^The shadows release your mind\.$", line) is not None:
                return "spell_torment_of_shadows_you_off"
            elif re.fullmatch(r"^The trepidation fades\.$", line) is not None:
                return "spell_trepidation_you_off"
            elif re.fullmatch(r"^The words soften\.$", line) is not None:
                return "spell_turning_of_the_unnatural_you_off"
            elif re.fullmatch(r"^The Mordinia fades\.$", line) is not None:
                return "spell_vexing_mordinia_you_off"
            elif re.fullmatch(r"^The wrath of nature recedes\.$", line) is not None:
                return "spell_wrath_of_nature_you_off"

        ### Spell Specific A
        elif re.fullmatch(r"^A .+", line) is not None:
            if (
                re.fullmatch(
                    r"^A burst of strength surges through your body\.\.$", line
                )
                is not None
            ):
                return "spell_anthem_de_arms_you_on"
            elif re.fullmatch(r"^A shrieking aura surrounds you\.$", line) is not None:
                return "spell_banshee_aura_you_on"
            elif (
                re.fullmatch(r"^A stream of fire washes over you\.$", line) is not None
            ):
                return "spell_line_bolt_of_flame_you_on"
                # return "spell_bolt_of_flame_you_on"
                # return "spell_cinder_bolt_you_on"
                # return "spell_fire_bolt_you_on"
                # return "spell_flame_bolt_you_on"
                # return "spell_lava_bolt_you_on"
            elif (
                re.fullmatch(r"^A cool breeze slips through your mind\.$", line)
                is not None
            ):
                return "spell_line_clarity_you_on"
                # return "spell_boon_of_the_clear_mind_you_on"
                # return "spell_clarity_you_on"
                # return "spell_flowing_thought_i_you_on"
                # return "spell_flowing_thought_ii_you_on"
                # return "spell_flowing_thought_iii_you_on"
                # return "spell_flowing_thought_iv_you_on"
            elif (
                re.fullmatch(r"^A light breeze slips through your mind\.$", line)
                is not None
            ):
                return "spell_breeze_you_on"
            elif re.fullmatch(r"^A bulwark of faith engulfs you\.$", line) is not None:
                return "spell_bulwark_of_faith_you_on"
            elif (
                re.fullmatch(r"^A scarab burrows into your flesh\.$", line) is not None
            ):
                return "spell_burrowing_scarab_you_on"
            elif (
                re.fullmatch(r"^A concussion of air knocks you backwards\.$", line)
                is not None
            ):
                return "spell_call_of_sky_strike_you_on"
            elif (
                re.fullmatch(
                    r"^A malevolent force drags you across physical space\!$", line
                )
                is not None
            ):
                return "spell_call_of_the_zero_you_on"
            elif (
                re.fullmatch(r"^A soft breeze slips through your mind(\.|)\.$", line)
                is not None
            ):
                return "spell_line_clarity_ii_you_on"
                # return "spell_clarity_ii_you_on"
                # return "spell_gift_of_pure_thought_you_on"
            elif (
                re.fullmatch(r"^A globe of Cold Light forms in your hand\.$", line)
                is not None
            ):
                return "spell_coldlight_you_on"
            elif (
                re.fullmatch(
                    r"^A song of inspiration fills your weapon arm with strength\.$",
                    line,
                )
                is not None
            ):
                return "spell_line_brd_haste_you_on"
                # return "spell_composition_of_ervaj_you_on"
                # return "spell_melody_of_ervaj_you_on"
            elif (
                re.fullmatch(r"^A foreign surge of mana refreshes your mind\.$", line)
                is not None
            ):
                return "spell_line_nec_twitch_you_on"
                # return "spell_covetous_subversion_you_on"
                # return "spell_rapacious_subversion_you_on"
                # return "spell_sedulous_subversion_you_on"
            elif (
                re.fullmatch(r"^A swarm of fireflies shimmer around your hand\.$", line)
                is not None
            ):
                return "spell_dance_of_the_fireflies_you_on"
            elif (
                re.fullmatch(r"^A flickering shield surrounds you\.$", line) is not None
            ):
                return "spell_desperate_hope_you_on"
            elif (
                re.fullmatch(r"^A flame of divine purpose compels you\.$", line)
                is not None
            ):
                return "spell_divine_purpose_you_on"
            elif (
                re.fullmatch(r"^A fellspine digs into your flesh painfully\.$", line)
                is not None
            ):
                return "spell_fellspine_you_on"
            elif (
                re.fullmatch(r"^A flame of divine light erupts around you\.$", line)
                is not None
            ):
                return "spell_flame_of_light_you_on"
            elif (
                re.fullmatch(r"^A flurry of attacks assaults you\.$", line) is not None
            ):
                return "spell_flurry_you_on"
            elif (
                re.fullmatch(
                    r"^A small piece of your soul is sucked out of you\.$", line
                )
                is not None
            ):
                return "spell_gift_of_aerr_you_on"
            elif re.fullmatch(r"^A dull aura covers your hand\.$", line) is not None:
                return "spell_grim_aura_you_on"
            elif (
                re.fullmatch(r"^A Halo of Light solidifies in your hand\.$", line)
                is not None
            ):
                return "spell_halo_of_light_you_on"
            elif (
                re.fullmatch(r"^A magical hammer appears in your hand\.$", line)
                is not None
            ):
                return "spell_line_hammer_you_on"
                # return "spell_hammer_of_requital_you_on"
                # return "spell_hammer_of_striking_you_on"
                # return "spell_hammer_of_wrath_you_on"
            elif (
                re.fullmatch(r"^A static pulse slams through you\.$", line) is not None
            ):
                return "spell_jylls_static_pulse_you_on"
            elif (
                re.fullmatch(r"^A wave of heat screams through you\.$", line)
                is not None
            ):
                return "spell_jylls_wave_of_heat_you_on"
            elif (
                re.fullmatch(r"^A zephyr of ice tears through you\.$", line) is not None
            ):
                return "spell_jylls_zephyr_of_ice_you_on"
            elif (
                re.fullmatch(
                    r"^A massive force knocks you backwards(.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_knockback_you_on"
            elif (
                re.fullmatch(r"^A tune pervades your mind and beckons you\.$", line)
                is not None
            ):
                return "spell_lyssas_locating_lyric_other_on"
            elif (
                re.fullmatch(r"^A silvery force slicks your skin\.$", line) is not None
            ):
                return "spell_manasink_you_on"
            elif (
                re.fullmatch(r"^A mellifluous melody sweeps you away\.$", line)
                is not None
            ):
                return "spell_melanies_mellifluous_motion_you_on"
            elif re.fullmatch(r"^A cloud of pain covers you\.$", line) is not None:
                return "spell_mind_cloud_you_on"
            elif (
                re.fullmatch(
                    r"^A precise infusion of mana energy sharpens your armors movement$",
                    line,
                )
                is not None
            ):
                return "spell_mystic_precision_you_on"
            elif (
                re.fullmatch(r"^A mystic symbol flashes before your eyes\.$", line)
                is not None
            ):
                return "spell_naltrons_mark_you_on"
            elif (
                re.fullmatch(r"^A green mist seeps in to your skin\.$", line)
                is not None
            ):
                return "spell_poison_breath_you_on"
            elif (
                re.fullmatch(r"^A protective aura settles over you\.$", line)
                is not None
            ):
                return "spell_protect_you_on"
            elif (
                re.fullmatch(r"^A light shimmer of runes surround you\.$", line)
                is not None
            ):
                return "spell_rune_i_you_on"
            elif re.fullmatch(r"^A shimmer of runes surround you\.$", line) is not None:
                return "spell_rune_ii_you_on"
            elif (
                re.fullmatch(r"^A dark shimmer of runes surround you\.$", line)
                is not None
            ):
                return "spell_rune_iii_you_on"
            elif (
                re.fullmatch(r"^A coat of shimmering runes surround you\.$", line)
                is not None
            ):
                return "spell_line_rune_you_on"
                # return "spell_rune_iv_you_on"
                # return "spell_rune_v_you_on"
            elif re.fullmatch(r"^A soft mist surrounds you\.$", line) is not None:
                return "spell_shauris_sonorous_clouding_you_on"
            elif (
                re.fullmatch(r"^A mystic force shields your skin\.$", line) is not None
            ):
                return "spell_shieldskin_you_on"
            elif (
                re.fullmatch(r"^A shifting spirit shield surrounds you\.$", line)
                is not None
            ):
                return "spell_shifting_shield_you_on"
            elif (
                re.fullmatch(
                    r"^A nimbus of deathly darkness covers your hands\.$", line
                )
                is not None
            ):
                return "spell_shroud_of_death_you_on"
            elif (
                re.fullmatch(r"^A seething mass of darkness engulfs you\.$", line)
                is not None
            ):
                return "spell_shroud_of_pain_you_on"
            elif (
                re.fullmatch(r"^A protective spirit shroud cloaks you\.$", line)
                is not None
            ):
                return "spell_shroud_of_the_spirits_you_on"
            elif (
                re.fullmatch(r"^A nimbus of deathly darkness covers your body\.$", line)
                is not None
            ):
                return "spell_shroud_of_undeath_you_on"
            elif (
                re.fullmatch(r"^A globe of stars form within your hands\.$", line)
                is not None
            ):
                return "spell_starshine_you_on"
            elif (
                re.fullmatch(r"^A swirling orb of elements forms in your hand\.$", line)
                is not None
            ):
                return "spell_summon_orb_you_on"
            elif re.fullmatch(r"^A wisp settles into your hand\.$", line) is not None:
                return "spell_summon_wisp_you_on"
            elif (
                re.fullmatch(r"^A clap of thunder fills your ears\.$", line) is not None
            ):
                return "spell_thunderclap_you_on"
            elif (
                re.fullmatch(
                    r"^A blast of acid eats at your skin(\.  You have taken \d+ point(s|) of damage|)\.$",
                    line,
                )
                is not None
            ):
                return "spell_torbas_acid_blast_you_on"
            elif re.fullmatch(r"^A tsunami crushes you\.$", line) is not None:
                return "spell_tsunami_you_on"
            elif (
                re.fullmatch(r"^A blast of cold freezes your skin\.$", line) is not None
            ):
                return "spell_wave_of_cold_you_on"
            elif (
                re.fullmatch(r"^A wave of healing washes over you\.$", line) is not None
            ):
                return "spell_wave_of_healing_you_on"
            elif (
                re.fullmatch(
                    r"^A blast of heat sears your flesh(  You have taken \d+ point(s|) of damage\.|)",
                    line,
                )
                is not None
            ):
                return "spell_wave_of_heat_you_on"
            elif re.fullmatch(r"^A wave crushes you\.$", line) is not None:
                return "spell_waves_of_the_deep_sea_you_on"

        if re.fullmatch(r"^An aegis of faith engulfs you\.$", line) is not None:
            return "spell_aegis_you_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ beams a smile at [a-zA-Z`\s]+$", line)
            is not None
        ):
            return "spell_flavor_nec_hp"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ \'s knees buckle\.$", line) is not None:
            return "spell_avatar_snare_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ experiences a quickening\.$", line) is not None
        ):
            return "spell_aanyas_quickening_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s enchantments fades\.$", line) is not None:
            return "spell_abolish_enchantment_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ drinks a potion\.$", line) is not None:
            return "spell_line_potion_other_on"
            # return "spell_accuracy_other_on"
            # return "spell_adroitness_other_on"
            # return "spell_aura_of_antibody_other_on"
            # return "spell_aura_of_cold_other_on"
            # return "spell_aura_of_heat_other_on"
            # return "spell_aura_of_purity_other_on"
            # return "spell_cohesion_other_on"
            # return "spell_null_aura_other_on"
            # return "spell_power_other_on"
            # return "spell_stability_other_on"
            # return "spell_vigor_other_on"
        elif (
            re.fullmatch(
                r"^Acid begins to eat at your flesh(\.  You have taken \d+ point(s|) of damage|)\.$",
                line,
            )
            is not None
        ):
            return "spell_acid_jet_you_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ breathes a jet of acid\.$", line) is not None:
            return "spell_acid_jet_other_casts"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s eyes tingle\.$", line) is not None:
            return "spell_line_see_invis_other_on"
            # return "spell_acumen_other_on"
            # return "spell_spirit_sight_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is adorned by an aura of radiant grace\.$", line
            )
            is not None
        ):
            return "spell_adorning_grace_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is shielded behind an aegis of pure faith\.$", line
            )
            is not None
        ):
            return "spell_aegis_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ radiates with the protection of Di`Zok\.$", line
            )
            is not None
        ):
            return "spell_aegis_of_bathezid_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is enveloped by the Aegis of Ro\.$", line)
            is not None
        ):
            return "spell_aegis_of_ro_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s eye gleams with the power of Aegolism\.$", line
            )
            is not None
        ):
            return "spell_aegolism_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ sweats and shivers\, looking feverish\.$", line
            )
            is not None
        ):
            return "spell_line_dot_disease_other_on"
            # return "spell_affliction_other_on"
            # return "spell_insidious_decay_other_on"
            # return "spell_insidious_fever_other_on"
            # return "spell_insidious_malady_other_on"
            # return "spell_plague_other_on"
            # return "spell_scourge_other_on"
            # return "spell_sebilite_pox_other_on"
            # return "spell_sicken_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks agile\.$", line) is not None:
            return "spell_line_agility_other_on"
            # return "spell_agility_other_on"
            # return "spell_talisman_of_the_cat_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ is lifted into the air\.$", line) is not None:
            return "spell_agilmentes_aria_of_eagles_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ feels much faster\.$", line) is not None:
            return "spell_line_haste_other_on"
            # return "spell_alacrity_other_on"
            # return "spell_celerity_other_on"
            # return "spell_quickness_other_on"
            # return "spell_swift_like_the_wind_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks friendly\.$", line) is not None:
            return "spell_line_faction_increase_other_on"
            # return "spell_alliance_other_on"
            # return "spell_benevolence_other_on"
            # return "spell_collaboration_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks sick\.$", line) is not None:
            return "spell_line_low_nec_mana_regen_other_on"
            # return "spell_allure_of_death_other_on"
            # return "spell_dark_pact_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ blinks\.$", line) is not None:
            return "spell_line_charm_other_on"
            # return "spell_allure_of_the_wild_other_on"
            # return "spell_befriend_animal_other_on"
            # return "spell_beguile_animals_other_on"
            # return "spell_beguile_plants_other_on"
            # return "spell_call_of_karana_other_on"
            # return "spell_charm_animals_other_on"
            # return "spell_tunares_request_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is surrounded by an alluring aura\.$", line)
            is not None
        ):
            return "spell_alluring_aura_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ begins to sweat aloe\.$", line) is not None:
            return "spell_aloe_sweat_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ creates a shimmering dimensional portal\.$", line
            )
            is not None
        ):
            return "spell_line_wiz_plane_port_other_on"
            # return "spell_alter_plane_hate_other_on"
            # return "spell_alter_plane_sky_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s world dissolves into anarchy\.$", line)
            is not None
        ):
            return "spell_anarchy_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ rises from the dead\.$", line) is not None:
            return "spell_line_nec_pet_other_on"
            # return "spell_animate_dead_other_on"
            # return "spell_bone_walk_other_on"
            # return "spell_cackling_bones_other_on"
            # return "spell_cavorting_bones_other_on"
            # return "spell_convoke_shadow_other_on"
            # return "spell_haunting_corpse_other_on"
            # return "spell_invoke_death_other_on"
            # return "spell_invoke_shadow_other_on"
            # return "spell_leering_corpse_other_on"
            # return "spell_minion_of_shadows_other_on"
            # return "spell_restless_bones_other_on"
            # return "spell_servant_of_bones_other_on"
            # return "spell_summon_dead_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ feels annulled\.$", line) is not None:
            return "spell_annul_magic_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ shrinks\.$", line) is not None:
            return "spell_line_shrink_other_on"
            # return "spell_ant_legs_other_on"
            # return "spell_shrink_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s skin peels away\.$", line) is not None:
            return "spell_line_nec_regen_other_on"
            # return "spell_arch_lich_other_on"
            # return "spell_call_of_bones_other_on"
            # return "spell_demi_lich_other_on"
            # return "spell_lich_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ feels the favor of the gods upon them\.$", line
            )
            is not None
        ):
            return "spell_line_holy_armor_other_on"
            # return "spell_armor_of_faith_other_on"
            # return "spell_guard_other_on"
            # return "spell_holy_armor_other_on"
            # return "spell_shield_of_words_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks protected\.$", line) is not None:
            return "spell_armor_of_protection_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ begins to choke\.$", line) is not None:
            return "spell_line_dot_enc_other_on"
            # return "spell_asphyxiate_other_on"
            # return "spell_choke_other_on"
            # return "spell_gasping_embrace_other_on"
            # return "spell_shallow_breath_other_on"
            # return "spell_suffocate_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s eyes shimmer\.$", line) is not None:
            return "spell_line_target_vision_other_on"
            # return "spell_assiduous_vision_other_on"
            # return "spell_sight_graft_other_on"
            # return "spell_vision_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ clutches their chest\.$", line) is not None:
            return "spell_dot_nec_heart_other_on"
            # return "spell_asystole_other_on"
            # return "spell_heart_flutter_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s feet are shackled to the ground\.$", line)
            is not None
        ):
            return "spell_atols_spectral_shackles_other_on"
        elif (
            re.fullmatch(r"^Spectral shackles bind your feet to the ground\.$", line)
            is not None
        ):
            return "spell_atols_spectral_shackles_you_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ calms down\.$", line) is not None:
            return "spell_atone_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s body pulses with energy\.$", line)
            is not None
        ):
            return "spell_line_haste_other_on"
            # return "spell_augment_other_on"
            # return "spell_augmentation_other_on"
            # return "spell_inner_fire_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s eyes gleam with madness\.$", line)
            is not None
        ):
            return "spell_line_nec_haste_other_on"
            # return "spell_augment_death_other_on"
            # return "spell_augmentation_of_death_other_on"
            # return "spell_intensify_death_other_on"
            # return "spell_strengthen_death_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ begins to regenerate\.$", line) is not None:
            return "spell_line_regen_other_on"
            # return "spell_aura_of_battle_other_on"
            # return "spell_chloroplast_other_on"
            # return "spell_extended_regeneration_other_on"
            # return "spell_pack_chloroplast_other_on"
            # return "spell_pack_regeneration_other_on"
            # return "spell_regeneration_other_on"
            # return "spell_regrowth_other_on"
            # return "spell_regrowth_of_the_grove_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is covered by an aura of black petals\.$", line
            )
            is not None
        ):
            return "spell_aura_of_black_petals_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is covered by an aura of blue petals\.$", line)
            is not None
        ):
            return "spell_aura_of_blue_petals_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is covered by an aura of green petals\.$", line
            )
            is not None
        ):
            return "spell_aura_of_green_petals_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s wounds begin to heal\.$", line) is not None
        ):
            return "spell_aura_of_marr_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is covered by an aura of red petals\.$", line)
            is not None
        ):
            return "spell_aura_of_red_petals_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is covered by an aura of white petals\.$", line
            )
            is not None
        ):
            return "spell_aura_of_white_petals_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ is entombed in ice\.$", line) is not None:
            return "spell_avalanche_other_on"
            # return "spell_entomb_in_ice_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ has been infused with the power of an Avatar\.$",
                line,
            )
            is not None
        ):
            return "spell_avatar_other_on"
            # return "spell_primal_avatar_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ summons power\.$", line) is not None:
            return "spell_avatar_other_cast"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s veins have been filled with deadly poison\.$",
                line,
            )
            is not None
        ):
            return "spell_bane_of_nife_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ staggers(\.|)\.$", line) is not None:
            return "spell_line_stagger_other_on"
            # return "spell_banish_summoned_other_on"
            # return "spell_banish_undead_other_on"
            # return "spell_bond_of_death_other_on"
            # return "spell_curse_of_the_garou_other_on"
            # return "spell_deadly_lifetap_other_on"
            # return "spell_deflux_other_on"
            # return "spell_dismiss_summoned_other_on"
            # return "spell_dismiss_undead_other_on"
            # return "spell_drain_soul_other_on"
            # return "spell_drain_spirit_other_on"
            # return "spell_essence_drain_other_on"
            # return "spell_essence_tap_other_on"
            # return "spell_exile_summoned_other_on"
            # return "spell_exile_undead_other_on"
            # return "spell_expel_undead_other_on"
            # return "spell_feast_of_blood_other_on"
            # return "spell_lifedraw_other_on"
            # return "spell_lifespike_other_on"
            # return "spell_lifetap_other_on"
            # return "spell_mana_conversion_other_on"
            # return "spell_poison_animal_i_other_on"
            # return "spell_poison_animal_ii_other_on"
            # return "spell_poison_animal_iii_other_on"
            # return "spell_poison_summoned_i_other_on"
            # return "spell_poison_summoned_ii_other_on"
            # return "spell_poison_summoned_iii_other_on"
            # return "spell_siphon_other_on"
            # return "spell_siphon_life_other_on"
            # return "spell_soul_bond_other_on"
            # return "spell_soul_consumption_other_on"
            # return "spell_soul_leech_other_on"
            # return "spell_soul_well_other_on"
            # return "spell_spirit_tap_other_on"
            # return "spell_strike_of_the_chosen_other_on"
            # return "spell_theft_of_thought_other_on"
            # return "spell_touch_of_night_other_on"
            # return "spell_ward_summoned_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is surrounded by a shrieking aura\.$", line)
            is not None
        ):
            return "spell_banshee_aura_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s skin sprouts barbs\.\.$", line) is not None
        ):
            return "spell_barbcoat_other_on"
        elif re.fullmatch(r"^Barbs spring from your skin\.$", line) is not None:
            return "spell_barbcoat_you_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ is enveloped by flame\.$", line) is not None:
            return "spell_line_mag_ds_other_on"
            # return "spell_barrier_of_combustion_other_on"
            # return "spell_boon_of_immolation_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is mauled by the moving ground\.$", line)
            is not None
        ):
            return "spell_upheaval_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is surrounded by a swirling maelstrom of magical force\.\.$",
                line,
            )
            is not None
        ):
            return "spell_barrier_of_force_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s goggles are imbued with bursts of battery powered sight\.$",
                line,
            )
            is not None
        ):
            return "spell_battery_vision_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s eyes gleam with bedlam\.$", line)
            is not None
        ):
            return "spell_bedlam_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ moans\.$", line) is not None:
            return "spell_line_nec_charm_other_on"
            # return "spell_beguile_undead_other_on"
            # return "spell_cajole_undead_other_on"
            # return "spell_dominate_undead_other_on"
            # return "spell_enslave_death_other_on"
            # return "spell_thrall_of_bones_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ begins to spin\.$", line) is not None:
            return "spell_line_spin_other_on"
            # return "spell_bellowing_winds_other_on"
            # return "spell_dyns_dizzying_draught_other_on"
            # return "spell_rodricks_gift_other_on"
            # return "spell_spin_the_bottle_other_on"
            # return "spell_whirl_till_you_hurl_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ lets loose a berserk yell\.$", line)
            is not None
        ):
            return "spell_line_berserker_madness_other_on"
            # return "spell_berserker_madness_i_other_on"
            # return "spell_berserker_madness_ii_other_on"
            # return "spell_berserker_madness_iii_other_on"
            # return "spell_berserker_madness_iv_other_on"
            # return "spell_berserker_spirit_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s muscles bulge with berserker strength\.$", line
            )
            is not None
        ):
            return "spell_berserker_strength_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ is bound to the area\.$", line) is not None:
            return "spell_bind_affinity_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ casts Bind Affinity\.$", line) is not None:
            return "spell_bind_affinity_other_cast"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s eyes gleam and then go dark\.$", line)
            is not None
        ):
            return "spell_line_bind_sight_other_on"
            # return "spell_bind_sight_other_on"
            # return "spell_cast_sight_other_on"
            # return "spell_shifting_sight_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s skin sprouts blades\.$", line) is not None:
            return "spell_bladecoat_other_on"
        elif re.fullmatch(r"^Blades spring from your skin\.$", line) is not None:
            return "spell_bladecoat_you_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ blinks a few times\.$", line) is not None:
            return "spell_line_memblur_other_on"
            # return "spell_blanket_of_forgetfulness_other_on"
            # return "spell_memory_blur_other_on"
            # return "spell_memory_flux_other_on"
            # return "spell_mind_wipe_other_on"
            # return "spell_reoccurring_amnesia_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s skin goes numb\.$", line) is not None:
            return "spell_blast_of_cold_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ screams in pain\.$", line) is not None:
            return "spell_line_shm_dis_dd_other_on"
            # return "spell_blast_of_poison_other_on"
            # return "spell_shock_of_the_tainted_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s skin ignites\.$", line) is not None:
            return "spell_line_fire_ignite_other_on"
            # return "spell_blaze_other_on"
            # return "spell_call_of_flame_other_on"
            # return "spell_firestrike_other_on"
            # return "spell_ignite_other_on"
            # return "spell_inferno_shock_other_on"
            # return "spell_shock_of_flame_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is surrounded by an aura of nature\.$", line)
            is not None
        ):
            return "spell_blessing_of_nature_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is surrounded by the blessing of the Blackstar\.$",
                line,
            )
            is not None
        ):
            return "spell_blessing_of_the_blackstar_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ begins to move faster\.$", line) is not None:
            return "spell_line_haste_other_on"
            # return "spell_blessing_of_the_grove_other_on"
            # return "spell_brittle_haste_ii_other_on"
            # return "spell_brittle_haste_iii_other_on"
            # return "spell_brittle_haste_iv_other_on"
            # return "spell_haste_other_on"
            # return "spell_swift_spirit_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is surrounded by a divine aura\.$", line)
            is not None
        ):
            return "spell_center_other_on"
            # return "spell_blessing_of_the_theurgist_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ lets loose a mighty roar\.$", line) is not None
        ):
            return "spell_blinding_fear_other_cast"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is blinded by a flash of light\.$", line)
            is not None
        ):
            return "spell_line_blind_other_on"
            # return "spell_blinding_luminance_other_on"
            # return "spell_flash_of_light_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ staggers around blindly\.$", line) is not None
        ):
            return "spell_line_blinding_poison_other_on"
            # return "spell_blinding_poison_i_other_on"
            # return "spell_blinding_poison_iii_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ fades away\.$", line) is not None:
            return "spell_line_fade_away_other_on"
            # return "spell_blinding_step_other_on"
            # return "spell_camouflage_other_on"
            # return "spell_cazic_gate_other_on"
            # return "spell_cobalt_scar_gate_other_on"
            # return "spell_combine_gate_other_on"
            # return "spell_common_gate_other_on"
            # return "spell_fay_gate_other_on"
            # return "spell_field_of_bone_port_other_on"
            # return "spell_frost_port_other_on"
            # return "spell_gate_other_on"
            # return "spell_great_divide_gate_other_on"
            # return "spell_iceclad_gate_other_on"
            # return "spell_improved_invisibility_other_on"
            # return "spell_improved_superior_camouflage_other_on"
            # return "spell_invisibility_other_on"
            # return "spell_nek_gate_other_on"
            # return "spell_north_gate_other_on"
            # return "spell_overthere_other_on"
            # return "spell_ring_of_butcher_other_on"
            # return "spell_ring_of_commons_other_on"
            # return "spell_ring_of_faydark_other_on"
            # return "spell_ring_of_feerrott_other_on"
            # return "spell_ring_of_great_divide_other_on"
            # return "spell_ring_of_iceclad_other_on"
            # return "spell_ring_of_karana_other_on"
            # return "spell_ring_of_lavastorm_other_on"
            # return "spell_ring_of_misty_other_on"
            # return "spell_ring_of_ro_other_on"
            # return "spell_ring_of_steamfont_other_on"
            # return "spell_ring_of_surefall_glade_other_on"
            # return "spell_ring_of_the_combines_other_on"
            # return "spell_ring_of_toxxulia_other_on"
            # return "spell_ring_of_wakening_lands_other_on"
            # return "spell_ro_gate_other_on"
            # return "spell_scareling_step_other_on"
            # return "spell_shadow_step_other_on"
            # return "spell_superior_camouflage_other_on"
            # return "spell_swamp_port_other_on"
            # return "spell_thurgadin_gate_other_on"
            # return "spell_tox_gate_other_on"
            # return "spell_translocate_other_on"
            # return "spell_translocate_cazic_other_on"
            # return "spell_translocate_combine_other_on"
            # return "spell_translocate_common_other_on"
            # return "spell_translocate_fay_other_on"
            # return "spell_translocate_great_divide_other_on"
            # return "spell_translocate_group_other_on"
            # return "spell_translocate_iceclad_other_on"
            # return "spell_translocate_nek_other_on"
            # return "spell_translocate_north_other_on"
            # return "spell_translocate_ro_other_on"
            # return "spell_translocate_tox_other_on"
            # return "spell_translocate_wakening_lands_other_on"
            # return "spell_translocate_west_other_on"
            # return "spell_wakening_lands_gate_other_on"
            # return "spell_west_gate_other_on"
            # return "spell_yonder_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is caught in a raging blizzard\.$", line)
            is not None
        ):
            return "spell_blizzard_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ staggers as spirits of frost slam against them\.$",
                line,
            )
            is not None
        ):
            return "spell_line_blizzard_blast_other_on"
            # return "spell_blizzard_blast_other_on"
            # return "spell_spirit_strike_other_on"
            # return "spell_winters_roar_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks pained\.$", line) is not None:
            return "spell_blood_claw_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s skin shrivels\.$", line) is not None:
            return "spell_bobbing_corpse_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s blood boils\.$", line) is not None:
            return "spell_boil_blood_other_on"
            # return "spell_boiling_blood_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ is bathed in fire\.$", line) is not None:
            return "spell_line_bolt_of_flame_other_on"
            # return "spell_bolt_of_flame_other_on"
            # return "spell_cinder_bolt_other_on"
            # return "spell_fire_bolt_other_on"
            # return "spell_flame_bolt_other_on"
            # return "spell_lava_bolt_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ has been struck by lightning\.$", line)
            is not None
        ):
            return "spell_line_bolt_of_karana_other_on"
            # return "spell_bolt_of_karana_other_on"
            # return "spell_careless_lightning_other_on"
            # return "spell_fury_of_air_other_on"
            # return "spell_invoke_lightning_other_on"
            # return "spell_lightning_blast_other_on"
        elif (
            re.fullmatch(
                r"^Lightning surges through your body(\.  You have taken \d+ point(s|) of damage|)\.$",
                line,
            )
            is not None
        ):
            return "spell_line_bolt_of_karana_you_on"
            # return "spell_bolt_of_karana_you_on"
            # return "spell_careless_lightning_you_on"
            # return "spell_fury_of_air_you_on"
            # return "spell_invoke_lightning_you_on"
            # return "spell_lightning_blast_you_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s feet are bound by strands of force\.$", line
            )
            is not None
        ):
            return "spell_bonds_of_force_other_on"
        elif (
            re.fullmatch(r"^Bonds of force stick your feet to the ground\.$", line)
            is not None
        ):
            return "spell_bonds_of_force_you_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is dragged down by dark vines\.$", line)
            is not None
        ):
            return "spell_bonds_of_tunare_other_on"
        elif (
            re.fullmatch(r"^Dark vines drag your feet into the ground\.$", line)
            is not None
        ):
            return "spell_bonds_of_tunare_you_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s skin burns away\.$", line) is not None:
            return "spell_ignite_bones_other_on"
            # return "spell_bone_melt_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks tranquil\.$", line) is not None:
            return "spell_line_clarity_other_on"
            # return "spell_boon_of_the_clear_mind_other_on"
            # return "spell_clarity_other_on"
            # return "spell_flowing_thought_i_other_on"
            # return "spell_flowing_thought_ii_other_on"
            # return "spell_flowing_thought_iii_other_on"
            # return "spell_flowing_thought_iv_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s face contorts and stretches, the skin breaking and peeling\.$",
                line,
            )
            is not None
        ):
            return "spell_boon_of_the_garou_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s skin sprouts brambles\.$", line) is not None
        ):
            return "spell_bramblecoat_other_on"
        elif re.fullmatch(r"^Brambles spring from your skin\.$", line) is not None:
            return "spell_bramblecoat_you_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks brave\.$", line) is not None:
            return "spell_bravery_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is slammed by an intense gust of wind\.$", line
            )
            is not None
        ):
            return "spell_breath_of_karana_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is immolated by blazing flames\.$", line)
            is not None
        ):
            return "spell_line_dru_fire_other_on"
            # return "spell_breath_of_ro_other_on"
            # return "spell_ros_fiery_sundering_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ stops breathing\.$", line) is not None:
            return "spell_breath_of_the_dead_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is slowed by the  mist of the seas\.$", line)
            is not None
        ):
            return "spell_breath_of_the_sea_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ sighs in tranquility\.$", line) is not None:
            return "spell_breeze_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ gains a flash of insight\.$", line) is not None
        ):
            return "spell_brilliance_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ reels in pain\.$", line) is not None:
            return "spell_line_brd_bruscos_other_on"
            # return "spell_bruscos_boastful_bellow_other_on"
            # return "spell_bruscos_bombastic_bellow_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ lets loose a great bellow\.$", line)
            is not None
        ):
            return "spell_bruscos_boastful_bellow_other_cast"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ lets loose a stunning bellow\.$", line)
            is not None
        ):
            return "spell_bruscos_bombastic_bellow_other_cast"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is engulfed by a bulwark of pure faith\.$", line
            )
            is not None
        ):
            return "spell_bulwark_of_faith_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s skin blisters and burns\.$", line)
            is not None
        ):
            return "spell_burn_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ is struck by fire\.$", line) is not None:
            return "spell_burning_vengeance_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ creates a mystic portal\.\.$", line)
            is not None
        ):
            return "spell_circle_of_the_combines_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ creates a mystic portal\.$", line) is not None
        ):
            return "spell_line_group_portal_other_on"
            # return "spell_burningtouch_other_on"
            # return "spell_circle_of_butcher_other_on"
            # return "spell_circle_of_cobalt_scar_other_on"
            # return "spell_circle_of_commons_other_on"
            # return "spell_circle_of_feerrott_other_on"
            # return "spell_circle_of_great_divide_other_on"
            # return "spell_circle_of_iceclad_other_on"
            # return "spell_circle_of_karana_other_on"
            # return "spell_circle_of_lavastorm_other_on"
            # return "spell_circle_of_misty_other_on"
            # return "spell_circle_of_ro_other_on"
            # return "spell_circle_of_steamfont_other_on"
            # return "spell_circle_of_the_combines_other_on"
            # return "spell_circle_of_toxxulia_other_on"
            # return "spell_circle_of_wakening_lands_other_on"
            # return "spell_evacuate_other_on"
            # return "spell_succor_other_on"
            # return "spell_succor_butcher_other_on"
            # return "spell_succor_east_other_on"
            # return "spell_succor_lavastorm_other_on"
            # return "spell_succor_north_other_on"
            # return "spell_succor_ro_other_on"
            # return "spell_trakanons_touch_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ goes berserk\.$", line) is not None:
            return "spell_line_berserk_other_on"
            # return "spell_burnout_other_on"
            # return "spell_burnout_ii_other_on"
            # return "spell_burnout_iii_other_on"
            # return "spell_burnout_iv_other_on"
            # return "spell_frenzy_other_on"
            # return "spell_fury_other_on"
            # return "spell_voice_of_the_berserker_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ shrieks as a scarab burrows into their skin\.$",
                line,
            )
            is not None
        ):
            return "spell_line_scarab_other_on"
            # return "spell_burrowing_scarab_other_on"
            # return "spell_scarab_storm_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ launches a foray of spores\.$", line)
            is not None
        ):
            return "spell_burrowing_scarab_other_cast"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ singes as the Burst of Fire hits them\.$", line
            )
            is not None
        ):
            return "spell_burst_of_fire_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ singes as the Burst of Flame hits them\.$", line
            )
            is not None
        ):
            return "spell_burst_of_flame_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks stronger\.$", line) is not None:
            return "spell_line_strength_other_on"
            # return "spell_burst_of_strength_other_on"
            # return "spell_furious_strength_other_on"
            # return "spell_girdle_of_karana_other_on"
            # return "spell_impart_strength_other_on"
            # return "spell_spirit_strength_other_on"
            # return "spell_storm_strength_other_on"
            # return "spell_strength_of_earth_other_on"
            # return "spell_strength_of_stone_other_on"
            # return "spell_strength_of_the_kunzar_other_on"
            # return "spell_strengthen_other_on"
            # return "spell_tumultuous_strength_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is enveloped in a cadeau of flame\.$", line)
            is not None
        ):
            return "spell_cadeau_of_flame_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ blisters and burns\.$", line) is not None:
            return "spell_calefaction_other_on"
            # return "spell_fist_of_fire_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ is briefly shadowed\.$", line) is not None:
            return "spell_calimony_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s body is surrounded by the Call of Earth\.$", line
            )
            is not None
        ):
            return "spell_call_of_earth_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ calls forth fire\.$", line) is not None:
            return "spell_call_of_flame_other_cast"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s weapons gleam\.$", line) is not None:
            return "spell_call_of_sky_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is knocked backwards by a concussion of air\.$",
                line,
            )
            is not None
        ):
            return "spell_call_of_sky_strike_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ steps into a mystic portal\.$", line)
            is not None
        ):
            return "spell_call_of_the_hero_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ growls as a whisper of the predator pervades the air\.$",
                line,
            )
            is not None
        ):
            return "spell_call_of_the_predator_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is ripped through a dimensional hole\.$", line)
            is not None
        ):
            return "spell_call_of_the_zero_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks less aggressive\.$", line) is not None:
            return "spell_line_pacify_other_on"
            # return "spell_calm_other_on"
            # return "spell_calm_animal_other_on"
            # return "spell_lull_other_on"
            # return "spell_pacify_other_on"
            # return "spell_soothe_other_on"
            # return "spell_wake_of_tranquility_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ feels a bit dispelled\.$", line) is not None:
            return "spell_cancel_magic_other_on"
            # return "spell_phobocancel_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ winces\.$", line) is not None:
            return "spell_line_wince_other_on"
            # return "spell_cannibalize_other_on"
            # return "spell_cannibalizei_ii_other_on"
            # return "spell_cannibalizei_iii_other_on"
            # return "spell_cannibalizei_iv_other_on"
            # return "spell_chords_of_dissonance_other_on"
            # return "spell_denons_disruptive_discord_other_on"
            # return "spell_denons_dissension_other_on"
            # return "spell_mana_sink_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is filled by the spirit of water\.$", line)
            is not None
        ):
            return "spell_captain_nalots_quickening_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is pelted by hailstones\.$", line) is not None
        ):
            return "spell_cascade_of_hail_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is engulfed in darkness\.$", line) is not None
        ):
            return "spell_line_nec_snare_other_on"
            # return "spell_cascading_darkness_other_on"
            # return "spell_dooming_darkness_other_on"
            # return "spell_engulfing_darkness_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ winces in an asinine way\.$", line) is not None
        ):
            return "spell_cassindras_insipid_ditty_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is covered in raging energy\.$", line)
            is not None
        ):
            return "spell_cast_force_other_on"
        elif (
            re.fullmatch(
                r"^Energy races across your body(\.  You have taken \d+ point(s|) of damage|)\.$",
                line,
            )
            is not None
        ):
            return "spell_cast_force_you_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ creates a shimmering portal(\.|)\.$", line)
            is not None
        ):
            return "spell_line_portal_other_on"
            # return "spell_cazic_portal_other_on"
            # return "spell_cobalt_scar_portal_other_on"
            # return "spell_combine_portal_other_on"
            # return "spell_common_portal_other_on"
            # return "spell_evacuate_fay_other_on"
            # return "spell_evacuate_nek_other_on"
            # return "spell_evacuate_north_other_on"
            # return "spell_evacuate_ro_other_on"
            # return "spell_evacuate_west_other_on"
            # return "spell_fay_portal_other_on"
            # return "spell_great_divide_portal_other_on"
            # return "spell_iceclad_portal_other_on"
            # return "spell_markars_relocation_other_on"
            # return "spell_nek_portal_other_on"
            # return "spell_ro_portal_other_on"
            # return "spell_tishans_relocation_other_on"
            # return "spell_tox_portal_other_on"
            # return "spell_wakening_lands_portal_other_on"
            # return "spell_west_portal_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s body is covered with a soft glow\.$", line)
            is not None
        ):
            return "spell_line_hot_other_on"
            # return "spell_celestial_cleansing_other_on"
            # return "spell_celestial_healing_other_on"
        elif (
            re.fullmatch(r"^Celestial light pumps through your body\.$", line)
            is not None
        ):
            return "spell_line_hot_you_on"
            # return "spell_celestial_cleansing_you_on"
            # return "spell_celestial_healing_you_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s blood stills within their veins\.$", line)
            is not None
        ):
            return "spell_cessation_of_cor_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ doubles over in pain as the noxious poison enters their lungs\.$",
                line,
            )
            is not None
        ):
            return "spell_ceticious_cloud_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ exhales a sickly green cloud\.$", line)
            is not None
        ):
            return "spell_ceticious_cloud_other_cast"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ rises chaotically into the air\.$", line)
            is not None
        ):
            return "spell_line_grav_flux_other_on"
            # return "spell_chaos_breath_other_on"
            # return "spell_gravity_flux_other_on"
            # return "spell_invert_gravity_other_on"
            # return "spell_scream_of_chaos_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is surrounded by fluxing strands of chaos\.$", line
            )
            is not None
        ):
            return "spell_chaos_flux_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s brain begins to smolder\.$", line)
            is not None
        ):
            return "spell_chaotic_feedback_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s skin ignites and chars\.$", line)
            is not None
        ):
            return "spell_char_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks charismatic\.$", line) is not None:
            return "spell_line_charisma_other_on"
            # return "spell_charisma_other_on"
            # return "spell_glamour_other_on"
            # return "spell_talisman_of_the_serpent_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ begins to run\.$", line) is not None:
            return "spell_chase_the_moon_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s skin frosts away\.$", line) is not None:
            return "spell_chill_bones_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is wracked by the chill of unlife\.$", line)
            is not None
        ):
            return "spell_chill_of_unlife_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s eyes glow violet\.$", line) is not None:
            return "spell_line_ultravision_other_on"
            # return "spell_chill_sight_other_on"
            # return "spell_plainsight_other_on"
            # return "spell_shadow_sight_other_on"
            # return "spell_ultravision_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is wracked by chilling poison\.$", line)
            is not None
        ):
            return "spell_chilling_embrace_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is blasted with chlorophyll\.$", line)
            is not None
        ):
            return "spell_chloroblast_other_on"
        elif re.fullmatch(r"^Jagged notes tear through your body\.$", line) is not None:
            return "spell_line_brd_dd_you_on"
            # return "spell_chords_of_dissonance_you_on"
            # return "spell_denons_disruptive_discord_you_on"
            # return "spell_denons_dissension_you_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s head snaps back\.$", line) is not None:
            return "spell_line_rng_aggro_other_on"
            # return "spell_cinder_jolt_other_on"
            # return "spell_jolt_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is immolated by raging energy\.$", line)
            is not None
        ):
            return "spell_circle_of_force_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is surrounded by a summer haze\.$", line)
            is not None
        ):
            return "spell_circle_of_summer_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is surrounded by a winter haze\.$", line)
            is not None
        ):
            return "spell_circle_of_winter_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks very tranquil\.$", line) is not None:
            return "spell_line_clarity_ii_other_on"
            # return "spell_clarity_ii_other_on"
            # return "spell_gift_of_pure_thought_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is surrounded by darkness\.$", line)
            is not None
        ):
            return "spell_clinging_darkness_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ has been poisoned, and begins to look dizzy\.$",
                line,
            )
            is not None
        ):
            return "spell_clockwork_poison_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s fangs gleam with poison\.$", line)
            is not None
        ):
            return "spell_line_npc_item_poison_other_cast"
            # return "spell_clockwork_poison_other_cast"
            # return "spell_deadly_poison_other_cast"
            # return "spell_feeble_poison_other_cast"
            # return "spell_ikatiars_revenge_other_cast"
            # return "spell_poison_other_cast"
            # return "spell_strong_poison_other_cast"
            # return "spell_weak_poison_other_cast"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s image clouds\.$", line) is not None:
            return "spell_cloud_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s skin freezes\.$", line) is not None:
            return "spell_line_skin_freeze_other_on"
            # return "spell_cloud_of_disempowerment_other_on"
            # return "spell_frost_shards_other_on"
            # return "spell_frost_shock_other_on"
            # return "spell_ice_comet_other_on"
            # return "spell_shock_of_frost_other_on"
            # return "spell_silver_breath_other_on"
            # return "spell_wave_of_cold_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ arches its back\.$", line) is not None:
            return "spell_line_raid_ae_other_cast"
            # return "spell_cloud_of_disempowerment_other_cast"
            # return "spell_silver_breath_other_cast"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks very afraid\.$", line) is not None:
            return "spell_line_fear_other_on"
            # return "spell_cloud_of_fear_other_on"
            # return "spell_fear_other_on"
            # return "spell_inspire_fear_other_on"
            # return "spell_invoke_fear_other_on"
            # return "spell_wave_of_fear_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is surrounded by a cloud of silence\.$", line)
            is not None
        ):
            return "spell_line_raid_silence_other_on"
            # return "spell_cloud_of_silence_other_on"
            # return "spell_mesmerizing_breath_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s armor cogs begin to spin faster and faster and faster\.$",
                line,
            )
            is not None
        ):
            return "spell_cog_boost_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s hands pulse blue\.$", line) is not None:
            return "spell_coldlight_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is stunned by scintillating colors\.$", line)
            is not None
        ):
            return "spell_line_enc_stun_other_on"
            # return "spell_color_flux_other_on"
            # return "spell_color_shift_other_on"
            # return "spell_color_skew_other_on"
        elif (
            re.fullmatch(r"^Scintillating colors pound through your brain\.$", line)
            is not None
        ):
            return "spell_line_enc_stun_you_on"
            # return "spell_color_flux_you_on"
            # return "spell_color_shift_you_on"
            # return "spell_color_skew_you_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is dazzled by scintillating colors\.$", line)
            is not None
        ):
            return "spell_color_slant_other_on"
        elif (
            re.fullmatch(r"^Scintillating colors dazzle your brain\.$", line)
            is not None
        ):
            return "spell_color_slant_you_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ is immolated by flame\.$", line) is not None:
            return "spell_column_of_fire_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ is encased in frost\.$", line) is not None:
            return "spell_line_frost_other_on"
            # return "spell_column_of_frost_other_on"
            # return "spell_ice_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is engulfed by lightning\.$", line) is not None
        ):
            return "spell_column_of_lightning_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s skin combusts\.$", line) is not None:
            return "spell_combust_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ summons a companion spirit\.$", line)
            is not None
        ):
            return "spell_line_shm_pet_other_on"
            # return "spell_companion_spirit_other_on"
            # return "spell_vigilant_spirit_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ is completely healed\.$", line) is not None:
            return "spell_complete_healing_other_on"
            # return "spell_complete_heal_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ staggers from a blow to the head\.$", line)
            is not None
        ):
            return "spell_concussion_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ combusts\.$", line) is not None:
            return "spell_line_combusts_other_on"
            # return "spell_conflagration_other_on"
            # return "spell_flame_shock_other_on"
            # return "spell_shock_of_fire_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s bones freezes and crack\.$", line)
            is not None
        ):
            return "spell_conglaciation_of_bone_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks courageous\.$", line) is not None:
            return "spell_courage_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ twitches\.$", line) is not None:
            return "spell_line_nec_twitch_other_on"
            # return "spell_covetous_subversion_other_on"
            # return "spell_rapacious_subversion_other_on"
            # return "spell_sedulous_subversion_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ concentrates\.$", line) is not None:
            return "spell_line_nec_twitch_other_cast"
            # return "spell_covetous_subversion_other_cast"
            # return "spell_rapacious_subversion_other_cast"
            # return "spell_sedulous_subversion_other_cast"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ is engulfed in a swarm\.$", line) is not None:
            return "spell_line_swarm_other_on"
            # return "spell_creeping_crud_other_on"
            # return "spell_drifting_death_other_on"
            # return "spell_drones_of_doom_other_on"
            # return "spell_stinging_swarm_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s eyes shimmer and gleam\.$", line)
            is not None
        ):
            return "spell_creeping_vision_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ has been crippled\.$", line) is not None:
            return "spell_cripple_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s eyes glaze over\.$", line) is not None:
            return "spell_line_brd_cc_other_on"
            # return "spell_crissions_pixie_strike_other_on"
            # return "spell_solons_bewitching_bravura_other_on"
            # return "spell_solons_song_of_the_sirens_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s eyes sparkle\.$", line) is not None:
            return "spell_cure_blindness_other_on"
            # return "spell_restore_sight_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks stupid\.$", line) is not None:
            return "spell_curse_of_the_simple_mind_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is consumed by the raging spirits of the land\.$",
                line,
            )
            is not None
        ):
            return "spell_curse_of_the_spirits_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s hands flicker\.$", line) is not None:
            return "spell_dance_of_the_fireflies_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks daring\.$", line) is not None:
            return "spell_daring_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s wounds disappear\.$", line) is not None:
            return "spell_dark_empathy_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ staggers as the light of dawn washes over it\.$",
                line,
            )
            is not None
        ):
            return "spell_dawncall_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ has been mesmerized\.$", line) is not None:
            return "spell_line_mez_other_on"
            # return "spell_dazzle_other_on"
            # return "spell_mesmerization_other_on"
            # return "spell_mesmerize_other_on"
            # return "spell_sathirs_mesmerization_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks dead\.$", line) is not None:
            return "spell_dead_man_floating_other_on"
            # return "spell_dead_men_floating_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s eyes glow red\.$", line) is not None:
            return "spell_line_infravision_other_on"
            # return "spell_deadeye_other_on"
            # return "spell_heat_sight_other_on"
            # return "spell_serpent_sight_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ smiles coldly\.$", line) is not None:
            return "spell_deadly_lifetap_other_cast"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ has been poisoned\.$", line) is not None:
            return "spell_line_poison_other_on"
            # return "spell_deadly_poison_other_on"
            # return "spell_dizzy_i_other_on"
            # return "spell_dizzy_ii_other_on"
            # return "spell_dizzy_iii_other_on"
            # return "spell_dizzy_iv_other_on"
            # return "spell_envenomed_bolt_other_on"
            # return "spell_feeble_mind_i_other_on"
            # return "spell_feeble_mind_ii_other_on"
            # return "spell_feeble_mind_iii_other_on"
            # return "spell_feeble_mind_iv_other_on"
            # return "spell_feeble_poison_other_on"
            # return "spell_froglok_poison_other_on"
            # return "spell_ikatiars_revenge_other_on"
            # return "spell_liquid_silver_i_other_on"
            # return "spell_lower_resists_i_other_on"
            # return "spell_lower_resists_ii_other_on"
            # return "spell_lower_resists_iii_other_on"
            # return "spell_lower_resists_iv_other_on"
            # return "spell_manticore_poison_other_on"
            # return "spell_muscle_lock_i_other_on"
            # return "spell_muscle_lock_ii_other_on"
            # return "spell_muscle_lock_iii_other_on"
            # return "spell_muscle_lock_iv_other_on"
            # return "spell_poison_other_on"
            # return "spell_poison_bolt_other_on"
            # return "spell_strong_poison_other_on"
            # return "spell_system_shock_i_other_on"
            # return "spell_system_shock_ii_other_on"
            # return "spell_system_shock_iii_other_on"
            # return "spell_system_shock_iv_other_on"
            # return "spell_system_shock_v_other_on"
            # return "spell_tainted_breath_other_on"
            # return "spell_venom_of_the_snake_other_on"
            # return "spell_weak_poison_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is wracked by deadly velium poison\.$", line)
            is not None
        ):
            return "spell_deadly_velium_poison_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is covered in a foreboding aura\.$", line)
            is not None
        ):
            return "spell_death_pact_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ dies\.$", line) is not None:
            return "spell_feign_death_other_on"
            # return "spell_death_peace_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ wilts\.$", line) is not None:
            return "spell_line_defoliation_other_on"
            # return "spell_defoliate_other_on"
            # return "spell_defoliation_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks dexterous\.$", line) is not None:
            return "spell_line_dexterity_other_on"
            # return "spell_deftness_other_on"
            # return "spell_dexterity_other_on"
            # return "spell_rising_dexterity_other_on"
            # return "spell_talisman_of_the_raptor_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ twitches, deliriously nimble\.$", line)
            is not None
        ):
            return "spell_deliriously_nimble_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s mind warps\.$", line) is not None:
            return "spell_dementia_other_on"
        elif re.fullmatch(r"^Twisted logic warps your mind\.$", line) is not None:
            return "spell_dementia_you_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s mind is clouded by insidious imagery\.$", line
            )
            is not None
        ):
            return "spell_dementing_visions_other_on"
        elif re.fullmatch(r"^Insidious imagery clouds your mind\.$", line) is not None:
            return "spell_dementing_visions_you_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ convulses\.$", line) is not None:
            return "spell_denons_bereavement_other_on"
        elif (
            re.fullmatch(r"^Venomous notes seep through your body\.\.$", line)
            is not None
        ):
            return "spell_denons_bereavement_you_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ staggers back a step\.$", line) is not None:
            return "spell_denons_desperate_dirge_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ lets loose a desperate dirge\.$", line)
            is not None
        ):
            return "spell_denons_desperate_dirge_other_cast"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is covered by a flickering shield\.$", line)
            is not None
        ):
            return "spell_desperate_hope_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is engulfed in devouring darkness\.$", line)
            is not None
        ):
            return "spell_devouring_darkness_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks more dexterous\.$", line) is not None:
            return "spell_dexterous_aura_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s brain begins to melt\.$", line) is not None
        ):
            return "spell_discordant_mind_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ has been diseased\.$", line) is not None:
            return "spell_line_npc_disease_other_on"
            # return "spell_disease_other_on"
            # return "spell_plagueratdisease_other_on"
            # return "spell_rabies_other_on"
            # return "spell_strong_disease_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s hands pulse with dark power\.$", line)
            is not None
        ):
            return "spell_line_npc_disease_other_cast"
            # return "spell_disease_other_cast"
            # return "spell_strong_disease_other_cast"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ doubles over in pain\.$", line) is not None:
            return "spell_disease_cloud_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s skin looks like diamond\.$", line)
            is not None
        ):
            return "spell_diamondskin_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s body begins to rot\.$", line) is not None:
            return "spell_diseased_cloud_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ exhales a cloud of corruption\.$", line)
            is not None
        ):
            return "spell_diseased_cloud_other_cast"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks frail\.$", line) is not None:
            return "spell_line_debuff_other_on"
            # return "spell_disempower_other_on"
            # return "spell_incapacitate_other_on"
            # return "spell_listless_power_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ has been disintegrated\.$", line) is not None:
            return "spell_disintegrate_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ looks around, distracted\.$", line) is not None
        ):
            return "spell_distraction_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is surrounded by a divine barrier\.$", line)
            is not None
        ):
            return "spell_divine_barrier_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is surrounded by an aura of Divine Favor\.$", line
            )
            is not None
        ):
            return "spell_divine_favor_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ begins to radiate with divine glory\.$", line)
            is not None
        ):
            return "spell_divine_glory_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ calls upon the gods\.$", line) is not None:
            return "spell_divine_intervention_other_cast"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is bathed in a divine light\.$", line)
            is not None
        ):
            return "spell_divine_light_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s hands begin to glow with divine might\.$", line
            )
            is not None
        ):
            return "spell_divine_might_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ feels the watchful eyes of the gods upon them\.$",
                line,
            )
            is not None
        ):
            return "spell_divine_intervention_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is struck by a surge of Divine Might\.$", line)
            is not None
        ):
            return "spell_divine_might_effect_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s eyes are filled by the flame of a divine purpose\.$",
                line,
            )
            is not None
        ):
            return "spell_divine_purpose_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ begins to radiate with divine strength\.$", line
            )
            is not None
        ):
            return "spell_divine_strength_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ is struck down\.$", line) is not None:
            return "spell_divine_wrath_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is encased in a cone of icy rage\.$", line)
            is not None
        ):
            return "spell_doljons_rage_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ begins to emanate heat\.$", line) is not None:
            return "spell_draconic_rage_other_on"
        elif re.fullmatch(r"^Rage courses through your veins\.$", line) is not None:
            return "spell_draconic_rage_you_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ lets loose a mighty roar.$", line) is not None
        ):
            return "spell_dragon_roar_other_cast"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is caught in a torrent of fire\.$", line)
            is not None
        ):
            return "spell_draught_of_fire_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is caught in a torrent of jagged ice\.$", line)
            is not None
        ):
            return "spell_draught_of_ice_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is caught in a torrent of reckless magic\.$", line
            )
            is not None
        ):
            return "spell_draught_of_jiva_other_on"
        elif (
            re.fullmatch(
                r"^[\w\s`\']+ (?<!opens (his|her|its) mouth wide and )yawns\.$", line
            )
            is not None
        ):
            return "spell_line_slow_other_on"
            # return "spell_drowsy_other_on"
            # return "spell_tagars_insects_other_on"
            # return "spell_tigirs_insects_other_on"
            # return "spell_turgurs_insects_other_on"
            # return "spell_walking_sleep_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s skin smolders\.$", line) is not None:
            return "spell_drybonefireburst_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ casts fire from its eyes\.$", line) is not None
        ):
            return "spell_line_npc_fire_you_off"
            # return "spell_drybonefireburst_you_off"
            # return "spell_smolder_other_cast"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ begins to rage\.$", line) is not None:
            return "spell_dulsehound_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is slowed by the embracing earth\.$", line)
            is not None
        ):
            return "spell_earthcall_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s feet sink into the ground\.$", line)
            is not None
        ):
            return "spell_line_hungry_earth_other_on"
            # return "spell_hungry_earth_other_on"
            # return "spell_earthelementalattack_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ rumbles\.$", line) is not None:
            return "spell_earthelementalattack_other_cast"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is smashed by the heaving ground\.$", line)
            is not None
        ):
            return "spell_earthquake_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ weakens\.$", line) is not None:
            return "spell_line_strength_debuff_other_on"
            # return "spell_ebbing_strength_other_on"
            # return "spell_siphon_strength_other_on"
            # return "spell_surge_of_enfeeblement_other_on"
            # return "spell_wave_of_enfeeblement_other_on"
            # return "spell_weaken_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is infused with echinacea\.$", line)
            is not None
        ):
            return "spell_echinacea_infusion_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ sinks into the ground\.$", line) is not None:
            return "spell_egress_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s body is electrified as the lightning strikes\.$",
                line,
            )
            is not None
        ):
            return "spell_electric_blast_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ feels protected from fire and ice\.$", line)
            is not None
        ):
            return "spell_line_int_resists_other_on"
            # return "spell_elemental_armor_other_on"
            # return "spell_elemental_shield_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s skin shreds and tears as bolts of elemental power strike\.$",
                line,
            )
            is not None
        ):
            return "spell_elemental_maelstrom_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ has been snared by vines of kelp\.$", line)
            is not None
        ):
            return "spell_embrace_of_the_kelpmaiden_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ is protected from cold\.$", line) is not None:
            return "spell_endure_cold_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is protected from disease\.$", line)
            is not None
        ):
            return "spell_endure_disease_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ is protected from fire\.$", line) is not None:
            return "spell_endure_fire_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is protected from magic\.$", line) is not None
        ):
            return "spell_endure_magic_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is protected from poison\.$", line) is not None
        ):
            return "spell_endure_poison_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ doesn\'t seem to be breathing anymore\.$", line
            )
            is not None
        ):
            return "spell_line_enduring_breath_other_on"
            # return "spell_enduring_breath_other_on"
            # return "spell_everlasting_breath_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s face loses it's glow\.$", line) is not None
        ):
            return "spell_energy_sap_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s skin blisters as energy rains down from above\.$",
                line,
            )
            is not None
        ):
            return "spell_energy_storm_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ is enfeebled\.$", line) is not None:
            return "spell_enfeeblement_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ gapes in reverent awe\.$", line) is not None:
            return "spell_enforced_reverence_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s feet become entangled\.$", line) is not None
        ):
            return "spell_engorging_roots_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s feet become entwined\.$", line) is not None
        ):
            return "spell_line_dru_root_other_on"
            # return "spell_engulfing_roots_other_on"
            # return "spell_ensnaring_roots_other_on"
            # return "spell_entrapping_roots_other_on"
            # return "spell_enveloping_roots_other_on"
            # return "spell_grasping_roots_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s\-]+ has been enlightened\.$", line) is not None:
            return "spell_enlightenment_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s\-]+ has been ensnared\.$", line) is not None:
            return "spell_line_snare_other_on"
            # return "spell_ensnare_other_on"
            # return "spell_snare_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s feet adhere to the ground\.$", line)
            is not None
        ):
            return "spell_line_root_other_on"
            # return "spell_enstill_other_on"
            # return "spell_fetter_other_on"
            # return "spell_immobilize_other_on"
            # return "spell_paralyzing_earth_other_on"
            # return "spell_root_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ has been enthralled\.$", line) is not None:
            return "spell_enthrall_other_on"
            # return "spell_gaze_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ succumbs to the enticement of flame\.$", line)
            is not None
        ):
            return "spell_enticement_of_flame_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ waves her hand\.$", line) is not None:
            return "spell_entomb_in_ice_other_cast"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ has been entranced\.$", line) is not None:
            return "spell_entrance_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ has been poisoned\.\.$", line) is not None:
            return "spell_envenomed_breath_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ reels\.$", line) is not None:
            return "spell_envenomed_heal_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ shimmers and blurs\.$", line) is not None:
            return "spell_line_mag_sow_other_on"
            # return "spell_expedience_other_on"
            # return "spell_velocity_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks energized\.$", line) is not None:
            return "spell_line_endurance_other_on"
            # return "spell_extinguish_fatigue_other_on"
            # return "spell_invigor_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks confused\.$", line) is not None:
            return "spell_eye_of_confusion_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s eyes glow green\.$", line) is not None:
            return "spell_eyes_of_the_cat_other_on"
        elif re.fullmatch(r"^[a-zA-Z`]+ fades\.$", line) is not None:
            return "spell_fade_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ screams in poisoned agony\.$", line)
            is not None
        ):
            return "spell_fangols_breath_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ has been fascinated\.$", line) is not None:
            return "spell_fascination_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks faint\.$", line) is not None:
            return "spell_fatigue_drain_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ casts Fear\.$", line) is not None:
            return "spell_fear_other_cast"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ is weakened\.$", line) is not None:
            return "spell_line_enc_debuff_other_on"
            # return "spell_feckless_might_other_on"
            # return "spell_insipid_weakness_other_on"
            # return "spell_weakness_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is enveloped in blazing energy\.$", line)
            is not None
        ):
            return "spell_feedback_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks more agile\.$", line) is not None:
            return "spell_feet_like_cat_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ winces as a fellspine digs in painfully\.$", line
            )
            is not None
        ):
            return "spell_fellspine_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ foams at the mouth\.$", line) is not None:
            return "spell_line_pet_haste_or_rabies_other_on"
            # return "spell_feral_spirit_other_on"
            # return "spell_rabies_other_on"
            # return "spell_spirit_quickening_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is enveloped by an aura of fiery might\.$", line
            )
            is not None
        ):
            return "spell_fiery_might_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ is covered in flames\.$", line) is not None:
            return "spell_line_fire_flames_other_on"
            # return "spell_fingers_of_fire_other_on"
            # return "spell_fire_flux_other_on"
            # return "spell_flame_arc_other_on"
            # return "spell_flame_flux_other_on"
        elif re.fullmatch(r"^Flames dance across your body\.$", line) is not None:
            return "spell_fingers_of_fire_you_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ is immolated in flame\.$", line) is not None:
            return "spell_line_fire_flame_other_on"
            # return "spell_fire_other_on"
            # return "spell_pillar_of_fire_other_on"
            # return "spell_supernova_other_on"
        elif (
            re.fullmatch(
                r"^Flames race across your body(\.  You have taken \d+ point of damage|)\.$",
                line,
            )
            is not None
        ):
            return "spell_line_fire_flames_you_on"
            # return "spell_fire_flux_you_on"
            # return "spell_flame_arc_you_on"
            # return "spell_flame_flux_you_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is blasted by blazing winds\.$", line)
            is not None
        ):
            return "spell_fire_spiral_of_alkabor_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s fist bursts into flame\.$", line)
            is not None
        ):
            return "spell_firefist_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s skin blisters as fire rains down from above\.$",
                line,
            )
            is not None
        ):
            return "spell_line_lava_storm_other_on"
            # return "spell_firestorm_other_on"
            # return "spell_lava_storm_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ has been struck by the shocking Fist of Karana\.$",
                line,
            )
            is not None
        ):
            return "spell_fist_of_karana_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ stands rigid in pain\.$", line) is not None:
            return "spell_fist_of_sentience_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ is encased in water\.$", line) is not None:
            return "spell_fist_of_water_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is surrounded by an outline of cold flame\.$", line
            )
            is not None
        ):
            return "spell_fixation_of_ro_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ breathes a jet of flame\.$", line) is not None
        ):
            return "spell_flame_jet_other_cast"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is surrounded by flickering flames\.$", line)
            is not None
        ):
            return "spell_flame_lick_other_on"
            # return "spell_obsidian_shatter_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s body erupts in a flame of divine light\.$", line
            )
            is not None
        ):
            return "spell_flame_of_light_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s skin erupts in flame\.$", line) is not None
        ):
            return "spell_flame_of_the_efreeti_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ begins to burn\.$", line) is not None:
            return "spell_flames_of_ro_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ simmers with fury\.$", line) is not None:
            return "spell_fleeting_fury_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ begins to rot\.$", line) is not None:
            return "spell_line_flesh_rot_other_on"
            # return "spell_flesh_rot_i_other_on"
            # return "spell_flesh_rot_ii_other_on"
            # return "spell_flesh_rot_iii_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is struck by a flurry of attacks\.$", line)
            is not None
        ):
            return "spell_flurry_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks focused\.$", line) is not None:
            return "spell_focus_of_spirit_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ is stunned\.$", line) is not None:
            return "spell_line_stun_other_on"
            # return "spell_force_other_on"
            # return "spell_holy_might_other_on"
            # return "spell_markars_clash_other_on"
            # return "spell_markars_discord_other_on"
            # return "spell_sound_of_force_other_on"
            # return "spell_stun_other_on"
            # return "spell_stun_command_on"
            # return "spell_tishans_clash_on"
            # return "spell_tishans_discord_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ has been force struck\.$", line) is not None:
            return "spell_line_force_strike_other_on"
            # return "spell_force_shock_other_on"
            # return "spell_force_strike_other_on"
            # return "spell_rage_of_the_sky_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is blasted by energy laden winds\.$", line)
            is not None
        ):
            return "spell_force_spiral_of_alkabor_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ slows down\.$", line) is not None:
            return "spell_line_enc_slow_other_on"
            # return "spell_forlorn_deeds_other_on"
            # return "spell_languid_pace_other_on"
            # return "spell_rejuvenation_other_on"
            # return "spell_shiftless_deeds_other_on"
            # return "spell_tepid_deeds_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ turns into a bear\.$", line) is not None:
            return "spell_form_of_the_great_bear_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ turns into a wolf\.$", line) is not None:
            return "spell_line_wolf_form_other_on"
            # return "spell_form_of_the_great_wolf_other_on"
            # return "spell_form_of_the_howler_other_on"
            # return "spell_form_of_the_hunter_other_on"
            # return "spell_greater_wolf_form_other_on"
            # return "spell_share_wolf_form_other_on"
            # return "spell_wolf_form_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s eyes flash with concentration\.$", line)
            is not None
        ):
            return "spell_fortitude_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is slowed by the freezing blast\.$", line)
            is not None
        ):
            return "spell_freezing_breath_other_on"
        elif (
            re.fullmatch(
                r"^An icy cold shoots through your body, slowing your movements\.$",
                line,
            )
            is not None
        ):
            return "spell_freezing_breath_you_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ exhales a freezing cone of cold\.$", line)
            is not None
        ):
            return "spell_freezing_breath_other_cast"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ summons a frenzied spirit\.$", line)
            is not None
        ):
            return "spell_frenzied_spirit_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s muscles bulge with frenzied strength\.$", line
            )
            is not None
        ):
            return "spell_frenzied_strength_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is iced by an intense cone of frost\.$", line)
            is not None
        ):
            return "spell_frost_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is chilled by a bolt of frost\.$", line)
            is not None
        ):
            return "spell_frost_bolt_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s body freezes as the frost hits them\.$", line
            )
            is not None
        ):
            return "spell_frost_breath_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ spouts forth a stream of frost\.$", line)
            is not None
        ):
            return "spell_frost_breath_other_cast"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is struck by the frost rift\.$", line)
            is not None
        ):
            return "spell_frost_rift_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is blasted by freezing winds\.$", line)
            is not None
        ):
            return "spell_line_wiz_alkabor_other_on"
            # return "spell_frost_spiral_of_alkabor_other_on"
            # return "spell_wrath_of_alkabor_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is assaulted by a storm of frost\.$", line)
            is not None
        ):
            return "spell_frost_storm_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s skin freezes and cracks\.$", line)
            is not None
        ):
            return "spell_frost_strike_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is blasted by a gust of bitter cold\.$", line)
            is not None
        ):
            return "spell_frostbite_other_on"
        elif re.fullmatch(r"^Bitter cold blasts your skin\.$", line) is not None:
            return "spell_frostbite_you_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is blessed by the spirits of ancient Coldain heroes\.$",
                line,
            )
            is not None
        ):
            return "spell_frostreavers_blessing_other_on"
            # return "spell_frostreavers_blessing_other_cast"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ is shredded by ice\.\.$", line) is not None:
            return "spell_frosty_death_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s hair stands on end\.$", line) is not None:
            return "spell_fufils_curtailing_chant_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ is covered in fungus\.$", line) is not None:
            return "spell_fungal_regrowth_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ inhales a dark powder\.$", line) is not None:
            return "spell_fungus_spores_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is struck by a sudden burst of force\.$", line)
            is not None
        ):
            return "spell_furor_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s skin blisters\.$", line) is not None:
            return "spell_line_shm_poison_other_on"
            # return "spell_gale_of_poison_other_on"
            # return "spell_poison_storm_other_on"
            # return "spell_sear_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s body withers from the gangrenous touch of Zum\`uul\.$",
                line,
            )
            is not None
        ):
            return "spell_gangrenous_touch_of_zumuul_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s hands take on a sickly green aura\.$", line)
            is not None
        ):
            return "spell_gangrenous_touch_of_zumuul_other_cast"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ screams as freezing ethereal mist swirls around them\.$",
                line,
            )
            is not None
        ):
            return "spell_garzicors_vengeance_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ steps into the shadows and disappears\.$", line
            )
            is not None
        ):
            return "spell_gather_shadows_other_on"
        elif re.fullmatch(r"^Strength returns to your legs\.$", line) is not None:
            return "spell_ghoul_root_you_off"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s hand pulses with an unholy aura\.$", line)
            is not None
        ):
            return "spell_ghoul_root_other_cast"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ screams in horror and pain\.$", line)
            is not None
        ):
            return "spell_gift_of_aerr_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ appears to be staring into nothingness\.$", line
            )
            is not None
        ):
            return "spell_line_enc_mana_buff_other_on"
            # return "spell_gift_of_brilliance_other_on"
            # return "spell_gift_of_insight_other_on"
            # return "spell_gift_of_magic_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ stumbles\.$", line) is not None:
            return "spell_line_npc_root_other_on"
            # return "spell_gelatroot_other_on"
            # return "spell_ghoul_root_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s pseudopods drip with fluid\.$", line)
            is not None
        ):
            return "spell_gelatroot_other_cast"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ has been mesmerized by the Glamour of Kintaz\.$",
                line,
            )
            is not None
        ):
            return "spell_glamour_of_kintaz_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is surrounded by a Tunarian glamour\.$", line)
            is not None
        ):
            return "spell_glamour_of_tunare_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s eyes gleam\.$", line) is not None:
            return "spell_line_magnify_other_on"
            # return "spell_glimpse_other_on"
            # return "spell_magnify_other_on"
            # return "spell_sight_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ becomes violent\.$", line) is not None:
            return "spell_graveyard_dust_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s armor is sped up by an injection of heated grease\.\.$",
                line,
            )
            is not None
        ):
            return "spell_grease_injection_other_on"
        elif (
            re.fullmatch(
                r"^An injection of heated grease speeds the movement of your armor$",
                line,
            )
            is not None
        ):
            return "spell_grease_injection_you_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ feels much better\.$", line) is not None:
            return "spell_line_healing_other_on"
            # return "spell_greater_healing_other_on"
            # return "spell_healing_other_on"
            # return "spell_knights_blessing_other_on"
            # return "spell_natures_touch_other_on"
            # return "spell_superior_healing_other_on"
            # return "spell_word_of_healing_other_on"
            # return "spell_word_of_health_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ becomes engulfed in a noxious cloud of green mist\.$",
                line,
            )
            is not None
        ):
            return "spell_greenmist_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s hand is covered with a dull aura\.$", line)
            is not None
        ):
            return "spell_grim_aura_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ is resistant to magic\.$", line) is not None:
            return "spell_line_magic_resist_other_on"
            # return "spell_group_resist_magic_other_on"
            # return "spell_resist_magic_other_on"
            # return "spell_resistance_to_magic_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is surrounded by a spirit aura\.$", line)
            is not None
        ):
            return "spell_guardian_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ summons a guardian spirit\.$", line)
            is not None
        ):
            return "spell_guardian_spirit_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s hands are bathed in light\.$", line)
            is not None
        ):
            return "spell_halo_of_light_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks peaceful\.$", line) is not None:
            return "spell_line_peace_other_on"
            # return "spell_harpy_voice_other_on"
            # return "spell_symphonic_harmony_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ gathers glowing blue strands of mana\.$", line)
            is not None
        ):
            return "spell_harvest_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ pulls out a leafy plant and looks at it\.$", line
            )
            is not None
        ):
            return "spell_harvest_leaves_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s image blurs\.$", line) is not None:
            return "spell_line_enc_ac_other_on"
            # return "spell_haze_other_on"
            # return "spell_mist_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks healthy\.$", line) is not None:
            return "spell_health_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s blood simmers\.$", line) is not None:
            return "spell_heat_blood_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s eyes gleam with heroic resolution\.$", line)
            is not None
        ):
            return "spell_line_heroic_valor_other_on"
            # return "spell_heroic_bond_other_on"
            # return "spell_heroism_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is burnt by the wrath of the heavens\.$", line)
            is not None
        ):
            return "spell_holy_shock_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s soul is assaulted by the ages\.$", line)
            is not None
        ):
            return "spell_porlos_fury_other_on"
            # return "spell_hsagras_wrath_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ hugs their doll\.$", line) is not None:
            return "spell_hug_other_on"
            # return "spell_hug_other_cast"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s body is cut by shards of magical ice\.$", line
            )
            is not None
        ):
            return "spell_ice_breath_other_on"
        elif re.fullmatch(r"^Shards of magical ice rend you\.$", line) is not None:
            return "spell_ice_breath_you_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s body is rent by freezing ice\.$", line)
            is not None
        ):
            return "spell_ice_rend_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+'s skin freezes over\.$", line) is not None:
            return "spell_line_wiz_ice_other_on"
            # return "spell_ice_shock_other_on"
            # return "spell_shock_of_ice_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is struck down by Solist's spear of ice\.$", line
            )
            is not None
        ):
            return "spell_ice_spear_of_solist_other_on"
        elif (
            re.fullmatch(r"^Solist's spear of ice strikes you down\.$", line)
            is not None
        ):
            return "spell_ice_spear_of_solist_you_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s body freezes\.$", line) is not None:
            return "spell_ice_strike_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ is pelted by sleet\.$", line) is not None:
            return "spell_icestrike_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s blood ignites\.$", line) is not None:
            return "spell_line_nec_fire_other_on"
            # return "spell_ignite_blood_other_on"
            # return "spell_pyrocruor_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s image shimmers(\.|)\.$", line) is not None:
            return "spell_line_illusion_other_on"
            # return "spell_illusion_air_elemental_other_on"
            # return "spell_illusion_barbarian_other_on"
            # return "spell_illusion_dark_elf_other_on"
            # return "spell_illusion_dry_bone_other_on"
            # return "spell_illusion_dwarf_other_on"
            # return "spell_illusion_earth_elemental_other_on"
            # return "spell_illusion_erudite_other_on"
            # return "spell_illusion_fire_elemental_other_on"
            # return "spell_illusion_gnome_other_on"
            # return "spell_illusion_halfelf_other_on"
            # return "spell_illusion_halfling_other_on"
            # return "spell_illusion_high_elf_other_on"
            # return "spell_illusion_human_other_on"
            # return "spell_illusion_iksar_other_on"
            # return "spell_illusion_ogre_other_on"
            # return "spell_illusion_skeleton_other_on"
            # return "spell_illusion_spirit_wolf_other_on"
            # return "spell_illusion_tree_other_on"
            # return "spell_illusion_troll_other_on"
            # return "spell_illusion_water_elemental_other_on"
            # return "spell_illusion_werewolf_other_on"
            # return "spell_illusion_wood_elf_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is surrounded by blazing flames\.$", line)
            is not None
        ):
            return "spell_immolate_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s flesh is seared\.$", line) is not None:
            return "spell_immolating_breath_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ exhales a cloud of flame\.$", line) is not None
        ):
            return "spell_immolating_breath_other_cast"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ shrieks as their bones are set ablaze\.$", line
            )
            is not None
        ):
            return "spell_incinerate_bones_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ starts to wretch\.$", line) is not None:
            return "spell_infectious_cloud_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ burns within the inferno of Al'Kabor\.$", line)
            is not None
        ):
            return "spell_inferno_of_alkabor_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ is enveloped in flame\.$", line) is not None:
            return "spell_line_mag_ds_other_on"
            # return "spell_inferno_shield_other_on"
            # return "spell_shield_of_flame_other_on"
            # return "spell_shield_of_lava_other_on"
            # return "spell_wave_of_flame_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ is healed\.$", line) is not None:
            return "spell_infusion_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks wise\.$", line) is not None:
            return "spell_insight_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ casts Inspire Fear\.$", line) is not None:
            return "spell_inspire_fear_other_cast"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks invigorated$", line) is not None:
            return "spell_invigorate_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ vanishes amidst the sound of whirrs and clicks\.$",
                line,
            )
            is not None
        ):
            return "spell_invisibility_cloak_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ fades a little\.$", line) is not None:
            return "spell_line_invis_undead_other_on"
            # return "spell_invisibility_to_undead_other_on"
            # return "spell_invisibility_versus_undead_other_on"
            # return "spell_sunskin_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is surrounded by an aura which shimmers\, and then fades away\.$",
                line,
            )
            is not None
        ):
            return "spell_line_invis_animal_other_on"
            # return "spell_invisibility_versus_animal_other_on"
            # return "spell_invisibility_versus_animals_other_on"
        elif re.fullmatch(r"^Part of your image fades away\.$", line) is not None:
            return "spell_line_invis_animal_you_on"
            # return "spell_invisibility_versus_animal_you_on"
            # return "spell_invisibility_versus_animals_you_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ casts Invoke Fear\.$", line) is not None:
            return "spell_invoke_fear_other_cast"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is slammed by a static pulse\.$", line)
            is not None
        ):
            return "spell_jylls_static_pulse_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is ashed by an intense wave of heat\.$", line)
            is not None
        ):
            return "spell_jylls_wave_of_heat_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is torn by a zephyr of ice\.$", line)
            is not None
        ):
            return "spell_jylls_zephyr_of_ice_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s head nods\.$", line) is not None:
            return "spell_kelins_lucid_lullaby_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks sad\.$", line) is not None:
            return "spell_kelins_lugubrious_lament_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s skin begins to steam\.$", line) is not None
        ):
            return "spell_line_potion_ds_other_on"
            # return "spell_kilvas_skin_of_flame_other_on"
            # return "spell_scorching_skin_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ flies backwards\.$", line) is not None:
            return "spell_knockback_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ sends forth a burst of energy\.$", line)
            is not None
        ):
            return "spell_knockback_other_cast"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ spasms violently\.$", line) is not None:
            return "spell_kylies_venom_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ begins to weep\.$", line) is not None:
            return "spell_largarns_lamentation_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is bound by strands of solid music\.$", line)
            is not None
        ):
            return "spell_line_brd_slow_other_on"
            # return "spell_largos_absonant_binding_other_on"
            # return "spell_largos_melodic_binding_other_on"
        elif (
            re.fullmatch(r"^Strands of solid music bind your body\.$", line) is not None
        ):
            return "spell_line_brd_slow_you_on"
            # return "spell_largos_absonant_binding_you_on"
            # return "spell_largos_melodic_binding_you_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is burned by the basilisk\'s firey breath\.$", line
            )
            is not None
        ):
            return "spell_lava_breath_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ pales\.$", line) is not None:
            return "spell_leach_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s skin looks like leather\.$", line)
            is not None
        ):
            return "spell_leatherskin_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is surrounded by a thorny barrier\.$", line)
            is not None
        ):
            return "spell_line_dru_ds_other_on"
            # return "spell_legacy_of_spike_other_on"
            # return "spell_legacy_of_thorn_other_on"
            # return "spell_shield_of_barbs_other_on"
            # return "spell_shield_of_brambles_other_on"
            # return "spell_shield_of_spikes_other_on"
            # return "spell_shield_of_thistles_other_on"
            # return "spell_shield_of_thorns_other_on"
            # return "spell_thorny_shield_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ steps into the shadows\.$", line) is not None:
            return "spell_levant_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s feet leave the ground\.$", line) is not None
        ):
            return "spell_levitate_other_on"
            # return "spell_levitation_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks pale\.$", line) is not None:
            return "spell_life_leech_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ feels better\.$", line) is not None:
            return "spell_light_healing_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s body spasms as the lightning bolt arcs through them\.$",
                line,
            )
            is not None
        ):
            return "spell_lightning_bolt_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is showered by sparks of lightning\.$", line)
            is not None
        ):
            return "spell_lightning_breath_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s skin ignites\.\.$", line) is not None:
            return "spell_lightning_shock_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s skin blisters as lightning rains down from above\.$",
                line,
            )
            is not None
        ):
            return "spell_lightning_storm_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s body spasms\.$", line) is not None:
            return "spell_lightning_strike_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s body begins to smoke\.$", line) is not None
        ):
            return "spell_line_liquid_silver_other_on"
            # return "spell_liquid_silver_ii_other_on"
            # return "spell_liquid_silver_iii_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ succumbs to the lure of flame\.$", line)
            is not None
        ):
            return "spell_lure_of_flame_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ succumbs to the lure of frost\.$", line)
            is not None
        ):
            return "spell_lure_of_frost_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ succumbs to the lure of ice\.$", line)
            is not None
        ):
            return "spell_lure_of_ice_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ succumbs to the lure of lightning\.$", line)
            is not None
        ):
            return "spell_lure_of_lightning_other_on"
        elif (
            re.fullmatch(r"^Long forgotten knowledge sifts through your mind\.$", line)
            is not None
        ):
            return "spell_lyssas_cataloging_libretto_you_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s eyes are covered by notes of solid music\.$",
                line,
            )
            is not None
        ):
            return "spell_lyssas_solidarity_of_vision_other_on"
        elif re.fullmatch(r"^Strands of music cover your eyes\.$", line) is not None:
            return "spell_lyssas_solidarity_of_vision_you_on"
        elif (
            re.fullmatch(r"^Music floods your mind and sharpens your sight\.$", line)
            is not None
        ):
            return "spell_lyssas_veracious_concord_you_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ has been Magi cursed\.$", line) is not None:
            return "spell_magi_curse_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ looks very uncomfortable\.$", line) is not None
        ):
            return "spell_line_malo_other_on"
            # return "spell_mala_other_on"
            # return "spell_malo_other_on"
            # return "spell_malosi_other_on"
            # return "spell_malosini_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is caught in a malevolent grasp\.$", line)
            is not None
        ):
            return "spell_malevolent_grasp_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is surrounded by orbs of chaotic mana\.$", line
            )
            is not None
        ):
            return "spell_mana_flare_other_on"
        elif (
            re.fullmatch(r"^Orbs of chaotic mana swirl around you\.$", line) is not None
        ):
            return "spell_mana_flare_you_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ staggers in pain\.$", line) is not None:
            return "spell_mana_sieve_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s skin is slicked by a silvery glow\.$", line)
            is not None
        ):
            return "spell_manasink_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s skin gleams with an incandescent glow\.$", line
            )
            is not None
        ):
            return "spell_manaskin_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s skin numbs as deadly mana rains down from above\.$",
                line,
            )
            is not None
        ):
            return "spell_manastorm_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s muscles fill with maniacal strength\.$", line
            )
            is not None
        ):
            return "spell_maniacal_strength_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ begins to shape the elements\.$", line)
            is not None
        ):
            return "spell_manifest_elements_other_cast"
        elif (
            re.fullmatch(r"^By your will the elements begin to take shape\.$", line)
            is not None
        ):
            return "spell_manifest_elements_you_cast"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s stinger gleams with poison\.$", line)
            is not None
        ):
            return "spell_manticore_poison_other_cast"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s skin gleams with a pure aura\.$", line)
            is not None
        ):
            return "spell_mark_of_karn_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s features sharpen\.$", line) is not None:
            return "spell_mask_of_the_hunter_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is swept away by a mellifluous melody\.$", line
            )
            is not None
        ):
            return "spell_melanies_mellifluous_motion_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ begins to mend\.$", line) is not None:
            return "spell_line_nec_pet_heal_other_on"
            # return "spell_mend_bones_other_on"
            # return "spell_renew_bones_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ exhales a silent cloud\.$", line) is not None:
            return "spell_mesmerizing_breath_other_cast"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is covered by a cloud of pain\.$", line)
            is not None
        ):
            return "spell_mind_cloud_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ feels a little better\.$", line) is not None:
            return "spell_minor_healing_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is surrounded by a translucent shield\.$", line
            )
            is not None
        ):
            return "spell_minor_shielding_other_on"
            # return "spell_minor_shielding_you_off"
            # return "spell_shielding_you_off"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ summons a familiar of the Mistwalker\.$", line)
            is not None
        ):
            return "spell_mistwalker_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ modulates\.$", line) is not None:
            return "spell_modulation_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ begins to move with mortal deftness\.$", line)
            is not None
        ):
            return "spell_mortal_deftness_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s armor movements are sharpened by an injection of mana energy$",
                line,
            )
            is not None
        ):
            return "spell_mystic_precision_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is cloaked in a shimmer of glowing symbols\.$", line
            )
            is not None
        ):
            return "spell_naltrons_mark_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ summons a spirit of nature\.$", line)
            is not None
        ):
            return "spell_nature_walkers_behest_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is assaulted by the wrath of nature\.$", line)
            is not None
        ):
            return "spell_natures_holy_wrath_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ has been struck down by the wrath of nature\.$",
                line,
            )
            is not None
        ):
            return "spell_natures_wrath_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+'s skin shimmers\.$", line) is not None:
            return "spell_line_dru_best_hp_other_on"
            # return "spell_natureskin_other_on"
            # return "spell_protection_of_the_glades_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ feels dispelled\.$", line) is not None:
            return "spell_nullify_magic_other_on"
            # return "spell_neutralize_magic_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks nimble\.$", line) is not None:
            return "spell_nimble_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks ambivalent\.$", line) is not None:
            return "spell_line_pacify_undead_other_on"
            # return "spell_numb_the_dead_other_on"
            # return "spell_rest_the_dead_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks stone cold\.$", line) is not None:
            return "spell_numbing_cold_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s image shifts out of focus\.$", line)
            is not None
        ):
            return "spell_obscure_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ reels in pain and loses concentration\.$", line
            )
            is not None
        ):
            return "spell_occlusion_of_sound_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ lets loose a piercing blast\.$", line)
            is not None
        ):
            return "spell_occlusion_of_sound_other_cast"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ begins to radiate\.$", line) is not None:
            return "spell_line_wiz_ds_other_on"
            # return "spell_okeils_flickering_flame_other_on"
            # return "spell_okeils_radiation_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ begins to spin from one hundred blows\.$", line
            )
            is not None
        ):
            return "spell_one_hundred_blows_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ deftly manipulates the boxes lock and flips the tumblers\.$",
                line,
            )
            is not None
        ):
            return "spell_open_black_box_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is adorned in an aura of radiant grace\.$", line
            )
            is not None
        ):
            return "spell_overwhelming_splendor_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is surrounded by a brief lupine aura\.$", line)
            is not None
        ):
            return "spell_spirit_of_wolf_other_on"
            # return "spell_pack_spirit_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ pulses with a blue-green aura\.$", line)
            is not None
        ):
            return "spell_line_nec_heal_other_on"
            # return "spell_pact_of_shadow_other_on"
            # return "spell_shadow_compact_other_on"
            # return "spell_shadowbond_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ panics\.$", line) is not None:
            return "spell_panic_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ has the fear of life put in them\.$", line)
            is not None
        ):
            return "spell_line_fear_undead_other_on"
            # return "spell_panic_the_dead_other_on"
            # return "spell_spook_the_dead_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s muscles lock\.$", line) is not None:
            return "spell_line_paralyzing_poison_other_on"
            # return "spell_paralyzing_poison_i_other_on"
            # return "spell_paralyzing_poison_ii_other_on"
            # return "spell_paralyzing_poison_iii_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ dons gleaming armor\.$", line) is not None:
            return "spell_phantom_armor_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ dons chainmail armor\.$", line) is not None:
            return "spell_phantom_chain_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ dons leather armor\.$", line) is not None:
            return "spell_phantom_leather_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ dons platemail armor\.$", line) is not None:
            return "spell_phantom_plate_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ feels very dispelled\.$", line) is not None:
            return "spell_line_enc_cancel_other_on"
            # return "spell_pillage_enchantment_other_on"
            # return "spell_strip_enchantment_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is encased within a pillar of frost\.$", line)
            is not None
        ):
            return "spell_pillar_of_frost_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is immolated in a pillar of raging lightning\.$",
                line,
            )
            is not None
        ):
            return "spell_pillar_of_lightning_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s jaws emit a foul stench\.$", line)
            is not None
        ):
            return "spell_plagueratdisease_other_cast"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is sheathed in ice crystals\.$", line)
            is not None
        ):
            return "spell_pogonip_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ has been injected with a chilling poison\.$", line
            )
            is not None
        ):
            return "spell_poisonous_chill_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ writhes in agony s the spirits of the forest attack\.$",
                line,
            )
            is not None
        ):
            return "spell_power_of_the_forests_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ shines with a primal aura\.$", line)
            is not None
        ):
            return "spell_primal_essence_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is washed in a vibrant blue light\.$", line)
            is not None
        ):
            return "spell_prime_healers_blessing_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is consumed by lightning\.$", line) is not None
        ):
            return "spell_project_lightning_other_on"
        elif re.fullmatch(r"^Lightning bursts through your body\.$", line) is not None:
            return "spell_project_lightning_you_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is covered in a protective aura\.$", line)
            is not None
        ):
            return "spell_protect_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s flesh begins to liquefy\.$", line)
            is not None
        ):
            return "spell_putrefy_flesh_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s skin erupts in purulent pock marks\.$", line
            )
            is not None
        ):
            return "spell_pox_of_bertoxxulous_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ gasps over in pain\.$", line) is not None:
            return "spell_putrid_breath_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ has been surrounded by the Quivering Veil of Xarn\.$",
                line,
            )
            is not None
        ):
            return "spell_quivering_veil_of_xarn_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s face takes on a radiant visage\.$", line)
            is not None
        ):
            return "spell_radiant_visage_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ flies into a chaotic rage\.$", line)
            is not None
        ):
            return "spell_rage_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is guided by the Rage of Tallon\.$", line)
            is not None
        ):
            return "spell_rage_of_tallon_other_on"
        elif re.fullmatch(r"^Tallons Rage departs\.$", line) is not None:
            return "spell_rage_of_tallon_you_off"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is weakened by the Rage of Vallon\.$", line)
            is not None
        ):
            return "spell_rage_of_vallon_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s eyes go wide with horror\.$", line)
            is not None
        ):
            return "spell_rage_of_zek_other_on"
        elif (
            re.fullmatch(
                r"^Lava sears your skin\.  You have taken [0-9]+ point(s|) of damage\.$",
                line,
            )
            is not None
        ):
            return "spell_rain_of_molten_lava_you_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ swoons in raptured bliss\.$", line) is not None
        ):
            return "spell_rapture_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s enchantments begin to fade\.$", line)
            is not None
        ):
            return "spell_recant_magic_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s body hums with a sapping vitality\.$", line)
            is not None
        ):
            return "spell_reckless_health_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s muscles bulge with reckless strength\.$", line
            )
            is not None
        ):
            return "spell_reckless_strength_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ has been struck by the judgement of the gods\.$",
                line,
            )
            is not None
        ):
            return "spell_reckoning_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ disperses\.$", line) is not None:
            return "spell_reclaim_energy_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s wounds fade away\.$", line) is not None:
            return "spell_remedy_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ screams as a magic force rends their flesh\.$", line
            )
            is not None
        ):
            return "spell_rend_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s form pulses blue$", line) is not None:
            return "spell_renew_elements_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s form shimmers blue\.$", line) is not None:
            return "spell_renew_summoning_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ is resistant to cold\.$", line) is not None:
            return "spell_resist_cold_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is resistant to disease\.$", line) is not None
        ):
            return "spell_resist_disease_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ is resistant to fire\.$", line) is not None:
            return "spell_resist_fire_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ is resistant to poison\.$", line) is not None:
            return "spell_resist_poison_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s skin shines\.$", line) is not None:
            return "spell_resistant_skin_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks resolute\.$", line) is not None:
            return "spell_resolution_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ has been struck by the wrath of the gods\.$",
                line,
            )
            is not None
        ):
            return "spell_retribution_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is frozen by the retribution of Al'Kabor\.$", line
            )
            is not None
        ):
            return "spell_retribution_of_alkabor_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s body shines with riotous health\.$", line)
            is not None
        ):
            return "spell_riotous_health_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s flesh begins to rot\.$", line) is not None:
            return "spell_rotting_flesh_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ begins to heal\.$", line) is not None:
            return "spell_rubicite_aura_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is surrounded by a shimmer of runes\.$", line)
            is not None
        ):
            return "spell_line_rune_other_on"
            # return "spell_rune_i_other_on"
            # return "spell_rune_ii_other_on"
            # return "spell_rune_iii_other_on"
            # return "spell_rune_iv_other_on"
            # return "spell_rune_v_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is filled with a savage spirit\.$", line)
            is not None
        ):
            return "spell_savage_spirit_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is surrounded by a dark lupine aura\.$", line)
            is not None
        ):
            return "spell_line_fragile_sow_other_on"
            # return "spell_scale_of_wolf_other_on"
            # return "spell_spirit_of_scale_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ grows scales\.$", line) is not None:
            return "spell_scale_skin_other_on"
        elif re.fullmatch(r"^Scarabs burrow into your flesh\.$", line) is not None:
            return "spell_scarab_storm_you_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ launches a spray of scarabs\.$", line)
            is not None
        ):
            return "spell_scarab_storm_other_cast"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is burned by the Scars of Sigil\.$", line)
            is not None
        ):
            return "spell_scars_of_sigil_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is surrounded by a dark haze\.$", line)
            is not None
        ):
            return "spell_line_nec_scent_other_on"
            # return "spell_scent_of_darkness_other_on"
            # return "spell_scent_of_terris_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is surrounded by a dull haze\.$", line)
            is not None
        ):
            return "spell_scent_of_dusk_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is surrounded by a dim haze\.$", line)
            is not None
        ):
            return "spell_scent_of_shadow_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is covered in scintillating flames\.$", line)
            is not None
        ):
            return "spell_scintillation_other_on"
        elif (
            re.fullmatch(r"^Scintillating flames race across your body\.$", line)
            is not None
        ):
            return "spell_scintillation_you_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s skin melts\.$", line) is not None:
            return "spell_scoriae_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ lets loose a mighty yaulp\.$", line)
            is not None
        ):
            return "spell_line_yaulp_other_on"
            # return "spell_screaming_mace_other_on"
            # return "spell_yaulp_other_on"
            # return "spell_yaulp_ii_other_on"
            # return "spell_yaulp_iii_other_on"
            # return "spell_yaulp_iv_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ begins to scream\.$", line) is not None:
            return "spell_screaming_terror_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is burnt by the Seeking Flame of Seukor\.$", line
            )
            is not None
        ):
            return "spell_seeking_flame_of_seukor_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s body pulses with fury\.$", line) is not None
        ):
            return "spell_seething_fury_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is bound by silver strands of music\.$", line)
            is not None
        ):
            return "spell_selos_assonant_strane_other_on"
        elif re.fullmatch(r"^Silver strands of music bind you\.$", line) is not None:
            return "spell_selos_assonant_strane_you_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is bound in chords of music\.$", line)
            is not None
        ):
            return "spell_selos_chords_of_cessation_other_on"
        elif re.fullmatch(r"^Chords of music bind your hands\.\.$", line) is not None:
            return "spell_selos_chords_of_cessation_you_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is surrounded by chains of music\.$", line)
            is not None
        ):
            return "spell_selos_consonant_chain_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s image fades around the edges\.$", line)
            is not None
        ):
            return "spell_shade_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s image fades into the shadows\.$", line)
            is not None
        ):
            return "spell_shadow_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is surrounded by a vortex of shadows\.$", line)
            is not None
        ):
            return "spell_shadow_vortex_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s skin is rent by shards\.$", line)
            is not None
        ):
            return "spell_shards_of_sorrow_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is surrounded by a thorny barrier of blades\.$",
                line,
            )
            is not None
        ):
            return "spell_shield_of_blades_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is surrounded by a shield of song\.$", line)
            is not None
        ):
            return "spell_shield_of_song_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s skin is covered in a mystic glow\.$", line)
            is not None
        ):
            return "spell_shieldskin_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is surrounded by a shifting spirit shield\.$", line
            )
            is not None
        ):
            return "spell_shifting_shield_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ is lacerated by steel\.$", line) is not None:
            return "spell_line_mag_shock_other_on"
            # return "spell_shock_of_blades_other_on"
            # return "spell_shock_of_spikes_other_on"
            # return "spell_shock_of_swords_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ convulses as lightning arcs through them\.$", line
            )
            is not None
        ):
            return "spell_shock_of_lightning_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ screams in agony\.$", line) is not None:
            return "spell_shock_of_poison_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is lacerated by deadly steel\.$", line)
            is not None
        ):
            return "spell_shock_of_steel_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is blasted by static winds\.$", line)
            is not None
        ):
            return "spell_shock_spiral_of_alkabor_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ is deafened\.$", line) is not None:
            return "spell_shrieking_howl_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s hands are covered by a nimbus of deathly darkness\.$",
                line,
            )
            is not None
        ):
            return "spell_shroud_of_death_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is washed over by a wave of shadows\.$", line)
            is not None
        ):
            return "spell_shroud_of_hate_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is engulfed in a seething mass of darkness\.$", line
            )
            is not None
        ):
            return "spell_shroud_of_pain_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is surrounded by a spirit shroud\.$", line)
            is not None
        ):
            return "spell_shroud_of_the_spirits_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s body is surrounded by a nimbus of deathly darkness\.$",
                line,
            )
            is not None
        ):
            return "spell_shroud_of_undeath_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s skin takes on a silvery hue\.$", line)
            is not None
        ):
            return "spell_silver_skin_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ grows stronger\.$", line) is not None:
            return "spell_line_siphon_strength_other_on"
            # return "spell_siphon_strength_recourse_other_on"
            # return "spell_steal_strength_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s skin blisters as lava rains down from above\.$",
                line,
            )
            is not None
        ):
            return "spell_sirocco_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s skin turns hard as diamond\.$", line)
            is not None
        ):
            return "spell_skin_like_diamond_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s skin shimmers with divine power\.$", line)
            is not None
        ):
            return "spell_skin_like_nature_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s skin turns hard as stone\.$", line)
            is not None
        ):
            return "spell_skin_like_rock_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s skin turns hard as steel\.$", line)
            is not None
        ):
            return "spell_skin_like_steel_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s skin turns hard as wood\.$", line)
            is not None
        ):
            return "spell_skin_like_wood_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s skin turns to shadow\.$", line) is not None
        ):
            return "spell_skin_of_the_shadow_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is drenched with skunk musk\.$", line)
            is not None
        ):
            return "spell_skunkspray_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ sprays its musk\.$", line) is not None:
            return "spell_skunkspray_other_cast"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ lets forth a fine mist\.$", line) is not None:
            return "spell_slime_mist_other_cast"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ has been smitten\.$", line) is not None:
            return "spell_smite_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ is engulfed by fire\.$", line) is not None:
            return "spell_smolder_other_on"
            # return "spell_snakeelefireburst_other_on"
        elif (
            re.fullmatch(
                r"^Fire engulfs you(\.  You have taken \d+ point(s|) of damage|)\.$",
                line,
            )
            is not None
        ):
            return "spell_smolder_you_on"
            # return "spell_snakeelefireburst_you_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s eyes cast fire\.$", line) is not None:
            return "spell_snakeelefireburst_other_cast"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ winks\.$", line) is not None:
            return "spell_song_of_dawn_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ flees in nocturnal terror\.$", line)
            is not None
        ):
            return "spell_song_of_midnight_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ stumbles toward you\.$", line) is not None:
            return "spell_song_of_twilight_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ writhes in agony\.$", line) is not None:
            return "spell_soul_devour_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s body pulses with the spirit of the Shissar\.$",
                line,
            )
            is not None
        ):
            return "spell_speed_of_the_shissar_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s skin sprouts spikes\.$", line) is not None:
            return "spell_spikecoat_other_on"
        elif re.fullmatch(r"^Spikes spring from your skin.$", line) is not None:
            return "spell_spikecoat_you_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ spins the bottle\.$", line) is not None:
            return "spell_spin_the_bottle_other_cast"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is coated in translucent armor\.$", line)
            is not None
        ):
            return "spell_spirit_armor_other_on"
        elif (
            re.fullmatch(r"^Translucent armor gathers around you\.$", line) is not None
        ):
            return "spell_spirit_armor_you_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is surrounded by a brief ursine aura\.$", line)
            is not None
        ):
            return "spell_spirit_of_bear_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is surrounded by a brief feline aura\.$", line)
            is not None
        ):
            return "spell_line_cat_other_on"
            # return "spell_spirit_of_cat_other_on"
            # return "spell_spirit_of_cheetah_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is surrounded by a brief simian aura\.$", line)
            is not None
        ):
            return "spell_spirit_of_monkey_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ turns into a tree\.$", line) is not None:
            return "spell_line_dru_tree_other_on"
            # return "spell_spirit_of_oak_other_on"
            # return "spell_treeform_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is surrounded by a brief bovine aura\.$", line)
            is not None
        ):
            return "spell_spirit_of_ox_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is surrounded by a brief serpentine aura\.$", line
            )
            is not None
        ):
            return "spell_spirit_of_snake_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ summons a howling spirit.$", line) is not None
        ):
            return "spell_spirit_of_the_howler_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s body begins to splurt\.$", line) is not None
        ):
            return "spell_splurt_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s feet stick to the ground as they begin to regenerate\.$",
                line,
            )
            is not None
        ):
            return "spell_stalwart_regeneration_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks robust\.$", line) is not None:
            return "spell_line_shm_sta_other_on"
            # return "spell_stamina_other_on"
            # return "spell_talisman_of_the_brute_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ is bathed in starfire\.$", line) is not None:
            return "spell_starfire_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s hands pulse softly\.$", line) is not None:
            return "spell_starshine_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is consumed in a magic pulse\.$", line)
            is not None
        ):
            return "spell_static_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ staggers back\.$", line) is not None:
            return "spell_static_strike_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s armor cranks harder as steam floods through it\.$",
                line,
            )
            is not None
        ):
            return "spell_steam_overload_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s skin looks like steel\.$", line) is not None
        ):
            return "spell_steelskin_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is encased in solid stone\.$", line)
            is not None
        ):
            return "spell_stone_breath_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s body burns as the acid hits them\.$", line)
            is not None
        ):
            return "spell_stream_of_acid_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ spews a stream of acid\.$", line) is not None:
            return "spell_stream_of_acid_other_cast"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks strong\.$", line) is not None:
            return "spell_line_shm_str_other_on"
            # return "spell_strength_other_on"
            # return "spell_talisman_of_the_rhino_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s body is strengthened by nature\.$", line)
            is not None
        ):
            return "spell_strength_of_nature_other_on"
        elif (
            re.fullmatch(r"^Nature\'s strength flows through your muscles\.$", line)
            is not None
        ):
            return "spell_strength_of_nature_you_on"
        elif re.fullmatch(r"^Nature\'s strength ebbs\.$", line) is not None:
            return "spell_strength_of_nature_you_off"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ is Struck\.$", line) is not None:
            return "spell_strike_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ sets loose a torrent of lightning\.$", line)
            is not None
        ):
            return "spell_line_npc_thunder_other_cast"
            # return "spell_strike_of_thunder_other_cast"
            # return "spell_thunder_blast_other_cast"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ staggers with intense pain\.$", line)
            is not None
        ):
            return "spell_stun_breath_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ screams\.$", line) is not None:
            return "spell_stun_breath_other_cast"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ reels from a stunning blow\.$", line)
            is not None
        ):
            return "spell_stunning_blow_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ gasps for breath\.$", line) is not None:
            return "spell_suffocating_sphere_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ summons a companion to their side\.$", line)
            is not None
        ):
            return "spell_summon_companion_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ summons a swirling orb of elements\.$", line)
            is not None
        ):
            return "spell_summon_orb_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s hands pulse with soft light\.$", line)
            is not None
        ):
            return "spell_summon_wisp_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is blinded by a sunbeam\.$", line) is not None
        ):
            return "spell_sunbeam_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is consumed by the flames of the sun\.$", line)
            is not None
        ):
            return "spell_sunstrike_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is engulfed by a swarm of deadly insects\.$", line
            )
            is not None
        ):
            return "spell_swarm_of_retribution_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is engulfed by a swarm of insects\.$", line)
            is not None
        ):
            return "spell_swarming_pain_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is surrounded by a warm aura\.$", line)
            is not None
        ):
            return "spell_sympathetic_aura_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks tougher\.$", line) is not None:
            return "spell_line_shm_hp_other_on"
            # return "spell_talisman_of_altuna_other_on"
            # return "spell_talisman_of_kragg_other_on"
            # return "spell_talisman_of_tnarg_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ has been protected by the Talisman of Jasinth\.$",
                line,
            )
            is not None
        ):
            return "spell_talisman_of_jasinth_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ has been protected by the Talisman of Shadoo\.$",
                line,
            )
            is not None
        ):
            return "spell_talisman_of_shadoo_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is surrounded by a pulse of static air\.$", line
            )
            is not None
        ):
            return "spell_taper_enchantment_other_on"
        elif (
            re.fullmatch(r"^Tiny bubbles of music surround your head\.$", line)
            is not None
        ):
            return "spell_tarews_aquatic_ayre_you_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ glances nervously about\.$", line) is not None
        ):
            return "spell_line_tash_other_on"
            # return "spell_tashan_other_on"
            # return "spell_tashani_other_on"
            # return "spell_tashania_other_on"
            # return "spell_tashanian_other_on"
            # return "spell_wind_of_tishani_other_on"
            # return "spell_wind_of_tishanian_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s skin blisters as the tears of Druzzil rain upon them\.\.$",
                line,
            )
            is not None
        ):
            return "spell_tears_of_druzzil_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s skin blisters as the tears of Solusek rain upon them\.\.$",
                line,
            )
            is not None
        ):
            return "spell_tears_of_solusek_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ peers through a telescope\.$", line)
            is not None
        ):
            return "spell_telescope_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is cast into the pit by Dain Frostreavers justice\.$",
                line,
            )
            is not None
        ):
            return "spell_the_dains_justice_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ writhes and staggers\.$", line) is not None:
            return "spell_the_unspoken_word_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ intones the Unspoken Word\.$", line)
            is not None
        ):
            return "spell_the_unspoken_word_you_off"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s skin sprouts thistles\.$", line) is not None
        ):
            return "spell_thistlecoat_other_on"
        elif re.fullmatch(r"^Thistles spring from your skin\.$", line) is not None:
            return "spell_thistlecoat_you_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s skin sprouts thorns\.$", line) is not None:
            return "spell_thorncoat_other_on"
        elif re.fullmatch(r"^Thorns spring from your skin\.$", line) is not None:
            return "spell_thorncoat_you_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ has been struck by a Thunder Bolt\.$", line)
            is not None
        ):
            return "spell_thunder_strike_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ has been thunder stunned\.$", line) is not None
        ):
            return "spell_thunderbold_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+  is stunned by a clap of thunder\.$", line)
            is not None
        ):
            return "spell_thunderclap_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is blasted by a jet of acid\.$", line)
            is not None
        ):
            return "spell_torbas_acid_blast_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ grimaces in pain\.$", line) is not None:
            return "spell_torment_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ screams from the Torment of Argli\.$", line)
            is not None
        ):
            return "spell_torment_of_argli_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is gripped by shadows of fear and terror\.$", line
            )
            is not None
        ):
            return "spell_torment_of_shadows_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ falls into a state of torpor\.$", line)
            is not None
        ):
            return "spell_torpor_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s skin steams and melts\.$", line) is not None
        ):
            return "spell_torrent_of_poison_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ begins to walk faster(\.|)\.$", line)
            is not None
        ):
            return "spell_travelerboots_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is filled with trepidation\.$", line)
            is not None
        ):
            return "spell_trepidation_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is crushed by a wall of water\.$", line)
            is not None
        ):
            return "spell_line_koi_or_trident_other_on"
            # return "spell_tsunami_other_on"
            # return "spell_waves_of_the_deep_sea_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ staggers under the weight of divine words\.$", line
            )
            is not None
        ):
            return "spell_turning_of_the_unnatural_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ begins to chant\.$", line) is not None:
            return "spell_line_brd_tuyen_other_on"
            # return "spell_tuyens_chant_of_flame_other_on"
            # return "spell_tuyens_chant_of_frost_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s image fades into the umbra\.$", line)
            is not None
        ):
            return "spell_umbra_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ exudes an aura of massive charisma\.$", line)
            is not None
        ):
            return "spell_unfailing_reverence_other_on"
        elif (
            re.fullmatch(r"^People look at you with unfailing reverence\.$", line)
            is not None
        ):
            return "spell_unfailing_reverence_you_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ has become fearless\!$", line) is not None:
            return "spell_valiant_companion_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks valorous\.$", line) is not None:
            return "spell_valor_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is blasted by the Vengeance of Al\'Kabor\.$", line
            )
            is not None
        ):
            return "spell_vengeance_of_alkabor_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ adheres to the ground\.$", line) is not None:
            return "spell_vengeance_of_the_glades_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is struck by a sudden force\.$", line)
            is not None
        ):
            return "spell_verlekarnorms_disaster_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ staggers under the curse of Vexing Mordinia\.$",
                line,
            )
            is not None
        ):
            return "spell_vexing_mordinia_other_on"
        elif (
            re.fullmatch(r"^Vexing Mordinia begins to drain your life away\.$", line)
            is not None
        ):
            return "spell_vexing_mordinia_you_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ experiences visions of grandeur\.$", line)
            is not None
        ):
            return "spell_visions_of_grandeur_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s head shimmers\.$", line) is not None:
            return "spell_voice_graft_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ calls out to Karana\.$", line) is not None:
            return "spell_wake_of_karana_other_cast"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ stares off into space\.$", line) is not None:
            return "spell_wandering_mind_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is singed by a wave of fire\.$", line)
            is not None
        ):
            return "spell_wave_of_fire_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ summons the power of elemental fire\.$", line)
            is not None
        ):
            return "spell_wave_of_flame_other_cast"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ is surrounded by a wave of healing\.$", line)
            is not None
        ):
            return "spell_wave_of_healing_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+\'s skin sears\.$", line) is not None:
            return "spell_wave_of_heat_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s face becomes twisted with fury\.$", line)
            is not None
        ):
            return "spell_whirlwind_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+\'s skin ignites as wildfire courses over them\.$",
                line,
            )
            is not None
        ):
            return "spell_wildfire_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ discorporates in a portal of wind\.$", line)
            is not None
        ):
            return "spell_line_dru_skyfire_or_ej_other_on"
            # return "spell_wind_of_the_north_other_on"
            # return "spell_wind_of_the_south_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+\'s body is rent by freezing winds\.$", line)
            is not None
        ):
            return "spell_winds_of_gelid_other_on"
        elif re.fullmatch(r"^Freezing winds rend your body\.$", line) is not None:
            return "spell_winds_of_gelid_you_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ is engulfed in a swarm of deadly insects\.$", line
            )
            is not None
        ):
            return "spell_winged_death_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ begins to move with wonderous rapidity\.$", line
            )
            is not None
        ):
            return "spell_wonderous_rapidity_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ writhes in pain\.$", line) is not None:
            return "spell_line_word_other_on"
            # return "spell_word_divine_other_on"
            # return "spell_word_of_pain_other_on"
            # return "spell_word_of_shadow_other_on"
            # return "spell_word_of_souls_other_on"
            # return "spell_word_of_spirit_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ feels the touch of Redemption\.$", line)
            is not None
        ):
            return "spell_word_of_redemption:_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ feels restored\.$", line) is not None:
            return "spell_word_of_restoration_other_on"
        elif re.fullmatch(r"^[a-zA-Z`\s]+ looks vigorous\.$", line) is not None:
            return "spell_word_of_vigor_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ has been struck down by wrath\.$", line)
            is not None
        ):
            return "spell_wrath_other_on"
        elif (
            re.fullmatch(r"^[a-zA-Z`\s]+ has been gripped by nature's wrath\.$", line)
            is not None
        ):
            return "spell_wrath_of_nature_other_on"
        elif (
            re.fullmatch(
                r"^[a-zA-Z`\s]+ has been struck by the force of Ykesha\.$", line
            )
            is not None
        ):
            return "spell_ykesha_other_on"

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
                r"^You agree with [a-zA-Z`\s]+\.$",
                line,
            )
            is not None
        ):
            return "emote_agree_you"
        elif (
            re.fullmatch(
                r"^[a-zA-Z]+ agrees with [a-zA-Z`\s]+\.$",
                line,
            )
            is not None
        ):
            return "emote_agree_other"
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
                r"^You make a rude gesture( at [a-zA-Z`\s]+|)\.$",
                line,
            )
            is not None
        ):
            return "emote_bird_you"
        elif (
            re.fullmatch(
                r"^[a-zA-Z]+ makes a rude gesture( at [a-zA-Z`\s]+|)\.$",
                line,
            )
            is not None
        ):
            return "emote_bird_other"
        elif (
            re.fullmatch(
                r"^You (look around for someone to bite|bite [a-zA-Z`\s]+ on the leg)\!$",
                line,
            )
            is not None
        ):
            return "emote_bite_you"
        elif (
            re.fullmatch(
                r"^[a-zA-Z]+ (looks around for someone to bite|bites [a-zA-Z`\s]+ on the leg)\!$",
                line,
            )
            is not None
        ):
            return "emote_bite_other"
        elif (
            re.fullmatch(r"^You bleed (quietly|all over [a-zA-Z`\s]+)\.$", line)
            is not None
        ):
            return "emote_bleed_you"
        elif (
            re.fullmatch(r"^[a-zA-Z]+ bleeds (quietly|all over [a-zA-Z`\s]+)\.$", line)
            is not None
        ):
            return "emote_bleed_other"
        elif (
            re.fullmatch(
                r"^(You blink in disbelief\.|You blink at [a-zA-Z`\s]+ in disbelief\.)$",
                line,
            )
            is not None
        ):
            return "emote_blink_you"
        elif (
            re.fullmatch(r"^(You blush profusely|You blush at [a-zA-Z`\s]+)\.$", line)
            is not None
        ):
            return "emote_blush_you"
        elif (
            re.fullmatch(
                r"^([a-zA-Z]+ blushes|[a-zA-Z]+ blushes at [a-zA-Z`\s]+)\.$", line
            )
            is not None
        ):
            return "emote_blush_other"
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
        elif re.fullmatch(r"^You burp loudly( at [a-zA-Z`\s]+|)\.$", line) is not None:
            return "emote_burp_you"
        elif (
            re.fullmatch(r"^[a-zA-Z]+ burps loudly( at [a-zA-Z`\s]+|)\.$", line)
            is not None
        ):
            return "emote_burp_other"
        elif (
            re.fullmatch(
                r"^You wave goodbye to [a-zA-Z`\s]+\.$",
                line,
            )
            is not None
        ):
            return "emote_bye_you"
        elif (
            re.fullmatch(
                r"^[a-zA-Z]+ waves goodbye to [a-zA-Z`\s]+\.$",
                line,
            )
            is not None
        ):
            return "emote_bye_other"
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
        elif re.fullmatch(r"^You chuckle( at [a-zA-Z`\s]+|)\.$", line) is not None:
            return "emote_chuckle_you"
        elif (
            re.fullmatch(r"^[a-zA-Z]+ chuckles( at [a-zA-Z`\s]+|)\.$", line) is not None
        ):
            return "emote_chuckle_other"
        elif (
            re.fullmatch(
                r"^(You clap your hands together|You clap happily for [a-zA-Z`\s]+) \- hurray\!$",
                line,
            )
            is not None
        ):
            return "emote_clap_you"
        elif (
            re.fullmatch(
                r"^([a-zA-Z]+ claps (his|her|its) hands together|[a-zA-Z]+ claps happily for [a-zA-Z`\s]+) \- hurray\!$",
                line,
            )
            is not None
        ):
            return "emote_clap_other"
        elif (
            re.fullmatch(r"^You (need to be comforted|comfort [a-zA-Z`\s]+)\.$", line)
            is not None
        ):
            return "emote_comfort_you"
        elif (
            re.fullmatch(
                r"^[a-zA-Z]+ (needs to be comforted|comforts [a-zA-Z`\s]+)\.$", line
            )
            is not None
        ):
            return "emote_comfort_other"
        elif (
            re.fullmatch(
                r"^You congratulate [a-zA-Z`\s]+ on a job well done\.$",
                line,
            )
            is not None
        ):
            return "emote_congratulate_you"
        elif (
            re.fullmatch(
                r"^[a-zA-Z]+ congratulates [a-zA-Z`\s]+ on a job well done\.$",
                line,
            )
            is not None
        ):
            return "emote_congratulate_other"
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
        elif re.fullmatch(r"^(You cry|You cry over [a-zA-Z`\s]+)\.$", line) is not None:
            return "emote_cry_you"
        elif (
            re.fullmatch(
                r"^([a-zA-Z]+ cries|[a-zA-Z]+ cries over [a-zA-Z`\s]+)\.$", line
            )
            is not None
        ):
            return "emote_cry_other"
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
                r"^You (stand on your tip\-toes and do a dance of joy\!|grab hold of [a-zA-Z`\s]+ and begin to dance with (him|her|it|them)\.)$",
                line,
            )
            is not None
        ):
            return "emote_dance_you"
        elif (
            re.fullmatch(
                r"^[a-zA-Z]+ (stands on (his|her) tip-toes and does a dance of joy\!|grabs hold of [a-zA-Z`\s\'\-]+ and begins to dance with (?:h(?:er|im)|it)\.)$",
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
            re.fullmatch(r"^You flex (your muscles proudly|at [a-zA-Z`\s]+)\.$", line)
            is not None
        ):
            return "emote_flex_you"
        elif (
            re.fullmatch(
                r"^[a-zA-Z]+ flexes ((his|her) muscles proudly|at [a-zA-Z`\s]+)\.$",
                line,
            )
            is not None
        ):
            return "emote_flex_other"
        elif re.fullmatch(r"^You frown(| at [a-zA-Z`\s]+)\.$", line) is not None:
            return "emote_frown_you"
        elif re.fullmatch(r"^[a-zA-Z]+ frowns(| at [a-zA-Z`\s]+)\.$", line) is not None:
            return "emote_frown_other"
        elif (
            re.fullmatch(
                r"^You gasp (in astonishment|at [a-zA-Z`\s]+ in astonishment)\.$",
                line,
            )
            is not None
        ):
            return "emote_gasp_you"
        elif (
            re.fullmatch(
                r"^[a-zA-Z]+ gasps (in astonishment|at [a-zA-Z`\s]+ in astonishment)\.$",
                line,
            )
            is not None
        ):
            return "emote_gasp_other"
        elif re.fullmatch(r"^You (giggle|giggle at [a-zA-Z`\s]+)\.$", line) is not None:
            return "emote_giggle_you"
        elif (
            re.fullmatch(r"^[a-zA-Z]+ (giggles|giggles at [a-zA-Z`\s]+)\.$", line)
            is not None
        ):
            return "emote_giggle_other"
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
        elif re.fullmatch(r"^[a-zA-Z]+ grins evilly\.$", line) is not None:
            return "emote_grin_other"
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
        elif re.fullmatch(r"^[a-zA-Z]+ hugs [a-zA-Z`\s]+\.$", line) is not None:
            return "emote_hug_other"
        elif (
            re.fullmatch(
                r"^You introduce (yourself\.  Hi there\!|[a-zA-Z`\s]+\.)$",
                line,
            )
            is not None
        ):
            return "emote_introduce_you"
        elif (
            re.fullmatch(
                r"^[a-zA-Z]+ introduces ((himself|herself)\.  Hi there\!|[a-zA-Z`\s]+\.)$",
                line,
            )
            is not None
        ):
            return "emote_introduce_other"
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
                r"^([a-zA-Z]+ blows a kiss into the air|[a-zA-Z]+ kisses [a-zA-Z`\s]+ on the cheek)\.$",
                line,
            )
            is not None
        ):
            return "emote_kiss_other"
        elif (
            re.fullmatch(
                r"^You kneel (down|before [a-zA-Z`\s]+ in humility and reverence)\.$",
                line,
            )
            is not None
        ):
            return "emote_kneel_you"
        elif (
            re.fullmatch(
                r"^[a-zA-Z]+ kneels (down|before [a-zA-Z`\s]+ in humility and reverence)\.$",
                line,
            )
            is not None
        ):
            return "emote_kneel_other"
        elif (
            re.fullmatch(r"^(You laugh|You laugh at [a-zA-Z`\s]+)\.$", line) is not None
        ):
            return "emote_laugh_you"
        elif (
            re.fullmatch(
                r"^([a-zA-Z]+ laughs|[a-zA-Z]+ laughs at [a-zA-Z`\s]+)\.$", line
            )
            is not None
        ):
            return "emote_laugh_other"
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
        elif (
            re.fullmatch(
                r"^\w+ lowers (his|her|its) head and mourns the loss of [a-zA-Z`\s\-]\.$",
                line,
            )
            is not None
        ):
            return "emote_mourn_other"
        elif re.fullmatch(r"^(You nod\.|You nod at [a-zA-Z`\s]+\.)$", line) is not None:
            return "emote_nod_you"
        elif (
            re.fullmatch(r"^([a-zA-Z]+ nods\.|[a-zA-Z]+ nods at [a-zA-Z`\s]+\.)$", line)
            is not None
        ):
            return "emote_nod_other"
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
                r"^You pat [a-zA-Z`\s]+ on the back\.$",
                line,
            )
            is not None
        ):
            return "emote_pat_you"
        elif (
            re.fullmatch(
                r"^[a-zA-Z]+ pats [a-zA-Z`\s]+ on the back\.$",
                line,
            )
            is not None
        ):
            return "emote_pat_other"
        elif (
            re.fullmatch(
                r"^(You peer around intently|You peer at [a-zA-Z`\s]+\, looking (him|her|it|them) up and down)\.$",
                line,
            )
            is not None
        ):
            return "emote_peer_you"
        elif (
            re.fullmatch(
                r"^([a-zA-Z]+ peers around intently|[a-zA-Z]+ peers at [a-zA-Z`\s]+\, looking (him|her|it|them) up and down)\.$",
                line,
            )
            is not None
        ):
            return "emote_peer_other"
        elif (
            re.fullmatch(
                r"^You plead with (everyone around you|[a-zA-Z`\s]+ desperately)\.$",
                line,
            )
            is not None
        ):
            return "emote_plead_you"
        elif (
            re.fullmatch(
                r"^[a-zA-Z]+ pleads with (everyone around (them|him|her)|[a-zA-Z`\s]+ desperately)\.$",
                line,
            )
            is not None
        ):
            return "emote_plead_other"
        elif (
            re.fullmatch(
                r"^(You point straight ahead\.|You point at [a-zA-Z`\s]+\. Yeah you\!)$",
                line,
            )
            is not None
        ):
            return "emote_point_you"
        elif (
            re.fullmatch(
                r"^([a-zA-Z]+ points straight ahead\.|[a-zA-Z]+ points at [a-zA-Z`\s]+\. Yeah you\!)$",
                line,
            )
            is not None
        ):
            return "emote_point_other"
        elif re.fullmatch(r"^[a-zA-Z]+ pokes [a-zA-Z`\s]+\.$", line) is not None:
            return "emote_poke_other"
        elif (
            re.fullmatch(r"^(You poke yourself\.|You poke [a-zA-Z`\s]+\.)$", line)
            is not None
        ):
            return "emote_poke_you"
        elif (
            re.fullmatch(
                r"^(You ponder the matters at hand\.|You ponder [a-zA-Z`\s]+\. What is going on with (him|her|them|it)\?)$",
                line,
            )
            is not None
        ):
            return "emote_ponder_you"
        elif (
            re.fullmatch(
                r"^([a-zA-Z]+ ponders the matters at hand\.|[a-zA-Z]+ ponders [a-zA-Z`\s]+\. What is going on with (him|her|them|it)\?)$",
                line,
            )
            is not None
        ):
            return "emote_ponder_other"
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
                r"^You emit a low rumble and then roar (like a lion\!|at [a-zA-Z`\s]+\.)$",
                line,
            )
            is not None
        ):
            return "emote_roar_you"
        elif (
            re.fullmatch(
                r"^[a-zA-Z]+ emits a low rumble and then roars (like a lion\!|at [a-zA-Z`\s]+\.)$",
                line,
            )
            is not None
        ):
            return "emote_roar_other"
        elif (
            re.fullmatch(
                r"^You roll on the floor laughing(| at [a-zA-Z`\s]+)\.$",
                line,
            )
            is not None
        ):
            return "emote_rofl_you"
        elif (
            re.fullmatch(
                r"^[a-zA-Z]+ rolls on the floor laughing(| at [a-zA-Z`\s]+)\.$",
                line,
            )
            is not None
        ):
            return "emote_rofl_other"
        elif (
            re.fullmatch(
                r"^(You salute the gods in pure admiration|You snap to attention and salute [a-zA-Z`\s]+ crisply)\.$",
                line,
            )
            is not None
        ):
            return "emote_salute_you"
        elif (
            re.fullmatch(
                r"^[a-zA-Z]+ (salutes the gods in pure admiration|snaps to attention and salutes [a-zA-Z`\s]+ crisply)\.$",
                line,
            )
            is not None
        ):
            return "emote_salute_other"
        elif (
            re.fullmatch(
                r"^(You shiver\.  Brrrrrr|You shiver at the thought of messing with [a-zA-Z`\s]+)\.$",
                line,
            )
            is not None
        ):
            return "emote_shiver_you"
        elif (
            re.fullmatch(
                r"^([a-zA-Z]+ shivers\.  Brrrrrr|[a-zA-Z]+ shivers at the thought of messing with [a-zA-Z`\s]+)\.$",
                line,
            )
            is not None
        ):
            return "emote_shiver_other"
        elif (
            re.fullmatch(r"^You shrug (unknowingly|at [a-zA-Z`\s\'\-]+)\.$", line)
            is not None
        ):
            return "emote_shrug_you"
        elif (
            re.fullmatch(
                r"^[a-zA-Z]+ shrugs (unknowingly|at [a-zA-Z`\s\'\-]+)\.$", line
            )
            is not None
        ):
            return "emote_shrug_other"
        elif (
            re.fullmatch(
                r"^(You sigh\, clearly disappointed|You sigh at [a-zA-Z`\s]+)\.$",
                line,
            )
            is not None
        ):
            return "emote_sigh_you"
        elif (
            re.fullmatch(
                r"^([a-zA-Z]+ sighs\, clearly disappointed|[a-zA-Z] sighs at [a-zA-Z`\s]+)\.$",
                line,
            )
            is not None
        ):
            return "emote_sigh_other"
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
        elif (
            re.fullmatch(r"^\w+ (smiles|beams a smile at [a-zA-Z`\s]+)\.$", line)
            is not None
        ):
            return "emote_smile_other"
        elif (
            re.fullmatch(
                r"^You smirk mischievously(| at [a-zA-Z`\s]+)\.$",
                line,
            )
            is not None
        ):
            return "emote_smirk_you"
        elif (
            re.fullmatch(
                r"^[a-zA-Z]+ smirks mischievously(| at [a-zA-Z`\s]+)\.$",
                line,
            )
            is not None
        ):
            return "emote_smirk_other"
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
                r"^You tap your foot (|as you look at [a-zA-Z`\s]+ )impatiently\.$",
                line,
            )
            is not None
        ):
            return "emote_tap_you"
        elif (
            re.fullmatch(
                r"^[a-zA-Z]+ taps (his|her|its) foot (|as (he|she|it) looks at [a-zA-Z`\s]+ )impatiently\.$",
                line,
            )
            is not None
        ):
            return "emote_tap_other"
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
        elif (
            re.fullmatch(r"^[a-zA-Z]+ thanks ([a-zA-Z`\s]+ heartily|everyone)\.$", line)
            is not None
        ):
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
        elif re.fullmatch(r"^\w+ vetoes [a-zA-Z`\s]+\'s idea\!$", line) is not None:
            return "emote_veto_other"
        elif (
            re.fullmatch(r"^(You wave\.|You wave at [a-zA-Z`\s]+\.)$", line) is not None
        ):
            return "emote_wave_you"
        elif (
            re.fullmatch(r"^(\w+ waves at [a-zA-Z`\s]+\.|\w+ waves\.)$", line)
            is not None
        ):
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
                r"^(You open your mouth wide and yawn|You yawn rudely in [a-zA-Z`\s\']+ face)\.$",
                line,
            )
            is not None
        ):
            return "emote_yawn_you"
        elif (
            re.fullmatch(
                r"^([a-zA-Z]+ opens (his|her|its) mouth wide and yawns|[a-zA-Z]+ yawns rudely in [a-zA-Z`\s\']+ face)\.$",
                line,
            )
            is not None
        ):
            return "emote_yawn_other"

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
        elif (
            re.fullmatch(r"^Your who request was cut short..too many players\.$", line)
            is not None
        ):
            return "who_etc"
        elif re.fullmatch(r"^---------------------------------$", line) is not None:
            return "who_line_friends"
        elif (
            re.fullmatch(
                r"^(AFK | AFK |\<LINKDEAD\>| \<LINKDEAD\>| AFK  \<LINKDEAD\>|\* GM\-Mgmt \*|\* GM \* |\* Guide \*|)\[(\d+ [a-zA-Z\s]+|ANONYMOUS)\] \w+( \([a-zA-Z\s]+\)|)( \<[a-zA-Z`\s\']+\>|  \<[a-zA-Z`\s\']+\>|)( ZONE\: \w+|  ZONE\: \w+| ZONE\:|  ZONE\:|)( LFG|  LFG|   LFG|)$",
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
    print("Test Here")
