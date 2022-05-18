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
import os
import json
from datetime import datetime
from collections import deque
import pkg_resources

import eqa.lib.settings as eqa_settings
import eqa.lib.struct as eqa_struct


def process(
    config, base_path, encounter_q, system_q, display_q, exit_flag, cfg_reload, state
):
    """
    Process: encounter_q
    Produce: display_q, system_q
    """

    encounter_stack = deque([])
    active_encounter = False

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

                ## Check for encounter_stack clear
                if interaction == "clear":
                    encounter_stack.clear()

                ## If not an active encounter
                if active_encounter == False:
                    ### And we see a line that indicates an encounter
                    if (
                        interaction == "combat"
                        or line_type == "spell_damage"
                        or line_type == "spell_resist_you"
                        or line_type == "you_auto_attack_on"
                    ):
                        #### Set active encounter
                        active_encounter = True
                ## Or if active encounter
                else:
                    ### And we see a line that indicates an encounter ends
                    if interaction == "stop":
                        #### Disable active encounter
                        active_encounter = False
                        #### Generate combat report and reset encounter stack
                        ##### Only care about this end trigger if we know its an NPC
                        if line_type == "mob_slain_other":
                            line_clean = re.sub(r"[^\w\s\,\-\'\`]", "", line)
                            target, source = line_clean.split(" has been slain by ")
                            if len(target.split()) > 1:
                                encounter_report(
                                    line_type,
                                    line_time,
                                    line,
                                    encounter_stack,
                                    state,
                                    config,
                                    display_q,
                                )
                            else:
                                encounter_stack.append(
                                    (
                                        line_time,
                                        source.title(),
                                        target.title(),
                                        "slain",
                                        "other",
                                    )
                                )
                        else:
                            encounter_report(
                                line_type,
                                line_time,
                                line,
                                encounter_stack,
                                state,
                                config,
                                display_q,
                            )

                    if line_type == "you_new_zone":
                        encounter_stack.clear()

                    elif interaction == "end":
                        encounter_report(
                            line_type,
                            line_time,
                            line,
                            encounter_stack,
                            state,
                            config,
                            display_q,
                        )

                    elif interaction == "start":
                        #### Set active encounter
                        active_encounter = True

                ## If we're in an encounter
                if active_encounter == True:
                    ### Add combat or spell events to the stack
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
            mode = "spell"
            source, sans_source = line.split(" begins to cast ")
            target = "unknown"
            result = "cast"
        elif line_type == "spell_cast_you":
            mode = "spell"
            source = state.char
            target = "unknown"
            result = "cast"
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


def encounter_report(
    line_type, line_time, line, encounter_stack, state, config, display_q
):
    """Report encounter stats"""

    try:

        slain_encounter_target = None

        if line_type == "mob_slain_other":
            line_clean = re.sub(r"[^\w\s\,\-\'\`]", "", line)
            target, source = line_clean.split(" has been slain by ")
            slain_encounter_target = target.title()
        elif line_type == "mob_slain_you":
            line_clean = re.sub(r"[^\w\s\,\-\'\`]", "", line)
            source, target = line_clean.split(" have slain ")
            slain_encounter_target = target.title()
        elif line_type == "you_new_zone":
            pass
        elif line_type == "faction_line":
            pass

        # Encounter Report
        encounter_stack_events = len(encounter_stack)
        if encounter_stack_events > 20:
            target_count = {}
            this_encounter = deque([])
            not_this_encounter = deque([])

            ## Either Know the Encounter Target
            if slain_encounter_target is not None:
                encounter_target = slain_encounter_target
            ## Or Determine Encounter Target
            else:
                for event in encounter_stack:
                    time, source, target, mode, result = event

                    ### Build target count
                    if target not in target_count.keys():
                        target_count[target] = 0
                    else:
                        targetted = int(target_count.get(str(target)))
                        targetted += 1
                        target_count[target] = targetted

                ## Determine Encounter Target
                high_count = 0
                for target in target_count.keys():
                    if target != "Unknown" and target != state.char:
                        if high_count < int(target_count.get(str(target))):
                            high_count = int(target_count.get(str(target)))
                            encounter_target = str(target)

            ## Check / Set Encounter Parse Directory
            encounter_parse_time = datetime.now().strftime("%H-%M-%s")
            encounter_parse_date = datetime.now().strftime("%Y-%m-%d")

            encounter_path = config["settings"]["paths"]["encounter"]
            clean_zone = re.sub(r"[^\w\s]", "", state.zone)
            if not os.path.exists(encounter_path):
                os.makedirs(encounter_path)
            encounter_zone_path = (
                encounter_path + clean_zone.lower().replace(" ", "-") + "/"
            )
            if not os.path.exists(encounter_zone_path):
                os.makedirs(encounter_zone_path)
            encounter_zone_date_path = encounter_zone_path + encounter_parse_date + "/"
            if not os.path.exists(encounter_zone_date_path):
                os.makedirs(encounter_zone_date_path)

            ## Set Encounter Parse Filename
            encounter_filename = (
                encounter_parse_time
                + "_"
                + encounter_target.lower().replace(" ", "-")
                + ".json"
            )

            ## Determine Encounter Duration
            ### Find end time
            found_time = False
            (
                last_time,
                last_source,
                last_target,
                last_mode,
                last_result,
            ) = encounter_stack[-1]
            last_hour, last_minute, last_second_m = last_time.split(":")
            last_second, last_milli = last_second_m.split(".")
            encounter_end_time = datetime(
                2020, 12, 30, int(last_hour), int(last_minute), int(last_second)
            )

            ## Find start time and build this_encounter
            count = 0
            while count < len(encounter_stack):
                event = encounter_stack.popleft()
                time, source, target, mode, result = event
                if (
                    not found_time
                    and source == encounter_target
                    or not found_time
                    and target == encounter_target
                ):
                    found_time = True
                    (
                        first_time,
                        first_source,
                        first_target,
                        first_mode,
                        first_result,
                    ) = event
                    first_hour, first_minute, first_second_m = first_time.split(":")
                    first_second, first_milli = first_second_m.split(".")
                    encounter_start_time = datetime(
                        2020,
                        12,
                        30,
                        int(first_hour),
                        int(first_minute),
                        int(first_second),
                    )
                    this_encounter.append(event)
                else:
                    not_this_encounter.append(event)
                if (
                    found_time
                    and source == encounter_target
                    or found_time
                    and target == encounter_target
                    or found_time
                    and source == "Unknown"
                    or found_time
                    and target == "Unknown"
                ):
                    this_encounter.append(event)
                else:
                    not_this_encounter.append(event)

            encounter_stack = not_this_encounter
            encounter_duration = int(
                (encounter_end_time - encounter_start_time).total_seconds()
            )
            ### Spot check duration weirdness over midnight
            if int(encounter_duration) < 0:
                first_half = (
                    datetime(2020, 12, 30, 23, 59, 59) - encounter_start_time
                ).total_seconds()
                last_half = encounter_end_time.total_seconds()
                encounter_duration = int(first_half + last_half)

            ## Scrape This Encounter Events
            pet_and_target_same = False
            this_encounter_events = len(this_encounter)
            target_melee_damage_recieved = {}
            target_melee_damage_done = {}
            target_spell_damage_recieved = {}
            target_spell_damage_done = {}
            encounter_target_damage_total = {}
            encounter_target_damage_done_total = {}
            encounter_target_spell_total = {}
            encounter_target_spell_done_total = {}
            target_block = {}
            target_dodge = {}
            target_invulnerable = {}
            target_miss = {}
            target_parry = {}
            target_riposte = {}
            target_rune = {}
            source_block = {}
            source_dodge = {}
            source_invulnerable = {}
            source_miss = {}
            source_parry = {}
            source_riposte = {}
            source_rune = {}
            encounter_activity = {}
            encounter_heals = {}
            encounter_casts = {}
            target_killed = {}
            killed_by_target = {}

            for event in this_encounter:
                time, source, target, mode, result = event

                # Track activity for source
                if source not in encounter_activity.keys():
                    encounter_activity[source] = 1
                else:
                    encounter_activity[source] += 1

                ### If mode is damage
                if mode == "damage":
                    if target == encounter_target:
                        if target == source:
                            pet_and_target_same = True
                        if result == "block":
                            if target not in target_block.keys():
                                target_block[target] = 1
                            else:
                                target_block[target] += 1
                        elif result == "dodge":
                            if target not in target_dodge.keys():
                                target_dodge[target] = 1
                            else:
                                target_dodge[target] += 1
                        elif result == "invulnerable":
                            if target not in target_invulnerable.keys():
                                target_invulnerable[target] = 1
                            else:
                                target_invulnerable[target] += 1
                        elif result == "miss":
                            if source not in source_miss.keys():
                                source_miss[source] = 1
                            else:
                                source_miss[source] += 1
                        elif result == "parry":
                            if target not in target_parry.keys():
                                target_parry[target] = 1
                            else:
                                target_parry[target] += 1
                        elif result == "riposte":
                            if target not in target_riposte.keys():
                                target_riposte[target] = 1
                            else:
                                target_riposte[target] += 1
                        elif result == "rune":
                            if target not in target_rune.keys():
                                target_rune[target] = 1
                            else:
                                target_rune[target] += 1
                        else:
                            if target not in encounter_target_damage_total.keys():
                                encounter_target_damage_total[target] = int(result)
                            else:
                                encounter_target_damage_total[target] += int(result)
                            if source not in target_melee_damage_recieved.keys():
                                target_melee_damage_recieved[source] = int(result)
                            else:
                                target_melee_damage_recieved[source] += int(result)
                    elif source == encounter_target:
                        if result == "block":
                            if source not in source_block.keys():
                                source_block[source] = 1
                            else:
                                source_block[source] += 1
                        elif result == "dodge":
                            if source not in source_dodge.keys():
                                source_dodge[source] = 1
                            else:
                                source_dodge[source] += 1
                        elif result == "invulnerable":
                            if source not in source_invulnerable.keys():
                                source_invulnerable[source] = 1
                            else:
                                source_invulnerable[source] += 1
                        elif result == "miss":
                            if target not in target_miss.keys():
                                target_miss[target] = 1
                            else:
                                target_miss[target] += 1
                        elif result == "parry":
                            if source not in source_parry.keys():
                                source_parry[source] = 1
                            else:
                                source_parry[source] += 1
                        elif result == "riposte":
                            if source not in source_riposte.keys():
                                source_riposte[source] = 1
                            else:
                                source_riposte[source] += 1
                        elif result == "rune":
                            if source not in source_rune.keys():
                                source_rune[source] = 1
                            else:
                                source_rune[source] += 1
                        else:
                            if target not in target_melee_damage_done.keys():
                                target_melee_damage_done[target] = int(result)
                            else:
                                target_melee_damage_done[target] += int(result)
                            if source not in encounter_target_damage_done_total.keys():
                                encounter_target_damage_done_total[source] = int(result)
                            else:
                                encounter_target_damage_done_total[source] += int(
                                    result
                                )
                ### If mode is spell
                elif mode == "spell":
                    if result == "cast":
                        if source not in encounter_casts.keys():
                            encounter_casts[source] = 1
                        else:
                            encounter_casts[source] += 1
                    else:
                        if source == "Unknown" and target != encounter_target:
                            source = encounter_target
                        if target == encounter_target:
                            if source not in target_spell_damage_recieved.keys():
                                target_spell_damage_recieved[source] = int(result)
                            elif source in target_spell_damage_recieved.keys():
                                target_spell_damage_recieved[source] += int(result)
                            if target not in encounter_target_spell_total.keys():
                                encounter_target_spell_total[target] = int(result)
                            elif target in encounter_target_spell_total.keys():
                                encounter_target_spell_total[target] += int(result)
                        elif source == encounter_target:
                            if target not in target_spell_damage_done.keys():
                                target_spell_damage_done[target] = int(result)
                            else:
                                target_spell_damage_done[target] += int(result)
                            if source not in encounter_target_spell_done_total.keys():
                                encounter_target_spell_done_total[source] = int(result)
                            else:
                                encounter_target_spell_done_total[source] += int(result)
                ### If mode is heal
                elif mode == "heal":
                    if source not in encounter_heals.keys():
                        encounter_heals[source] = int(result)
                    else:
                        encounter_heals[source] += int(results)
                ### If mode is slain
                elif mode == "slain":
                    if source == encounter_target:
                        if target not in target_killed.keys():
                            target_killed[target] = 1
                        else:
                            target_killed[target] += 1

            ## Sort Encounter Activity from Most to Least Active
            sorted_encounter_activity = dict(
                sorted(encounter_activity.items(), key=lambda x: x[1], reverse=True)
            )

            ## Build Encounter Report
            ### Encounter Summary
            encounter_report = {
                "header": {},
                "encounter_summary": {},
                "target": {},
                "participants": {},
            }
            encounter_report["header"]["version"] = str(
                pkg_resources.get_distribution("eqalert").version
            )
            encounter_report["header"]["date"] = str(encounter_parse_date)
            encounter_report["header"]["time"] = str(encounter_parse_time)
            encounter_report["encounter_summary"]["character"] = str(state.char)
            encounter_report["encounter_summary"]["server"] = str(state.server)
            encounter_report["encounter_summary"]["zone"] = str(state.zone)
            if state.loc != ["0.00", "0.00", "0.00"]:
                encounter_report["encounter_summary"]["location"] = str(state.loc)
            if state.afk == "true":
                encounter_report["encounter_summary"]["context"] = "afk"
            elif state.group == "false" and state.raid == "false":
                encounter_report["encounter_summary"]["context"] = "solo"
            elif state.group == "true" and state.raid == "false":
                encounter_report["encounter_summary"]["context"] = "group"
            elif state.group == "true" and state.raid == "true":
                encounter_report["encounter_summary"]["context"] = "raid"
            encounter_report["encounter_summary"]["target"] = str(encounter_target)
            encounter_report["encounter_summary"]["total_events"] = str(
                this_encounter_events
            )
            encounter_report["encounter_summary"]["duration"] = str(encounter_duration)
            if pet_and_target_same:
                encounter_report["encounter_summary"][
                    "pet_warning"
                ] = "This encounter likely includes one or more pets with the same name as the target.  All pet data in the encounter stack were attributed to the target."

            ### Encounter Target
            encounter_report["target"]["name"] = str(encounter_target)
            if encounter_target in sorted_encounter_activity.keys():
                encounter_report["target"]["activity"] = str(
                    int(
                        (
                            sorted_encounter_activity[encounter_target]
                            / this_encounter_events
                        )
                        * 100
                    )
                )
            if encounter_target in encounter_target_damage_total.keys():
                encounter_report["target"]["melee_damage_taken"] = str(
                    encounter_target_damage_total[encounter_target]
                )
                if encounter_duration > 0:
                    melee_dps_taken = int(
                        encounter_target_damage_total[encounter_target]
                    ) / int(encounter_duration)
                    encounter_report["target"]["melee_dps_taken"] = str(melee_dps_taken)
            if encounter_target in encounter_target_spell_total.keys():
                encounter_report["target"]["spell_damage_taken"] = str(
                    encounter_target_spell_total[encounter_target]
                )
                if encounter_duration > 0:
                    spell_dps_taken = int(
                        encounter_target_spell_total[encounter_target]
                    ) / int(encounter_duration)
                    encounter_report["target"]["spell_dps_taken"] = str(spell_dps_taken)
            if (
                encounter_target in encounter_target_damage_total.keys()
                and encounter_target in encounter_target_spell_total.keys()
            ):
                combined_damage_taken = int(
                    encounter_target_damage_total[encounter_target]
                ) + int(encounter_target_spell_total[encounter_target])
                encounter_report["target"]["combined_damage_taken"] = str(
                    combined_damage_taken
                )
                if encounter_duration > 0:
                    combined_dps_taken = combined_damage_taken / int(encounter_duration)
                    encounter_report["target"]["combined_dps_taken"] = str(
                        combined_dps_taken
                    )
            if encounter_target in encounter_target_damage_done_total.keys():
                encounter_report["target"]["melee_damage_done"] = str(
                    encounter_target_damage_done_total[encounter_target]
                )
                if encounter_duration > 0:
                    melee_dps_done = int(
                        encounter_target_damage_done_total[encounter_target]
                    ) / int(encounter_duration)
                    encounter_report["target"]["melee_dps_done"] = str(melee_dps_done)
            if encounter_target in encounter_target_spell_done_total.keys():
                encounter_report["target"]["spell_damage_done"] = str(
                    encounter_target_spell_done_total[encounter_target]
                )
                if encounter_duration > 0:
                    spell_dps_done = int(
                        encounter_target_spell_done_total[encounter_target]
                    ) / int(encounter_duration)
                    encounter_report["target"]["spell_dps_done"] = str(spell_dps_done)
            if (
                encounter_target in encounter_target_damage_done_total.keys()
                and encounter_target in encounter_target_spell_done_total.keys()
            ):
                combined_damage_done = int(
                    encounter_target_damage_done_total[encounter_target]
                ) + int(encounter_target_spell_done_total[encounter_target])
                encounter_report["target"]["combined_damage_done"] = str(
                    combined_damage_done
                )
                if encounter_duration > 0:
                    combined_dps_done = combined_damage_done / int(encounter_duration)
                    encounter_report["target"]["combined_dps_done"] = str(
                        combined_dps_done
                    )
            if encounter_target in target_block.keys():
                encounter_report["target"]["attacks_blocked"] = str(
                    target_block[encounter_target]
                )
            if encounter_target in target_dodge.keys():
                encounter_report["target"]["attacks_dodged"] = str(
                    target_dodge[encounter_target]
                )
            if encounter_target in target_invulnerable.keys():
                encounter_report["target"]["attacks_invuln"] = str(
                    target_invulnerable[encounter_target]
                )
            if encounter_target in target_miss.keys():
                encounter_report["target"]["attacks_missed"] = str(
                    target_miss[encounter_target]
                )
            if encounter_target in target_parry.keys():
                encounter_report["target"]["attacks_parried"] = str(
                    target_parry[encounter_target]
                )
            if encounter_target in target_riposte.keys():
                encounter_report["target"]["attacks_riposted"] = str(
                    target_riposte[encounter_target]
                )
            if encounter_target in target_rune.keys():
                encounter_report["target"]["attacks_runed"] = str(
                    target_rune[encounter_target]
                )
            if encounter_target in encounter_casts.keys():
                encounter_report["target"]["spell_casts"] = str(
                    encounter_casts[encounter_target]
                )
            if target_killed:
                encounter_report["target"]["killed"] = {}
                for victim in target_killed.keys():
                    v_low = victim.lower()
                    encounter_report["target"]["killed"][v_low] = str(
                        target_killed[victim]
                    )

            ### Encounter Participants
            for participant in sorted_encounter_activity.keys():
                if participant != encounter_target:
                    l_part = str(participant.lower())
                    encounter_report["participants"][l_part] = {}
                    activity = (
                        int(sorted_encounter_activity[participant])
                        / int(this_encounter_events)
                    ) * 100
                    encounter_report["participants"][l_part]["activity"] = str(activity)
                    total_damage = 0
                    if participant in target_melee_damage_recieved.keys():
                        encounter_report["participants"][l_part][
                            "melee_damage_done"
                        ] = str(target_melee_damage_recieved[participant])
                        total_damage += int(target_melee_damage_recieved[participant])
                    if participant in target_spell_damage_recieved.keys():
                        encounter_report["participants"][l_part][
                            "spell_damage_done"
                        ] = str(target_spell_damage_recieved[participant])
                        total_damage += int(target_spell_damage_recieved[participant])
                    if total_damage > 0 and int(encounter_duration) > 0:
                        encounter_report["participants"][l_part][
                            "melee_dps_done"
                        ] = str(total_damage / int(encounter_duration))
                    total_damage = 0
                    if participant in target_melee_damage_done.keys():
                        encounter_report["participants"][l_part][
                            "melee_damage_taken"
                        ] = str(target_melee_damage_done[participant])
                        total_damage += int(target_melee_damage_done[participant])
                    if participant in target_spell_damage_done.keys():
                        encounter_report["participants"][l_part][
                            "spell_damage_taken"
                        ] = str(target_spell_damage_done[participant])
                        total_damage += int(target_spell_damage_done[participant])
                    if total_damage > 0 and int(encounter_duration) > 0:
                        encounter_report["participants"][l_part][
                            "melee_dps_taken"
                        ] = str(total_damage / int(encounter_duration))
                    if participant in source_block.keys():
                        encounter_report["participants"][l_part][
                            "attacks_blocked"
                        ] = str(source_block[participant])
                    if participant in source_dodge.keys():
                        encounter_report["participants"][l_part][
                            "attacks_dodged"
                        ] = str(source_dodge[participant])
                    if participant in source_invulnerable.keys():
                        encounter_report["participants"][l_part][
                            "attacks_invuln"
                        ] = str(source_invulnerable[participant])
                    if participant in source_miss.keys():
                        encounter_report["participants"][l_part][
                            "attacks_missed"
                        ] = str(source_miss[participant])
                    if participant in source_parry.keys():
                        encounter_report["participants"][l_part][
                            "attacks_parried"
                        ] = str(source_parry[participant])
                    if participant in source_riposte.keys():
                        encounter_report["participants"][l_part][
                            "attacks_riposted"
                        ] = str(source_riposte[participant])
                    if participant in source_rune.keys():
                        encounter_report["participants"][l_part]["attacks_runed"] = str(
                            source_rune[participant]
                        )
                    if participant in encounter_casts.keys():
                        encounter_report["participants"][l_part]["spell_casts"] = str(
                            encounter_casts[participant]
                        )
                    if participant in encounter_heals.keys():
                        encounter_report["participants"][l_part]["healing"] = str(
                            encounter_heals.get(participant)
                        )
                    if participant in target_killed.keys():
                        encounter_report["participants"][l_part]["died"] = str(
                            target_killed[participant]
                        )

            ## Send Report to Display
            display_q.put(
                eqa_struct.display(
                    eqa_settings.eqa_time(), "update", "encounter", encounter_report
                )
            )

            ## Write Encounter to File
            if config["settings"]["encounter_parsing"]["auto_save"] == "true":
                encounter_report_json_string = json.dumps(encounter_report, indent=2)
                encounter_report_file = open(
                    encounter_zone_date_path + encounter_filename, "w"
                )
                encounter_report_file.write(encounter_report_json_string)
                encounter_report_file.close()

            ## Prune Old Events in encounter_stack
            if len(encounter_stack) > 1:
                count = 0
                keep_encounter_stack = deque([])
                while count < len(encounter_stack):
                    event = encounter_stack.popleft()
                    time, source, target, mode, result = event
                    this_hour, this_minute, this_second_m = time.split(":")
                    this_second, this_milli = last_second_m.split(".")
                    this_message_time = datetime(
                        2020, 12, 30, int(this_hour), int(this_minute), int(this_second)
                    )
                    message_age = int(
                        (encounter_end_time - this_message_time).total_seconds()
                    )
                    if message_age < 0:
                        first_half = int(
                            (
                                datetime(2020, 12, 30, 23, 59, 59) - this_message_time
                            ).total_seconds()
                        )
                        second_half = int(encounter_end_time.total_seconds())
                        message_age = int(first_half + second_half)

                    # If an event is more than 30 minutes old and still hasn't been used in an encounter log, remove it
                    if not message_age > 18000:
                        keep_encounter_stack.append(event)

                encounter_stack = keep_encounter_stack

    except Exception as e:
        eqa_settings.log(
            "encounter report: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


if __name__ == "__main__":
    main()
