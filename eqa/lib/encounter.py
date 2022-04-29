#! /usr/bin/env python

"""
   Program:   EQ Alert
   File Name: eqa/lib/encounter.py
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

   Parse and react to eqemu logs
"""

import re
import sys
import time

import eqa.lib.settings as eqa_settings


def process(
    config, base_path, encounter_q, system_q, display_q, exit_flag, cfg_reload, state
):
    """
    Process: encounter_q
    Produce: display_q, system_q
    """

    encounter_stack = []
    active_encounter = False
    detect_encounter = True

    try:
        while not exit_flag.is_set() and not cfg_reload.is_set():

            # Sleep between empty checks
            if encounter_q.qsize() < 1:
                time.sleep(0.01)

            # Check queue for message
            if not encounter_q.empty():
                new_message = encounter_q.get()
                line_type = new_message.type
                line_time = new_message.timestamp
                interaction = new_message.tx
                line = new_message.payload

                if active_encounter == False:
                    if (
                        interaction == "combat"
                        or line_type == "spell_damage"
                        or line_type == "spell_resist_you"
                        or line_type == "you_auto_attack_on"
                        or line_type == "you_auto_attack_off"
                        or line_type == "engage"
                    ):
                        active_encounter = True
                else:
                    if interaction == "stop" or line_type == "you_new_zone":
                        active_encounter = False
                        encounter_report(
                            line_type, line_time, line, encounter_stack, state
                        )
                        encounter_stack.clear()

                if active_encounter == True:
                    if interaction == "combat":
                        encounter_combat(
                            line_type, line_time, line, encounter_stack, state
                        )
                    elif interaction == "spell":
                        encounter_spell(
                            line_type, line_time, line, encounter_stack, state
                        )

                encounter_q.task_done()

        sys.exit(0)

    except Exception as e:
        eqa_settings.log(
            "encounter: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def encounter_combat(line_type, line_time, line, encounter_stack, state):
    """Handle combat lines for encounters"""

    try:

        source = None
        target = None
        mode = None
        result = None

        if line_type == "combat_other_melee":
            mode = "damage"
            if " mauls " in line:
                source, sans_source = line.split(" mauls ")
                target, extra = sans_source.split(" for ")
                if target == "YOU":
                    target = state.char
                result = extra.split(" ")[0]
            elif " hits " in line:
                source, sans_source = line.split(" hits ")
                target, extra = sans_source.split(" for ")
                if target == "YOU":
                    target = state.char
                result = extra.split(" ")[0]
            elif " crushes " in line:
                source, sans_source = line.split(" crushes ")
                target, extra = sans_source.split(" for ")
                if target == "YOU":
                    target = state.char
                result = extra.split(" ")[0]
            elif " slashes " in line:
                source, sans_source = line.split(" slashes ")
                target, extra = sans_source.split(" for ")
                if target == "YOU":
                    target = state.char
                result = extra.split(" ")[0]
            elif " pierces " in line:
                source, sans_source = line.split(" pierces ")
                target, extra = sans_source.split(" for ")
                if target == "YOU":
                    target = state.char
                result = extra.split(" ")[0]
            elif " bashes " in line:
                source, sans_source = line.split(" bashes ")
                target, extra = sans_source.split(" for ")
                if target == "YOU":
                    target = state.char
                result = extra.split(" ")[0]
            elif " backstabs " in line:
                source, sans_source = line.split(" backstabs ")
                target, extra = sans_source.split(" for ")
                if target == "YOU":
                    target = state.char
                result = extra.split(" ")[0]
            elif " bites " in line:
                source, sans_source = line.split(" bites ")
                target, extra = sans_source.split(" for ")
                if target == "YOU":
                    target = state.char
                result = extra.split(" ")[0]
            elif " kicks " in line:
                source, sans_source = line.split(" kicks ")
                target, extra = sans_source.split(" for ")
                if target == "YOU":
                    target = state.char
                result = extra.split(" ")[0]
            elif " claws " in line:
                source, sans_source = line.split(" claws ")
                target, extra = sans_source.split(" for ")
                if target == "YOU":
                    target = state.char
                result = extra.split(" ")[0]
            elif " gores " in line:
                source, sans_source = line.split(" gores ")
                target, extra = sans_source.split(" for ")
                if target == "YOU":
                    target = state.char
                result = extra.split(" ")[0]
            elif " punches " in line:
                source, sans_source = line.split(" punches ")
                target, extra = sans_source.split(" for ")
                if target == "YOU":
                    target = state.char
                result = extra.split(" ")[0]
            elif " strikes " in line:
                source, sans_source = line.split(" strikes ")
                target, extra = sans_source.split(" for ")
                if target == "YOU":
                    target = state.char
                result = extra.split(" ")[0]
            elif " slices " in line:
                source, sans_source = line.split(" slices ")
                target, extra = sans_source.split(" for ")
                if target == "YOU":
                    target = state.char
                result = extra.split(" ")[0]
        elif line_type == "combat_other_melee_block":
            mode = "damage"
            if " tries to maul " in line:
                source, sans_source = line.split(" tries to maul ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "block"
            elif " tries to hit " in line:
                source, sans_source = line.split(" tries to hit ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "block"
            elif " tries to crush " in line:
                source, sans_source = line.split(" tries to crush ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "block"
            elif " tries to slash " in line:
                source, sans_source = line.split(" tries to slash ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "block"
            elif " tries to pierce " in line:
                source, sans_source = line.split(" tries to pierce ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "block"
            elif " tries to bash " in line:
                source, sans_source = line.split(" tries to bash ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "block"
            elif " tries to backstab " in line:
                source, sans_source = line.split(" tries to backstab ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "block"
            elif " tries to bite " in line:
                source, sans_source = line.split(" tries to bite ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "block"
            elif " tries to kick " in line:
                source, sans_source = line.split(" tries to kick ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "block"
            elif " tries to claw " in line:
                source, sans_source = line.split(" tries to claw ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "block"
            elif " tries to gore " in line:
                source, sans_source = line.split(" tries to gore ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "block"
            elif " tries to punch " in line:
                source, sans_source = line.split(" tries to punch ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "block"
            elif " tries to strike " in line:
                source, sans_source = line.split(" tries to strike ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "block"
            elif " tries to slice " in line:
                source, sans_source = line.split(" tries to slice ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "block"
        elif line_type == "combat_other_melee_crip_blow":
            pass
        elif line_type == "combat_other_melee_crit":
            pass
        elif line_type == "combat_other_melee_crit_kick":
            pass
        elif line_type == "you_auto_attack_off":
            pass
        elif line_type == "you_auto_attack_on":
            pass
        elif line_type == "engage":
            pass
        elif line_type == "combat_other_melee_dodge":
            mode = "damage"
            if " tries to maul " in line:
                source, sans_source = line.split(" tries to maul ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "dodge"
            elif " tries to hit " in line:
                source, sans_source = line.split(" tries to hit ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "dodge"
            elif " tries to crush " in line:
                source, sans_source = line.split(" tries to crush ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "dodge"
            elif " tries to slash " in line:
                source, sans_source = line.split(" tries to slash ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "dodge"
            elif " tries to pierce " in line:
                source, sans_source = line.split(" tries to pierce ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "dodge"
            elif " tries to bash " in line:
                source, sans_source = line.split(" tries to bash ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "dodge"
            elif " tries to backstab " in line:
                source, sans_source = line.split(" tries to backstab ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "dodge"
            elif " tries to bite " in line:
                source, sans_source = line.split(" tries to bite ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "dodge"
            elif " tries to kick " in line:
                source, sans_source = line.split(" tries to kick ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "dodge"
            elif " tries to claw " in line:
                source, sans_source = line.split(" tries to claw ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "dodge"
            elif " tries to gore " in line:
                source, sans_source = line.split(" tries to gore ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "dodge"
            elif " tries to punch " in line:
                source, sans_source = line.split(" tries to punch ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "dodge"
            elif " tries to strike " in line:
                source, sans_source = line.split(" tries to strike ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "dodge"
            elif " tries to slice " in line:
                source, sans_source = line.split(" tries to slice ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "dodge"
        elif line_type == "combat_other_melee_invulnerable":
            mode = "damage"
            if " tries to maul " in line:
                source, sans_source = line.split(" tries to maul ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "invulnerable"
            elif " tries to hit " in line:
                source, sans_source = line.split(" tries to hit ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "invulnerable"
            elif " tries to crush " in line:
                source, sans_source = line.split(" tries to crush ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "invulnerable"
            elif " tries to slash " in line:
                source, sans_source = line.split(" tries to slash ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "invulnerable"
            elif " tries to pierce " in line:
                source, sans_source = line.split(" tries to pierce ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "invulnerable"
            elif " tries to bash " in line:
                source, sans_source = line.split(" tries to bash ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "invulnerable"
            elif " tries to backstab " in line:
                source, sans_source = line.split(" tries to backstab ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "invulnerable"
            elif " tries to bite " in line:
                source, sans_source = line.split(" tries to bite ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "invulnerable"
            elif " tries to kick " in line:
                source, sans_source = line.split(" tries to kick ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "invulnerable"
            elif " tries to claw " in line:
                source, sans_source = line.split(" tries to claw ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "invulnerable"
            elif " tries to gore " in line:
                source, sans_source = line.split(" tries to gore ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "invulnerable"
            elif " tries to punch " in line:
                source, sans_source = line.split(" tries to punch ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "invulnerable"
            elif " tries to strike " in line:
                source, sans_source = line.split(" tries to strike ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "invulnerable"
            elif " tries to slice " in line:
                source, sans_source = line.split(" tries to slice ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "invulnerable"
        elif line_type == "combat_other_melee_miss":
            mode = "damage"
            if " tries to maul " in line:
                source, sans_source = line.split(" tries to maul ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "miss"
            elif " tries to hit " in line:
                source, sans_source = line.split(" tries to hit ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "miss"
            elif " tries to crush " in line:
                source, sans_source = line.split(" tries to crush ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "miss"
            elif " tries to slash " in line:
                source, sans_source = line.split(" tries to slash ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "miss"
            elif " tries to pierce " in line:
                source, sans_source = line.split(" tries to pierce ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "miss"
            elif " tries to bash " in line:
                source, sans_source = line.split(" tries to bash ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "miss"
            elif " tries to backstab " in line:
                source, sans_source = line.split(" tries to backstab ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "miss"
            elif " tries to bite " in line:
                source, sans_source = line.split(" tries to bite ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "miss"
            elif " tries to kick " in line:
                source, sans_source = line.split(" tries to kick ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "miss"
            elif " tries to claw " in line:
                source, sans_source = line.split(" tries to claw ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "miss"
            elif " tries to gore " in line:
                source, sans_source = line.split(" tries to gore ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "miss"
            elif " tries to punch " in line:
                source, sans_source = line.split(" tries to punch ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "miss"
            elif " tries to strike " in line:
                source, sans_source = line.split(" tries to strike ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "miss"
            elif " tries to slice " in line:
                source, sans_source = line.split(" tries to slice ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "miss"
        elif line_type == "combat_other_melee_parry":
            mode = "damage"
            if " tries to maul " in line:
                source, sans_source = line.split(" tries to maul ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "parry"
            elif " tries to hit " in line:
                source, sans_source = line.split(" tries to hit ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "parry"
            elif " tries to crush " in line:
                source, sans_source = line.split(" tries to crush ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "parry"
            elif " tries to slash " in line:
                source, sans_source = line.split(" tries to slash ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "parry"
            elif " tries to pierce " in line:
                source, sans_source = line.split(" tries to pierce ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "parry"
            elif " tries to bash " in line:
                source, sans_source = line.split(" tries to bash ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "parry"
            elif " tries to backstab " in line:
                source, sans_source = line.split(" tries to backstab ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "parry"
            elif " tries to bite " in line:
                source, sans_source = line.split(" tries to bite ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "parry"
            elif " tries to kick " in line:
                source, sans_source = line.split(" tries to kick ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "parry"
            elif " tries to claw " in line:
                source, sans_source = line.split(" tries to claw ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "parry"
            elif " tries to gore " in line:
                source, sans_source = line.split(" tries to gore ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "parry"
            elif " tries to punch " in line:
                source, sans_source = line.split(" tries to punch ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "parry"
            elif " tries to strike " in line:
                source, sans_source = line.split(" tries to strike ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "parry"
            elif " tries to slice " in line:
                source, sans_source = line.split(" tries to slice ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "parry"
        elif line_type == "combat_other_melee_reposte":
            mode = "damage"
            if " tries to maul " in line:
                source, sans_source = line.split(" tries to maul ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "riposte"
            elif " tries to hit " in line:
                source, sans_source = line.split(" tries to hit ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "riposte"
            elif " tries to crush " in line:
                source, sans_source = line.split(" tries to crush ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "riposte"
            elif " tries to slash " in line:
                source, sans_source = line.split(" tries to slash ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "riposte"
            elif " tries to pierce " in line:
                source, sans_source = line.split(" tries to pierce ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "riposte"
            elif " tries to bash " in line:
                source, sans_source = line.split(" tries to bash ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "riposte"
            elif " tries to backstab " in line:
                source, sans_source = line.split(" tries to backstab ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "riposte"
            elif " tries to bite " in line:
                source, sans_source = line.split(" tries to bite ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "riposte"
            elif " tries to kick " in line:
                source, sans_source = line.split(" tries to kick ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "riposte"
            elif " tries to claw " in line:
                source, sans_source = line.split(" tries to claw ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "riposte"
            elif " tries to gore " in line:
                source, sans_source = line.split(" tries to gore ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "riposte"
            elif " tries to punch " in line:
                source, sans_source = line.split(" tries to punch ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "riposte"
            elif " tries to strike " in line:
                source, sans_source = line.split(" tries to strike ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "riposte"
            elif " tries to slice " in line:
                source, sans_source = line.split(" tries to slice ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "riposte"
        elif line_type == "combat_other_rune_damage":
            mode = "damage"
            if " tries to maul " in line:
                source, sans_source = line.split(" tries to maul ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "rune"
            elif " tries to hit " in line:
                source, sans_source = line.split(" tries to hit ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "rune"
            elif " tries to crush " in line:
                source, sans_source = line.split(" tries to crush ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "rune"
            elif " tries to slash " in line:
                source, sans_source = line.split(" tries to slash ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "rune"
            elif " tries to pierce " in line:
                source, sans_source = line.split(" tries to pierce ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "rune"
            elif " tries to bash " in line:
                source, sans_source = line.split(" tries to bash ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "rune"
            elif " tries to backstab " in line:
                source, sans_source = line.split(" tries to backstab ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "rune"
            elif " tries to bite " in line:
                source, sans_source = line.split(" tries to bite ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "rune"
            elif " tries to kick " in line:
                source, sans_source = line.split(" tries to kick ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "rune"
            elif " tries to claw " in line:
                source, sans_source = line.split(" tries to claw ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "rune"
            elif " tries to gore " in line:
                source, sans_source = line.split(" tries to gore ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "rune"
            elif " tries to punch " in line:
                source, sans_source = line.split(" tries to punch ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "rune"
            elif " tries to strike " in line:
                source, sans_source = line.split(" tries to strike ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "rune"
            elif " tries to slice " in line:
                source, sans_source = line.split(" tries to slice ")
                target, extra = sans_source.split(",")
                if target == "YOU":
                    target = state.char
                result = "rune"
        elif line_type == "combat_you_melee":
            mode = "damage"
            if " maul " in line:
                source, sans_source = line.split(" maul ")
                source = state.char
                target, extra = sans_source.split(" for ")
                result = extra.split(" ")[0]
            elif " hit " in line:
                source, sans_source = line.split(" hit ")
                source = state.char
                target, extra = sans_source.split(" for ")
                result = extra.split(" ")[0]
            elif " crush " in line:
                source, sans_source = line.split(" crush ")
                source = state.char
                target, extra = sans_source.split(" for ")
                result = extra.split(" ")[0]
            elif " slash " in line:
                source, sans_source = line.split(" slash ")
                source = state.char
                target, extra = sans_source.split(" for ")
                result = extra.split(" ")[0]
            elif " pierce " in line:
                source, sans_source = line.split(" pierce ")
                source = state.char
                target, extra = sans_source.split(" for ")
                result = extra.split(" ")[0]
            elif " bash " in line:
                source, sans_source = line.split(" bash ")
                source = state.char
                target, extra = sans_source.split(" for ")
                result = extra.split(" ")[0]
            elif " backstab " in line:
                source, sans_source = line.split(" backstab ")
                source = state.char
                target, extra = sans_source.split(" for ")
                result = extra.split(" ")[0]
            elif " bite " in line:
                source, sans_source = line.split(" bite ")
                source = state.char
                target, extra = sans_source.split(" for ")
                result = extra.split(" ")[0]
            elif " kick " in line:
                source, sans_source = line.split(" kick ")
                source = state.char
                target, extra = sans_source.split(" for ")
                result = extra.split(" ")[0]
            elif " claw " in line:
                source, sans_source = line.split(" claw ")
                source = state.char
                target, extra = sans_source.split(" for ")
                result = extra.split(" ")[0]
            elif " gore " in line:
                source, sans_source = line.split(" gore ")
                source = state.char
                target, extra = sans_source.split(" for ")
                result = extra.split(" ")[0]
            elif " punch " in line:
                source, sans_source = line.split(" punch ")
                source = state.char
                target, extra = sans_source.split(" for ")
                result = extra.split(" ")[0]
            elif " strike " in line:
                source, sans_source = line.split(" strike ")
                source = state.char
                target, extra = sans_source.split(" for ")
                result = extra.split(" ")[0]
            elif " slice " in line:
                source, sans_source = line.split(" slice ")
                source = state.char
                target, extra = sans_source.split(" for ")
                result = extra.split(" ")[0]
        elif line_type == "combat_you_melee_miss":
            mode = "damage"
            if " try to maul " in line:
                source, sans_source = line.split(" try to maul ")
                source = state.char
                target, extra = sans_source.split(",")
                result = "miss"
            elif " try to hit " in line:
                source, sans_source = line.split(" try to hit ")
                source = state.char
                target, extra = sans_source.split(",")
                result = "miss"
            elif " try to crush " in line:
                source, sans_source = line.split(" try to crush ")
                source = state.char
                target, extra = sans_source.split(",")
                result = "miss"
            elif " try to slash " in line:
                source, sans_source = line.split(" try to slash ")
                source = state.char
                target, extra = sans_source.split(",")
                result = "miss"
            elif " try to pierce " in line:
                source, sans_source = line.split(" try to pierce ")
                source = state.char
                target, extra = sans_source.split(",")
                result = "miss"
            elif " try to bash " in line:
                source, sans_source = line.split(" try to bash ")
                source = state.char
                target, extra = sans_source.split(",")
                result = "miss"
            elif " try to backstab " in line:
                source, sans_source = line.split(" try to backstab ")
                source = state.char
                target, extra = sans_source.split(",")
                result = "miss"
            elif " try to bite " in line:
                source, sans_source = line.split(" try to bite ")
                source = state.char
                target, extra = sans_source.split(",")
                result = "miss"
            elif " try to kick " in line:
                source, sans_source = line.split(" try to kick ")
                source = state.char
                target, extra = sans_source.split(",")
                result = "miss"
            elif " try to claw " in line:
                source, sans_source = line.split(" try to claw ")
                source = state.char
                target, extra = sans_source.split(",")
                result = "miss"
            elif " try to gore " in line:
                source, sans_source = line.split(" try to gore ")
                source = state.char
                target, extra = sans_source.split(",")
                result = "miss"
            elif " try to punch " in line:
                source, sans_source = line.split(" try to punch ")
                source = state.char
                target, extra = sans_source.split(",")
                result = "miss"
            elif " try to strike " in line:
                source, sans_source = line.split(" try to strike ")
                source = state.char
                target, extra = sans_source.split(",")
                result = "miss"
            elif " try to slice " in line:
                source, sans_source = line.split(" try to slice ")
                source = state.char
                target, extra = sans_source.split(",")
                result = "miss"
        elif line_type == "combat_you_receive_melee":
            mode = "damage"
            if " mauls " in line:
                source, sans_source = line.split(" mauls ")
                target, extra = sans_source.split(" for ")
                target = state.char
                result = extra.split(" ")[0]
            elif " hits " in line:
                source, sans_source = line.split(" hits ")
                target, extra = sans_source.split(" for ")
                target = state.char
                result = extra.split(" ")[0]
            elif " crushes " in line:
                source, sans_source = line.split(" crushes ")
                target, extra = sans_source.split(" for ")
                target = state.char
                result = extra.split(" ")[0]
            elif " slashes " in line:
                source, sans_source = line.split(" slashes ")
                target, extra = sans_source.split(" for ")
                target = state.char
                result = extra.split(" ")[0]
            elif " pierces " in line:
                source, sans_source = line.split(" pierces ")
                target, extra = sans_source.split(" for ")
                target = state.char
                result = extra.split(" ")[0]
            elif " bashes " in line:
                source, sans_source = line.split(" bashes ")
                target, extra = sans_source.split(" for ")
                target = state.char
                result = extra.split(" ")[0]
            elif " backstabs " in line:
                source, sans_source = line.split(" backstabs ")
                target, extra = sans_source.split(" for ")
                target = state.char
                result = extra.split(" ")[0]
            elif " bites " in line:
                source, sans_source = line.split(" bites ")
                target, extra = sans_source.split(" for ")
                target = state.char
                result = extra.split(" ")[0]
            elif " kicks " in line:
                source, sans_source = line.split(" kicks ")
                target, extra = sans_source.split(" for ")
                target = state.char
                result = extra.split(" ")[0]
            elif " claws " in line:
                source, sans_source = line.split(" claws ")
                target, extra = sans_source.split(" for ")
                target = state.char
                result = extra.split(" ")[0]
            elif " gores " in line:
                source, sans_source = line.split(" gores ")
                target, extra = sans_source.split(" for ")
                target = state.char
                result = extra.split(" ")[0]
            elif " punches " in line:
                source, sans_source = line.split(" punches ")
                target, extra = sans_source.split(" for ")
                target = state.char
                result = extra.split(" ")[0]
            elif " strikes " in line:
                source, sans_source = line.split(" strikes ")
                target, extra = sans_source.split(" for ")
                target = state.char
                result = extra.split(" ")[0]
            elif " slices " in line:
                source, sans_source = line.split(" slices ")
                target, extra = sans_source.split(" for ")
                target = state.char
                result = extra.split(" ")[0]

        # Add to encounter stack
        if (
            source is not None
            and target is not None
            and mode is not None
            and result is not None
        ):
            encounter_stack.append(
                (line_time, source.title(), target.title(), mode, result)
            )
        elif state.debug == "true":
            eqa_settings.log(
                "encounter combat ["
                + line_type
                + "] not added to encounter stack: "
                + line
            )

    except Exception as e:
        eqa_settings.log(
            "encounter combat: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def encounter_spell(line_type, line_time, line, encounter_stack, state):
    """Handle spell lines for encounters"""

    try:
        source = None
        target = None
        mode = None
        result = None

        if line_type == "spell_heal_you":
            mode = "heal"
            source, sans_source = line.split(" have healed ")
            source = state.char
            target, extra = sans_source.split(" for ")
            result = extra.split(" ")[0]
        elif line_type == "spell_cast_other":
            pass
        elif line_type == "spell_cast_you":
            pass
        elif line_type == "spell_cast_item_you":
            pass
        elif line_type == "spell_fizzle_other":
            pass
        elif line_type == "spell_fizzle_you":
            pass
        elif line_type == "spell_not_hold":
            pass
        elif line_type == "spell_cast_oom":
            pass
        elif line_type == "spell_interrupt_other":
            pass
        elif line_type == "spell_interrupt_you":
            pass
        elif line_type == "spell_recover_other":
            pass
        elif line_type == "spell_recover_you":
            pass
        elif line_type == "spell_resist_you":
            pass
        elif line_type == "spell_damage":
            mode = "spell"
            if "was" in line:
                source = state.char
                target, sans_target = line.split(" was ")
                result = re.findall(r"\d+", line)[0]
            elif "were" in line:
                source = "unknown"
                target = state.char
                result = re.findall(r"\d+", line)[0]
        elif line_type == "spell_memorize_begin":
            pass
        elif line_type == "spell_memorize_finish":
            pass
        elif line_type == "spell_memorize_already":
            pass
        elif line_type == "spell_forget":
            pass
        elif line_type == "spell_worn_off":
            pass
        elif line_type == "spell_protected":
            pass
        elif line_type == "spell_cooldown_active":
            pass
        elif line_type == "spell_sitting":
            pass
        elif line_type == "spell_no_target":
            pass
        elif line_type == "spell_regen_on_other":
            pass
        elif line_type == "spell_regen_on_you":
            pass
        elif line_type == "spell_sow_on_you":
            pass
        elif line_type == "spell_sow_off_you":
            pass
        elif line_type == "spell_invis_on_you":
            pass
        elif line_type == "spell_invis_off_you":
            pass
        elif line_type == "spell_invis_dropping_you":
            pass
        elif line_type == "spell_levitate_on_you":
            pass
        elif line_type == "spell_levitate_dropping_you":
            pass
        elif line_type == "spell_levitate_off_you":
            pass
        elif line_type == "spell_cured_other":
            pass
        elif line_type == "spell_summoned_you":
            pass
        elif line_type == "spell_slow_on":
            pass
        elif line_type == "spell_bind_you":
            pass
        elif line_type == "spell_gate_collapse":
            pass

        # Add to encounter stack
        if (
            source is not None
            and target is not None
            and mode is not None
            and result is not None
        ):
            encounter_stack.append(
                (line_time, source.title(), target.title(), mode, result)
            )
        elif state.debug == "true":
            eqa_settings.log(
                "encounter spell ["
                + line_type
                + "] not added to encounter stack: "
                + line
            )

    except Exception as e:
        eqa_settings.log(
            "encounter spell: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def encounter_report(line_type, line_time, line, encounter_stack, state):
    """Report encounter stats"""

    try:

        eqa_settings.log("--- encounter stack contents ---")
        eqa_settings.log("Total events: " + str(len(encounter_stack)))
        if line_type == "mob_slain_other":
            line_clean = re.sub(r"[^\w\s\,\-\'\`]", "", line)
            target, source = line_clean.split(" has been slain by ")
            mode = "slain"
            result = "dead"
        elif line_type == "mob_slain_you":
            line_clean = re.sub(r"[^\w\s\,\-\'\`]", "", line)
            source, target = line_clean.split(" have slain ")
            source = state.char
            mode = "slain"
            result = "dead"
        elif line_type == "you_new_zone":
            pass
        elif line_type == "faction_line":
            pass

        # Generate Encounter log
        if len(encounter_stack) > 10:
            target_count = {}
            target_damage = {}

            ## Determine Encounter Target
            for event in encounter_stack:
                time, source, target, mode, result = event
                eqa_settings.log(
                    time + " [" + source + " -> " + target + "] " + mode + " " + result
                )

                ### Build target count
                if target not in target_count.keys():
                    target_count[target] = 0
                else:
                    targetted = int(target_count.get(str(target)))
                    targetted += 1
                    target_count[target] = targetted

            ## Read target count
            high_count = 0
            for target in target_count.keys():
                if high_count < int(target_count.get(str(target))):
                    high_count = int(target_count.get(str(target)))
                    encounter_target = str(target)

            ## Encounter Target
            if state.debug == "true":
                eqa_settings.log("Target: " + encounter_target)

            ## Encounter Report
            for event in encounter_stack:
                time, source, target, mode, result = event
                ### If event targets encounter target
                if target == encounter_target:
                    if source not in target_damage.keys():
                        if mode == "damage" or mode == "spell":
                            if not (
                                result == "block"
                                or result == "dodge"
                                or result == "invulnerable"
                                or result == "miss"
                                or result == "parry"
                                or result == "riposte"
                                or result == "rune"
                            ):
                                target_damage[source] = int(result)
                    else:
                        if mode == "damage" or mode == "spell":
                            if not (
                                result == "block"
                                or result == "dodge"
                                or result == "invulnerable"
                                or result == "miss"
                                or result == "parry"
                                or result == "riposte"
                                or result == "rune"
                            ):
                                total_dmg = int(target_damage.get(source)) + int(result)
                                target_damage[source] = total_dmg

            eqa_settings.log("--- encounter summary ---")
            for attacker in target_damage.keys():
                eqa_settings.log(attacker + ": " + str(target_damage.get(attacker)))

        encounter_stack.clear()

    except Exception as e:
        eqa_settings.log(
            "encounter stop: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


if __name__ == "__main__":
    main()
