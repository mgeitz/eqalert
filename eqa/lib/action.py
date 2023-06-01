#! /usr/bin/env python

"""
   Program:   EQ Alert
   File Name: eqa/lib/action.py
   Copyright (C) 2023 M Geitz

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
import datetime
import sys
import time
import re
import os

import eqa.lib.config as eqa_config
import eqa.lib.settings as eqa_settings
import eqa.lib.sound as eqa_sound
import eqa.lib.struct as eqa_struct


def process(
    configs,
    base_path,
    state,
    action_q,
    encounter_q,
    timer_q,
    system_q,
    display_q,
    sound_q,
    exit_flag,
    cfg_reload,
    mute_list,
    change_char,
    version,
):
    """
    Process: action_q
    Produce: sound_q, display_q, system_q, encounter_q
    """

    try:
        # Spell Cast Buffers
        spell_casting_buffer_other = deque(maxlen=8)
        spell_casting_buffer_you = {}

        # Spell Timer Data
        spell_timers = eqa_config.get_spell_timers(
            configs.settings.config["settings"]["paths"]["data"]
        )

        # Spell Line Data
        spell_lines = eqa_config.get_spell_lines(
            configs.settings.config["settings"]["paths"]["data"]
        )

        # Spell Caster Data
        spell_casters = eqa_config.get_spell_casters(
            configs.settings.config["settings"]["paths"]["data"]
        )

        # Player Data
        player_list = eqa_config.get_players_file(
            configs.settings.config["settings"]["paths"]["data"], state.server
        )

        # Class Mapping
        class_mapping = {
            "bard": "bard",
            "minstrel": "bard",
            "troubadour": "bard",
            "virtuoso": "bard",
            "cleric": "cleric",
            "vicar": "cleric",
            "templar": "cleric",
            "high priest": "cleric",
            "druid": "druid",
            "wanderer": "druid",
            "preserver": "druid",
            "hierophant": "druid",
            "enchanter": "enchanter",
            "illusionist": "enchanter",
            "beguiler": "enchanter",
            "phantasmist": "enchanter",
            "magician": "magician",
            "elementalist": "magician",
            "conjurer": "magician",
            "arch mage": "magician",
            "monk": "monk",
            "disciple": "monk",
            "master": "monk",
            "grandmaster": "monk",
            "necromancer": "necromancer",
            "heretic": "necromancer",
            "defiler": "necromancer",
            "warlock": "necromancer",
            "paladin": "paladin",
            "cavalier": "paladin",
            "knight": "paladin",
            "crusader": "paladin",
            "ranger": "ranger",
            "pathfinder": "ranger",
            "outrider": "ranger",
            "warder": "ranger",
            "rogue": "rogue",
            "rake": "rogue",
            "blackguard": "rogue",
            "assassin": "rogue",
            "shadow knight": "shadow knight",
            "reaver": "shadow knight",
            "revenant": "shadow knight",
            "grave lord": "shadow knight",
            "shaman": "shaman",
            "mystic": "shaman",
            "luminary": "shaman",
            "oracle": "shaman",
            "warrior": "warrior",
            "champion": "warrior",
            "myrmidon": "warrior",
            "warlord": "warrior",
            "wizard": "wizard",
            "channeler": "wizard",
            "evoker": "wizard",
            "sorcerer": "wizard",
        }

        # Always on line_type actions
        action_line_types = [
            "who_player",
            "location",
            "direction",
            "motd_welcome",
            "group_join_notify",
            "group_removed",
            "group_alone",
            "group_disbanded",
            "group_created",
            "group_leader_you",
            "group_leader_other",
            "encumbered_off",
            "encumbered_on",
            "you_char_bound",
            "spell_bind_you",
            "you_afk_off",
            "you_afk_on",
            "say_you",
            "you_new_zone",
        ]

        while (
            not exit_flag.is_set()
            and not cfg_reload.is_set()
            and not change_char.is_set()
        ):
            # Sleep between empty checks
            if action_q.qsize() < 1:
                time.sleep(0.01)
            elif state.debug:
                eqa_settings.log("action_q depth: " + str(action_q.qsize()))

            # Check queue for message
            if not action_q.empty():
                ## Read new message
                new_message = action_q.get()
                line_type = new_message.type
                line_time = new_message.timestamp
                line_tx = new_message.tx
                line_rx = new_message.rx
                check_line = new_message.payload

                ## Debug: Log line match type
                if state.debug:
                    action_matched(line_type, check_line, base_path, version)
                    display_q.put(
                        eqa_struct.display(
                            eqa_settings.eqa_time(),
                            "event",
                            "debug",
                            (line_type, check_line),
                        )
                    )

                ## Encounter Parsing
                if state.encounter_parse:
                    if "combat_" in line_type:
                        encounter_q.put(
                            eqa_struct.message(
                                line_time,
                                line_type,
                                "combat",
                                None,
                                check_line,
                            )
                        )
                    elif "spells_" in line_type:
                        encounter_q.put(
                            eqa_struct.message(
                                line_time,
                                line_type,
                                "spell",
                                None,
                                check_line,
                            )
                        )
                    elif "you_auto_attack_" in line_type:
                        encounter_q.put(
                            eqa_struct.message(
                                line_time,
                                line_type,
                                "combat",
                                None,
                                check_line,
                            )
                        )
                    elif "experience_" in line_type:
                        encounter_q.put(
                            eqa_struct.message(
                                line_time,
                                line_type,
                                "stop",
                                None,
                                check_line,
                            )
                        )
                    elif line_type == "faction_line":
                        encounter_q.put(
                            eqa_struct.message(
                                line_time,
                                line_type,
                                "stop",
                                None,
                                check_line,
                            )
                        )
                    elif "mob_slain_" in line_type:
                        encounter_q.put(
                            eqa_struct.message(
                                line_time,
                                line_type,
                                "stop",
                                None,
                                check_line,
                            )
                        )
                    elif line_type == "you_new_zone":
                        encounter_q.put(
                            eqa_struct.message(
                                line_time,
                                line_type,
                                "stop",
                                None,
                                check_line,
                            )
                        )

                ## Mob Timers
                if state.auto_mob_timer:
                    if "experience_" in line_type:
                        if state.zone is not None:
                            action_mob_timer(
                                timer_q,
                                configs.zones.config["zones"][state.zone]["timer"],
                                state.auto_mob_timer_delay,
                                state.zone,
                            )

                ## Spell Timers
                if state.spell_timer_self or state.spell_timer_other:
                    ## Other Spell Timers
                    if state.spell_timer_other:
                        if (
                            re.fullmatch(r"^spell\_.+\_other_on$", line_type)
                            is not None
                        ):
                            action_spell_timer(
                                state,
                                configs,
                                timer_q,
                                line_type,
                                line_time,
                                check_line,
                                spell_casting_buffer_other,
                                spell_casting_buffer_you,
                                spell_timers,
                                spell_lines,
                                spell_casters,
                                player_list,
                            )
                    ## Self Spell Timers
                    if state.spell_timer_self:
                        if re.fullmatch(r"^spell\_.+\_you_on$", line_type) is not None:
                            action_spell_timer(
                                state,
                                configs,
                                timer_q,
                                line_type,
                                line_time,
                                check_line,
                                spell_casting_buffer_other,
                                spell_casting_buffer_you,
                                spell_timers,
                                spell_lines,
                                spell_casters,
                                player_list,
                            )
                        elif (
                            re.fullmatch(r"^spell\_.+\_you_off$", line_type) is not None
                        ):
                            action_spell_remove_timer(
                                state, timer_q, spell_lines, line_type, check_line
                            )
                    ### Spell Casting Buffer Other
                    if line_type == "spells_cast_other":
                        action_spell_casting_other(
                            check_line,
                            line_type,
                            line_time,
                            spell_casting_buffer_other,
                        )
                    ### Spell Casting Buffer You
                    elif line_type == "spells_cast_you":
                        spell_casting_buffer_you = action_spell_casting_you(
                            check_line,
                            line_type,
                            line_time,
                            spell_casting_buffer_you,
                        )
                    ### TODO: Spell Casting Item Buffer
                    # Interesting note, these only show up for the active player for any non-instant cast item.  Other plays get the normal casting message.
                    # elif line_type == "spells_cast_item_you":
                    #    action_spell_casting(
                    #        check_line,
                    #        line_type,
                    #        line_time,
                    #        spell_casting_buffer_other,
                    #        spell_casting_buffer_you,
                    #    )
                    ### Zone drift
                    elif line_type == "zoning":
                        timer_q.put(
                            eqa_struct.timer(
                                datetime.datetime.now(),
                                "zoning",
                                None,
                                None,
                            )
                        )
                    # Remove spell timers for the dead
                    elif "_slain" in line_type:
                        action_spell_remove_timer(
                            state, timer_q, spell_lines, line_type, check_line
                        )

                ## Consider Evaluation
                if state.consider_eval:
                    if line_type == "consider":
                        action_consider_evaluation(sound_q, check_line)

                if configs.settings.config["settings"]["hail_alert"]["enabled"]:
                    if line_type == "say":
                        if "hail" in check_line:
                            action_say_hail_alert(sound_q, state, check_line)

                ## Always on line_type specific actions
                if line_type in action_line_types:
                    if line_type == "who_player":
                        action_who_player(
                            configs,
                            system_q,
                            state,
                            check_line,
                            player_list,
                            class_mapping,
                        )
                    ### State building line types
                    elif line_type == "location":
                        action_location(system_q, check_line)
                    elif line_type == "direction":
                        action_direction(system_q, check_line)
                    elif line_type == "group_join_notify":
                        action_group_join_notify(system_q, check_line)
                    elif line_type == "group_removed":
                        action_group_removed(system_q)
                    elif line_type == "group_disbanded":
                        action_group_disbanded(system_q)
                    elif line_type == "group_created":
                        action_group_created(system_q)
                    elif line_type == "group_alone":
                        action_group_alone(system_q)
                    elif line_type == "group_leader_you":
                        action_group_leader_you(system_q)
                    elif line_type == "group_leader_other":
                        action_group_leader_other(system_q, check_line)
                    elif line_type == "encumbered_off":
                        action_encumbered_off(system_q)
                    elif line_type == "encumbered_on":
                        action_encumbered_on(system_q)
                    elif line_type == "you_afk_off":
                        action_you_afk_off(system_q)
                    elif line_type == "you_afk_on":
                        action_you_afk_on(system_q)
                    elif line_type == "you_new_zone":
                        action_you_new_zone(
                            base_path,
                            system_q,
                            display_q,
                            sound_q,
                            timer_q,
                            state,
                            configs,
                            check_line,
                        )
                    elif line_type == "say_you":
                        ### Parser say commands
                        if (
                            re.fullmatch(r"^You say, \'parser .+\'$", check_line)
                            is not None
                        ):
                            action_you_say_commands(
                                timer_q,
                                system_q,
                                sound_q,
                                display_q,
                                check_line,
                                configs,
                                mute_list,
                                state,
                                player_list,
                            )
                    elif line_type == "motd_welcome":
                        action_motd_welcome(system_q)
                    elif (
                        line_type == "spell_bind_you"
                    ):  # TODO: Whats going on here is this a dupe?
                        action_spell_bind_you(system_q, state)
                    elif line_type == "you_char_bound":
                        action_you_char_bound(system_q, check_line)

                ## If line_type exists in the config
                if line_type in configs.alerts.config["line"].keys():
                    reaction = configs.alerts.config["line"][line_type]["reaction"]

                    ### Handle Alert Reactions
                    if reaction == "alert":
                        reaction_alert(
                            line_type,
                            check_line,
                            configs,
                            sound_q,
                            display_q,
                            state,
                            mute_list,
                        )

                    ### Handle Context Reactions
                    elif reaction != False:
                        reaction_context(
                            line_type,
                            check_line,
                            configs,
                            sound_q,
                            display_q,
                            state,
                            mute_list,
                            reaction,
                        )

                    ### Handle alert reactions for all lines
                    if configs.alerts.config["line"]["all"]["reaction"] == "alert":
                        reaction_alert(
                            "all",
                            check_line,
                            configs,
                            sound_q,
                            display_q,
                            state,
                            mute_list,
                        )

                    ### Handle context reaction for all lines
                    elif configs.alerts.config["line"]["all"]["reaction"] != False:
                        reaction_context(
                            "all",
                            check_line,
                            configs,
                            sound_q,
                            display_q,
                            state,
                            mute_list,
                            configs.alerts.config["line"]["all"]["reaction"],
                        )

                ## If line_type is not in the config
                else:
                    ### Add new line type
                    eqa_config.add_type(line_type, base_path)
                    display_q.put(
                        eqa_struct.display(
                            eqa_settings.eqa_time(),
                            "event",
                            "events",
                            "added: " + line_type,
                        )
                    )
                    system_q.put(
                        eqa_struct.message(
                            eqa_settings.eqa_time(),
                            "system",
                            "reload_config",
                            None,
                            None,
                        )
                    )

                action_q.task_done()

        # Save any new player data collected to file
        if configs.settings.config["settings"]["player_data"]["persist"]:
            eqa_config.update_players_file(
                configs.settings.config["settings"]["paths"]["data"],
                state.server,
                player_list,
            )

    except Exception as e:
        eqa_settings.log(
            "process action: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )

    sys.exit(0)


def action_spell_casting_other(
    check_line,
    line_type,
    line_time,
    spell_casting_buffer_other,
):
    """Populate Spell Casting Buffer"""

    try:
        caster = re.findall(r"[a-zA-Z\s\'`]+(?= begins)", check_line)[0].lower()
        spell_casting_buffer_other.append({"caster": caster.lower(), "time": line_time})

    except Exception as e:
        eqa_settings.log(
            "acton spell casting other: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def action_spell_casting_you(
    check_line,
    line_type,
    line_time,
    spell_casting_buffer_you,
):
    """Populate Spell Casting Buffer"""

    try:
        spell = (
            re.findall(r"(?<=casting\ )[a-zA-Z\s]+", check_line)[0]
            .lower()
            .replace(" ", "_")
        )
        spell_casting_buffer_you = {"spell": spell, "time": line_time}

        return spell_casting_buffer_you

    except Exception as e:
        eqa_settings.log(
            "acton spell casting you: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def action_say_hail_alert(sound_q, state, check_line):
    """Alert when active character is hailed"""

    try:
        if state.char.lower() in check_line:
            sound_q.put(eqa_struct.sound("speak", check_line))

    except Exception as e:
        eqa_settings.log(
            "acton say hail alert: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def spell_formulas(formula, level, duration):
    """Calculate spell duration"""

    try:
        if formula == "1":
            if (int(level) / 2) < int(duration):
                spell_duration = int(level) / 2
            else:
                spell_duration = int(duration)
        elif formula == "2":
            spell_duration = (int(duration) / 5) * 3
        elif formula == "3":
            if (int(level) * 30) < int(duration):
                spell_duration = int(level) * 30
            else:
                spell_duration = int(duration)
        elif formula == "4":
            if int(duration) > 0:
                spell_duration = int(duration)
            else:
                spell_duration = 50
        elif formula == "5":
            if int(duration) < 3:
                spell_duration = int(duration)
            else:
                spell_duration = 3
        elif formula == "6":
            if (int(level) / 2) < int(duration):
                spell_duration = int(level) / 2
            else:
                spell_duration = int(duration)
        elif formula == "7":
            if int(duration) != 0:
                spell_duration = int(duration)
            else:
                spell_duration = int(level)
        elif formula == "8":
            if (int(level) + 10) < int(duration):
                spell_duration = int(level) + 10
            else:
                spell_duration = int(duration)
        elif formula == "9":
            if ((int(level) * 2) + 10) < int(duration):
                spell_duration = (int(level) * 2) + 10
            else:
                spell_duration = int(duration)
        elif formula == "10":
            if ((int(level) * 3) + 10) < int(duration):
                spell_duration = (int(level) * 3) + 10
            else:
                spell_duration = int(duration)
        elif formula == "11":
            spell_duration = int(duration)
        elif formula == "12":
            spell_duration = int(duration)
        elif formula == "50":
            spell_duration = 72000
        elif formula == "3600":
            if int(duration) != 0:
                spell_duration = int(duration)
            else:
                spell_duration = 3600
        else:
            spell_duration = 0

        return spell_duration * 6

    except Exception as e:
        eqa_settings.log(
            "spell formulas: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def action_spell_remove_timer(state, timer_q, spell_lines, line_type, check_line):
    """Remove timer for spell that dropped"""

    try:
        if "spell_" in line_type:
            if re.fullmatch(r"^spell\_line\_.+$", line_type) is not None:
                if line_type in spell_lines["spell_lines"].keys():
                    for spell in spell_lines["spell_lines"][line_type].keys():
                        # Submit timer removal
                        timer_q.put(
                            eqa_struct.spell_timer(
                                (datetime.datetime.now()),
                                "remove_spell_timer",
                                None,
                                state.char.lower(),
                                spell,
                                None,
                                None,
                                None,
                            )
                        )
            else:
                spell = re.findall(
                    r"(?<=spell\_)[a-zA-Z\s\_]+(?=\_you\_off)", line_type
                )[0]
                # Submit timer removal
                timer_q.put(
                    eqa_struct.spell_timer(
                        (datetime.datetime.now()),
                        "remove_spell_timer",
                        None,
                        state.char.lower(),
                        spell,
                        None,
                        None,
                        None,
                    )
                )
        elif line_type == "mob_slain_other":
            target = re.findall(r"(?:^|(?:[.!?]\s))(\w+)", check_line)[0].lower()
            # Submit timer removal
            timer_q.put(
                eqa_struct.spell_timer(
                    (datetime.datetime.now()),
                    "remove_spell_timer",
                    None,
                    target,
                    "all",
                    None,
                    None,
                    None,
                )
            )
        elif line_type == "mob_slain_you":
            target = re.findall(r"(?<=You have slain )[a-zA-Z\_]+", check_line)[
                0
            ].lower()
            # Submit timer removal
            timer_q.put(
                eqa_struct.spell_timer(
                    (datetime.datetime.now()),
                    "remove_spell_timer",
                    None,
                    target,
                    "all",
                    None,
                    None,
                    None,
                )
            )
        elif line_type == "you_slain":
            # Submit timer removal
            timer_q.put(
                eqa_struct.spell_timer(
                    (datetime.datetime.now()),
                    "remove_spell_timer",
                    None,
                    state.char.lower(),
                    "all",
                    None,
                    None,
                    None,
                )
            )

    except Exception as e:
        eqa_settings.log(
            "acton spell remove timer: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def action_spell_timer(
    state,
    configs,
    timer_q,
    line_type,
    line_time,
    line,
    spell_casting_buffer_other,
    spell_casting_buffer_you,
    spell_timers,
    spell_lines,
    spell_casters,
    player_list,
):
    """Set timer for spell duration"""

    try:
        is_spell_line = False
        find_time = False

        if re.fullmatch(r"^spell\_line\_[a-zA-Z\s\_]+\_you\_on", line_type) is not None:
            target = state.char.lower()
            spell_line = re.findall(
                r"(?<=spell\_line\_)[a-zA-Z\s\_]+(?=\_you\_on)", line_type
            )[0]
            is_spell_line = True
        elif (
            re.fullmatch(r"^spell\_line\_[a-zA-Z\s\_]+\_other\_on", line_type)
            is not None
        ):
            # TODO: Find way to reliably pull multi-word NPC names from spell_line_*_other_on
            target = re.findall(r"(?:^|(?:[.!?]\s))(\w+)", line)[0].lower()
            spell_line = re.findall(
                r"(?<=spell\_line\_)[a-zA-Z\s\_]+(?=\_other\_on)", line_type
            )[0]
            is_spell_line = True
        elif re.fullmatch(r".+\_you\_on$", line_type) is not None:
            spell = re.findall(r"(?<=spell\_)[a-zA-Z\s\_]+(?=\_you\_on)", line_type)[0]
            target = state.char.lower()
        elif re.fullmatch(r".+\_other\_on", line_type) is not None:
            spell = re.findall(r"(?<=spell\_)[a-zA-Z\s\_]+(?=\_other\_on)", line_type)[
                0
            ]
            # TODO: Find way to reliably pull multi-word NPC names from spell_*_other_on () sans spell_line_
            target = re.findall(r"(?:^|(?:[.!?]\s))(\w+)", line)[0].lower()

        # If this is a spell cast line output shared by more than one spell
        if is_spell_line:
            if state.debug:
                eqa_settings.log("spell line found: " + line_type)
            # Determine possible spells
            if line_type in spell_lines["spell_lines"].keys():
                possible_spells = spell_lines["spell_lines"][line_type].keys()
                if state.debug:
                    eqa_settings.log("possible spells: " + str(possible_spells))
                check_for_spells = []
                # Retrieve casting requirements for each possible spell
                for possible_spell in possible_spells:
                    if possible_spell in spell_casters["spells"].keys():
                        # Validate a player cast this spell
                        ## TODO: later try and guess npc/item only spells with vague messages, for now thats too much guessing
                        if spell_casters["spells"][possible_spell]["classes"]:
                            check_for_spells.append(
                                {
                                    "spell": possible_spell,
                                    "classes": spell_casters["spells"][possible_spell][
                                        "classes"
                                    ].keys(),
                                }
                            )

                # First check if the player could have cast this
                if spell_casting_buffer_you and state.char_level is not None:
                    # If the most recent player cast spell is in the possible spell list
                    if (
                        spell_casting_buffer_you["spell"]
                        in spell_lines["spell_lines"][line_type].keys()
                        and spell_casting_buffer_you["spell"]
                        in spell_casters["spells"].keys()
                    ):
                        if state.debug:
                            eqa_settings.log(
                                "Checking if cast for: "
                                + spell_casting_buffer_you["spell"]
                                + " occurred "
                                + spell_timers["spells"][
                                    spell_casting_buffer_you["spell"]
                                ]["cast_time"]
                                + " seconds ago"
                            )
                        # If most recent player cast spell occurred spell time ago to this spell landing
                        if (
                            int(
                                (
                                    datetime.datetime.strptime(line_time, "%H:%M:%S.%f")
                                    - datetime.datetime.strptime(
                                        spell_casting_buffer_you["time"], "%H:%M:%S.%f"
                                    )
                                    - datetime.timedelta(
                                        seconds=float(
                                            spell_timers["spells"][
                                                spell_casting_buffer_you["spell"]
                                            ]["cast_time"]
                                        )
                                    )
                                ).total_seconds()
                            )
                            == 0
                        ):
                            identified_spell_caster = state.char.lower()
                            identified_spell_level = state.char_level
                            identified_spell = spell_casting_buffer_you["spell"]
                            identified_spell_target = target
                            find_time = True

                # Then check spell cast buffer other cast time ago for each possible spell
                if not find_time:
                    # For each possible spell
                    for spell_caster in check_for_spells:
                        # Retrieve cast time for the possible spell
                        cast_time = spell_timers["spells"][
                            spell_caster["spell"]
                        ]  # this is way too hard to read
                        # Check each event in spell cast buffer other if it occurred possible spell cast time ago
                        for recent_cast_event in spell_casting_buffer_other:
                            # If this spell event coincides with a spell cast event cast time ago
                            if (
                                int(
                                    (
                                        datetime.datetime.strptime(
                                            line_time, "%H:%M:%S.%f"
                                        )
                                        - datetime.datetime.strptime(
                                            recent_cast_event["time"], "%H:%M:%S.%f"
                                        )
                                        - datetime.timedelta(
                                            seconds=float(
                                                spell_timers["spells"][
                                                    spell_caster["spell"]
                                                ]["cast_time"]
                                            )
                                        )
                                    ).total_seconds()
                                )
                                == 0
                            ):
                                # Check if caster is able to cast potential spell
                                if recent_cast_event["caster"] in player_list.keys():
                                    player_class = player_list[
                                        recent_cast_event["caster"]
                                    ]["class"]
                                    player_level = player_list[
                                        recent_cast_event["caster"]
                                    ]["level"]
                                    # If we know this players class and level
                                    if player_class is not None and player_level > 0:
                                        # If the player class can cast this spell
                                        if (
                                            player_class
                                            in spell_casters["spells"][
                                                spell_caster["spell"]
                                            ]["classes"].keys()
                                        ):
                                            # If that players level can cast this spell
                                            if (
                                                int(
                                                    spell_casters["spells"][
                                                        spell_caster["spell"]
                                                    ]["classes"][player_class]
                                                )
                                                <= player_level
                                            ):
                                                if not find_time:
                                                    identified_spell_caster = (
                                                        recent_cast_event["caster"]
                                                    )
                                                    identified_spell_level = (
                                                        player_list[
                                                            identified_spell_caster
                                                        ]["level"]
                                                    )
                                                    identified_spell = spell_caster[
                                                        "spell"
                                                    ]
                                                    identified_spell_target = target
                                                    find_time = True
                                                # Favor matched spell with highest level casting requirements
                                                elif int(
                                                    spell_casters["spells"][
                                                        identified_spell
                                                    ]["classes"][
                                                        player_list[
                                                            identified_spell_caster
                                                        ]["class"]
                                                    ]
                                                ) < int(
                                                    spell_casters["spells"][
                                                        identified_spell
                                                    ]["classes"][
                                                        player_list[
                                                            recent_cast_event["caster"]
                                                        ]["class"]
                                                    ]
                                                ):
                                                    identified_spell_caster = (
                                                        recent_cast_event["caster"]
                                                    )
                                                    identified_spell_level = (
                                                        player_list[
                                                            identified_spell_caster
                                                        ]["level"]
                                                    )
                                                    identified_spell = spell_caster[
                                                        "spell"
                                                    ]
                                                    identified_spell_target = target
                                # TODO: Maybe add an option to assume your player level if player data is not found and your level is sufficient to cast the identified spell?

        # We know the spell which landed
        else:
            if state.debug:
                eqa_settings.log("Checking for spell: " + spell)
            # If we have spell_caster info on this spell
            if spell in spell_casters["spells"].keys():
                # Check if player has cast anything
                if spell_casting_buffer_you and state.char_level is not None:
                    # If the spell cast by the player is in the spell casters file
                    if (
                        spell_casting_buffer_you["spell"]
                        in spell_casters["spells"].keys()
                    ):
                        # If most recent player cast spell occurred spell time ago to this spell landing
                        if (
                            int(
                                (
                                    datetime.datetime.strptime(line_time, "%H:%M:%S.%f")
                                    - datetime.datetime.strptime(
                                        spell_casting_buffer_you["time"], "%H:%M:%S.%f"
                                    )
                                    - datetime.timedelta(
                                        seconds=float(
                                            spell_timers["spells"][
                                                spell_casting_buffer_you["spell"]
                                            ]["cast_time"]
                                        )
                                    )
                                ).total_seconds()
                            )
                            == 0
                        ):
                            identified_spell_caster = state.char.lower()
                            identified_spell_level = state.char_level
                            identified_spell = spell_casting_buffer_you["spell"]
                            identified_spell_target = target
                            find_time = True
                        # This spell has no listed classes listed and can be an item cast and you cast it
                        elif (
                            not spell_casters["spells"][spell]["classes"]
                            and spell_casters["spells"][spell]["item"]
                        ):
                            identified_spell_caster = state.char.lower()
                            identified_spell_level = state.char_level
                            identified_spell = spell_casting_buffer_you["spell"]
                            identified_spell_target = target
                            find_time = True
                        # The spell cannot be cast by your class and can be an item cast and you cast it but not spell cast time ago
                        # elif (
                        #    state.char_class.lower()
                        #    not in spell_casters["spells"][spell]["classes"].keys()
                        #    and spell_casters["spells"][spell]["item"]
                        # ):
                        #    # TODO: This is where item cast durations would be checked
                        #    if state.spell_timer_guess:
                        #        identified_spell_caster = state.char.lower()
                        #        identified_spell_level = state.char_level
                        #        identified_spell = spell_casting_buffer_you["spell"]
                        #        identified_spell_target = target
                        #        find_time = True

                # Check for matching spell cast event
                if not find_time:
                    for recent_cast_event in spell_casting_buffer_other:
                        if state.debug:
                            eqa_settings.log("Checking " + recent_cast_event["caster"])
                        if (
                            int(
                                (
                                    datetime.datetime.strptime(line_time, "%H:%M:%S.%f")
                                    - datetime.datetime.strptime(
                                        recent_cast_event["time"], "%H:%M:%S.%f"
                                    )
                                    - datetime.timedelta(
                                        seconds=float(
                                            spell_timers["spells"][spell]["cast_time"]
                                        )
                                    )
                                ).total_seconds()
                            )
                            == 0
                        ):
                            if state.debug:
                                eqa_settings.log(
                                    "Checking player info for "
                                    + recent_cast_event["caster"]
                                )
                            # Do we have player info on the likely caster?
                            if recent_cast_event["caster"] in player_list.keys():
                                player_class = player_list[recent_cast_event["caster"]][
                                    "class"
                                ]
                                player_level = player_list[recent_cast_event["caster"]][
                                    "level"
                                ]
                                if player_class is not None and player_level > 0:
                                    if (
                                        player_class
                                        in spell_casters["spells"][spell][
                                            "classes"
                                        ].keys()
                                    ):
                                        player_level = int(
                                            player_list[recent_cast_event["caster"]][
                                                "level"
                                            ]
                                        )
                                        if (
                                            int(
                                                spell_casters["spells"][spell][
                                                    "classes"
                                                ][player_class]
                                            )
                                            <= player_level
                                        ):
                                            identified_spell_caster = recent_cast_event[
                                                "caster"
                                            ]
                                            identified_spell_level = player_list[
                                                identified_spell_caster
                                            ]["level"]
                                            identified_spell = spell
                                            identified_spell_target = target
                                            find_time = True
                                            if state.debug:
                                                eqa_settings.log(
                                                    "Found spell cast by "
                                                    + identified_spell_caster
                                                )
                            # Time to guess the spell level
                            elif state.spell_timer_guess:
                                if state.debug:
                                    eqa_settings.log("Into spell guessing territory")
                                player_level_could_cast = False
                                # If a player could cast this
                                if spell_casters["spells"][spell]["classes"]:
                                    # Check if the current player level could cast this (assuming it is a grouped peer or target mob)
                                    for caster_class in spell_casters["spells"][spell][
                                        "classes"
                                    ]:
                                        if state.char_level is not None:
                                            if state.char_level >= int(
                                                spell_casters["spells"][spell][
                                                    "classes"
                                                ][caster_class]
                                            ):
                                                player_level_could_cast = True

                                    if player_level_could_cast:
                                        identified_spell_level = state.char_level
                                    else:
                                        identified_spell_level = 60

                                    identified_spell_caster = recent_cast_event[
                                        "caster"
                                    ]
                                    identified_spell = spell
                                    identified_spell_target = target
                                    find_time = True

                                # If this is a known npc only spell, just set to current player level
                                elif (
                                    spell_casters["spells"][spell]["npc"]
                                    and state.char_level is not None
                                ):
                                    identified_spell_caster = recent_cast_event[
                                        "caster"
                                    ]
                                    identified_spell_level = state.char_level
                                    identified_spell = spell
                                    identified_spell_target = target
                                    find_time = True

        if find_time:
            make_timer = True

            # Guild Only Filter
            if state.spell_timer_guild_only and state.char_guild is not None:
                # If this was cast by myself or another player
                if identified_spell_caster in player_list.keys():
                    # If a guildie didn't cast it
                    if (
                        not player_list[str(identified_spell_caster)]["guild"]
                        == state.char_guild.lower()
                    ):
                        # and it didn't land on a guildie
                        if identified_spell_target in player_list.keys():
                            if (
                                not player_list[str(identified_spell_target)]["guild"]
                                == state.char_guild.lower()
                            ):
                                make_timer = False
                # If we don't know anything about the identified caster
                else:
                    make_timer = False

            # Yours Only Filter
            if state.spell_timer_yours_only:
                if identified_spell_caster != state.char.lower():
                    make_timer = False

            # By List Filter
            if configs.settings.config["settings"]["timers"]["spell"]["filter"][
                "by_list"
            ]:
                make_timer = False
                if (
                    len(
                        configs.settings.config["settings"]["timers"]["spell"][
                            "filter"
                        ]["filter_list"].keys()
                    )
                    > 0
                ):
                    for spell in configs.settings.config["settings"]["timers"]["spell"][
                        "filter"
                    ]["filter_list"].keys():
                        if configs.settings.config["settings"]["timers"]["spell"][
                            "filter"
                        ]["filter_list"][spell]:
                            if spell == identified_spell:
                                make_timer = True

            # See if this is a timer which will at least last longer than spell timer delay
            spell_duration = spell_formulas(
                spell_timers["spells"][identified_spell]["formula"],
                identified_spell_level,
                spell_timers["spells"][identified_spell]["duration"],
            )
            if spell_duration <= state.spell_timer_delay:
                if state.debug:
                    eqa_settings.log("Spell duration too short for timer")
                make_timer = False

            # Set timer message
            if make_timer:
                if identified_spell_target == state.char.lower():
                    if state.spell_timer_delay <= 0:
                        message = identified_spell.replace("_", " ") + " has worn off"
                    else:
                        message = identified_spell.replace("_", " ") + " is wearing off"
                else:
                    if state.spell_timer_delay <= 0:
                        message = (
                            identified_spell.replace("_", " ")
                            + " on "
                            + identified_spell_target
                            + " has worn off"
                        )
                    else:
                        message = (
                            identified_spell.replace("_", " ")
                            + " on "
                            + identified_spell_target
                            + " is wearing off"
                        )

                spell_timer_expire = (
                    datetime.datetime.now()
                    + datetime.timedelta(seconds=spell_duration)
                    - datetime.timedelta(seconds=state.spell_timer_delay)
                )

                # Submit timer
                timer_q.put(
                    eqa_struct.spell_timer(
                        spell_timer_expire,
                        "spell",
                        identified_spell_caster,
                        identified_spell_target,
                        identified_spell,
                        spell_duration,
                        datetime.datetime.now(),
                        message,
                    )
                )

                # Debug logging
                if state.debug:
                    eqa_settings.log(
                        "Spell timer created for "
                        + identified_spell
                        + " "
                        + identified_spell_caster
                        + "->"
                        + identified_spell_target
                        + " for "
                        + str(spell_duration)
                        + " seconds"
                    )

    except Exception as e:
        eqa_settings.log(
            "action spell timer: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def action_mob_timer(timer_q, timer_seconds, auto_mob_timer_delay, zone):
    """Set timer for mob spawn using default zone timer value"""

    timer_seconds = timer_seconds - auto_mob_timer_delay
    if timer_seconds < 0:
        timer_seconds = 0
    if auto_mob_timer_delay <= 0:
        pop_message = "Pop " + str(zone)
    else:
        pop_message = (
            "Pop " + str(zone) + " in " + str(auto_mob_timer_delay) + " seconds."
        )
    timer_q.put(
        eqa_struct.timer(
            (datetime.datetime.now() + datetime.timedelta(seconds=timer_seconds)),
            "timer",
            str(timer_seconds),
            pop_message,
        )
    )


def send_alerts(line_type, check_line, configs, sound_q, display_q, mute_list):
    """Send messages to sound and display queues"""

    try:
        # Check Sender
        sender = re.findall(r"^([\w\-]+)", check_line)

        if configs.alerts.config["line"][line_type]["sound"] == True:
            if (
                not (line_type, sender[0].lower()) in mute_list
                and not (line_type, "all") in mute_list
            ):
                sound_q.put(eqa_struct.sound("speak", check_line))
                display_q.put(
                    eqa_struct.display(
                        eqa_settings.eqa_time(),
                        "event",
                        "events",
                        line_type + ": " + check_line,
                    )
                )
            else:
                display_q.put(
                    eqa_struct.display(
                        eqa_settings.eqa_time(),
                        "event",
                        "events",
                        line_type + " (MUTED): " + check_line,
                    )
                )

        elif configs.alerts.config["line"][line_type]["sound"] != False:
            if (
                not (line_type, sender[0].lower()) in mute_list
                and not (line_type, "all") in mute_list
            ):
                sound_q.put(eqa_struct.sound("alert", line_type))
                display_q.put(
                    eqa_struct.display(
                        eqa_settings.eqa_time(),
                        "event",
                        "events",
                        line_type + ": " + check_line,
                    )
                )
            else:
                display_q.put(
                    eqa_struct.display(
                        eqa_settings.eqa_time(),
                        "event",
                        "events",
                        line_type + " (MUTED): " + check_line,
                    )
                )

    except Exception as e:
        eqa_settings.log(
            "send alerts: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def send_keyphrase_alerts(
    line_type, check_line, configs, sound_q, display_q, keyphrase, context, mute_list
):
    """Send keyphrase messages to sound and display queues"""

    try:
        # Check Sender
        sender = re.findall(r"^([\w\-]+)", check_line)

        if configs.alerts.config["line"][line_type]["sound"] == True:
            if keyphrase == "assist" or keyphrase == "rampage" or keyphrase == "spot":
                payload = keyphrase + " on " + sender[0]
            else:
                payload = keyphrase
            if (
                not (line_type, sender[0].lower()) in mute_list
                and not (line_type, "all") in mute_list
            ):
                if context == True:
                    sound_q.put(eqa_struct.sound("speak", check_line))
                elif context != False:
                    sound_q.put(eqa_struct.sound("speak", payload))
                display_q.put(
                    eqa_struct.display(
                        eqa_settings.eqa_time(),
                        "event",
                        "events",
                        line_type + ": [" + payload + "] " + check_line,
                    )
                )
            else:
                display_q.put(
                    eqa_struct.display(
                        eqa_settings.eqa_time(),
                        "event",
                        "events",
                        line_type + " (MUTED): [" + payload + "] " + check_line,
                    )
                )

        elif configs.alerts.config["line"][line_type]["sound"] != False:
            if keyphrase == "assist" or keyphrase == "rampage" or keyphrase == "spot":
                payload = keyphrase + " on " + sender[0]
            else:
                payload = keyphrase
            if (
                not (line_type, sender[0].lower()) in mute_list
                and not (line_type, "all") in mute_list
            ):
                if context == True:
                    sound_q.put(eqa_struct.sound("alert", line_type))
                elif context != False:
                    sound_q.put(eqa_struct.sound("speak", payload))
                display_q.put(
                    eqa_struct.display(
                        eqa_settings.eqa_time(),
                        "event",
                        "events",
                        line_type + ": [" + payload + "] " + check_line,
                    )
                )
            else:
                display_q.put(
                    eqa_struct.display(
                        eqa_settings.eqa_time(),
                        "event",
                        "events",
                        line_type + " (MUTED): [" + payload + "] " + check_line,
                    )
                )

    except Exception as e:
        eqa_settings.log(
            "send keyphrase alerts: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def reaction_context(
    line_type, check_line, configs, sound_q, display_q, state, mute_list, reaction
):
    """Reactions for when reaction is a context"""

    try:
        # Or if line_type reaction is all
        if reaction == "all":
            send_alerts(
                line_type,
                check_line,
                configs,
                sound_q,
                display_q,
                mute_list,
            )

        # Or if line_type reaction is solo_only and you are solo and not in a raid
        elif reaction == "solo_only" and not state.group and not state.raid:
            send_alerts(
                line_type,
                check_line,
                configs,
                sound_q,
                display_q,
                mute_list,
            )

        # Or if line_type reaction is solo and you are solo and not in a raid
        elif reaction == "solo" and not state.group and not state.raid:
            send_alerts(
                line_type,
                check_line,
                configs,
                sound_q,
                display_q,
                mute_list,
            )

        # Or if line_type reaction is solo and you are grouped but not in a raid
        elif reaction == "solo" and state.group and not state.raid:
            send_alerts(
                line_type,
                check_line,
                configs,
                sound_q,
                display_q,
                mute_list,
            )

        # Or if line_type reaction is solo_group_only and you are not in a raid
        elif reaction == "solo_group_only" and not state.raid:
            send_alerts(
                line_type,
                check_line,
                configs,
                sound_q,
                display_q,
                mute_list,
            )

        # Or if line_type reaction group_only and you are grouped but not in a raid
        elif reaction == "group_only" and state.group and not state.raid:
            send_alerts(
                line_type,
                check_line,
                configs,
                sound_q,
                display_q,
                mute_list,
            )

        # Or if line_type reaction is group and you are grouped but not in a raid
        elif reaction == "group" and state.group and not state.raid:
            send_alerts(
                line_type,
                check_line,
                configs,
                sound_q,
                display_q,
                mute_list,
            )

        # Or if line_type reaction is solo regardless of group state and in a raid
        elif reaction == "solo" and state.raid:
            send_alerts(
                line_type,
                check_line,
                configs,
                sound_q,
                display_q,
                mute_list,
            )

        # Or if line_type reaction is group regardless of group state and in a raid
        elif reaction == "group" and state.raid:
            send_alerts(
                line_type,
                check_line,
                configs,
                sound_q,
                display_q,
                mute_list,
            )

        # Or if line_type reaction is raid regardless of group state and in a raid
        elif reaction == "raid" and state.raid:
            send_alerts(
                line_type,
                check_line,
                configs,
                sound_q,
                display_q,
                mute_list,
            )

        # Or if line_type reaction is afk and you are afk
        elif reaction == "afk" and state.afk:
            send_alerts(
                line_type,
                check_line,
                configs,
                sound_q,
                display_q,
                mute_list,
            )

    except Exception as e:
        eqa_settings.log(
            "reaction context: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def reaction_alert(
    line_type, check_line, configs, sound_q, display_q, state, mute_list
):
    """Reactions for when reaction is alert"""

    try:
        for keyphrase, value in configs.alerts.config["line"][line_type][
            "alert"
        ].items():
            # If the alert value is true
            if str(keyphrase).lower() in check_line.lower():
                if value == True:
                    send_keyphrase_alerts(
                        line_type,
                        check_line,
                        configs,
                        sound_q,
                        display_q,
                        keyphrase,
                        value,
                        mute_list,
                    )
                # If the alert value is solo_only
                elif value == "solo_only" and not state.group and not state.raid:
                    send_keyphrase_alerts(
                        line_type,
                        check_line,
                        configs,
                        sound_q,
                        display_q,
                        keyphrase,
                        value,
                        mute_list,
                    )
                # If the alert value is solo
                elif value == "solo" and not state.group and not state.raid:
                    send_keyphrase_alerts(
                        line_type,
                        check_line,
                        configs,
                        sound_q,
                        display_q,
                        keyphrase,
                        value,
                        mute_list,
                    )
                # If the alert value is group
                elif value == "group" and state.group and not state.raid:
                    send_keyphrase_alerts(
                        line_type,
                        check_line,
                        configs,
                        sound_q,
                        display_q,
                        keyphrase,
                        value,
                        mute_list,
                    )
                # If the alert value is group_only
                elif value == "group_only" and state.group and not state.raid:
                    send_keyphrase_alerts(
                        line_type,
                        check_line,
                        configs,
                        sound_q,
                        display_q,
                        keyphrase,
                        value,
                        mute_list,
                    )
                # If the alert value is solo, but you are grouped
                elif value == "solo" and state.group and not state.raid:
                    send_keyphrase_alerts(
                        line_type,
                        check_line,
                        configs,
                        sound_q,
                        display_q,
                        keyphrase,
                        value,
                        mute_list,
                    )
                # If the alert value is solo_group_only
                elif value == "solo_group_only" and not state.raid:
                    send_keyphrase_alerts(
                        line_type,
                        check_line,
                        configs,
                        sound_q,
                        display_q,
                        keyphrase,
                        value,
                        mute_list,
                    )
                # If the alert value is raid
                elif value == "raid" and state.raid:
                    send_keyphrase_alerts(
                        line_type,
                        check_line,
                        configs,
                        sound_q,
                        display_q,
                        keyphrase,
                        value,
                        mute_list,
                    )
                # If the alert value is group, but you are in a raid
                elif value == "group" and state.raid:
                    send_keyphrase_alerts(
                        line_type,
                        check_line,
                        configs,
                        sound_q,
                        display_q,
                        keyphrase,
                        value,
                        mute_list,
                    )
                # If the alert value is solo, but you are in a raid
                elif value == "solo" and state.raid:
                    send_keyphrase_alerts(
                        line_type,
                        check_line,
                        configs,
                        sound_q,
                        display_q,
                        keyphrase,
                        value,
                        mute_list,
                    )

    except Exception as e:
        eqa_settings.log(
            "reaction alert: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def action_consider_evaluation(sound_q, check_line):
    """Evaluate consider lines"""

    try:
        faction, level = check_line.split(" -- ")
        if "threateningly" in faction or "scowls" in faction:
            if (
                "gamble" in level
                or "floor" in level
                or "tombstone" in level
                or "formidable" in level
            ):
                danger = True
            else:
                danger = False
        else:
            danger = False

        if danger:
            sound_q.put(eqa_struct.sound("speak", "danger"))
        else:
            sound_q.put(eqa_struct.sound("speak", "safe"))

    except Exception as e:
        eqa_settings.log(
            "action consider evaluate: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def action_motd_welcome(system_q):
    """Perform actions for motd welcome line types"""

    try:
        # Remove group
        system_q.put(
            eqa_struct.message(
                eqa_settings.eqa_time(),
                "system",
                "group",
                None,
                False,
            )
        )
        # Remove group leader
        system_q.put(
            eqa_struct.message(
                eqa_settings.eqa_time(),
                "system",
                "leader",
                None,
                False,
            )
        )
        # Remove AFK
        system_q.put(
            eqa_struct.message(
                eqa_settings.eqa_time(),
                "system",
                "afk",
                None,
                False,
            )
        )

    except Exception as e:
        eqa_settings.log(
            "action motd welcome: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def action_group_alone(system_q):
    """Perform actions for group alone line types"""

    try:
        system_q.put(
            eqa_struct.message(
                eqa_settings.eqa_time(),
                "system",
                "group",
                None,
                False,
            )
        )
        system_q.put(
            eqa_struct.message(
                eqa_settings.eqa_time(),
                "system",
                "leader",
                None,
                False,
            )
        )

    except Exception as e:
        eqa_settings.log(
            "action group alone: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def action_group_created(system_q):
    """Perform actions for group created line types"""

    try:
        system_q.put(
            eqa_struct.message(
                eqa_settings.eqa_time(),
                "system",
                "group",
                None,
                True,
            )
        )
        system_q.put(
            eqa_struct.message(
                eqa_settings.eqa_time(),
                "system",
                "leader",
                None,
                "you",
            )
        )

    except Exception as e:
        eqa_settings.log(
            "action group created: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def action_group_removed(system_q):
    """Perform actions for group removed line types"""

    try:
        system_q.put(
            eqa_struct.message(
                eqa_settings.eqa_time(),
                "system",
                "group",
                None,
                False,
            )
        )
        system_q.put(
            eqa_struct.message(
                eqa_settings.eqa_time(),
                "system",
                "leader",
                None,
                False,
            )
        )

    except Exception as e:
        eqa_settings.log(
            "action group removed: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def action_group_disbanded(system_q):
    """Perform actions for group disbanded line types"""

    try:
        system_q.put(
            eqa_struct.message(
                eqa_settings.eqa_time(),
                "system",
                "group",
                None,
                False,
            )
        )
        system_q.put(
            eqa_struct.message(
                eqa_settings.eqa_time(),
                "system",
                "leader",
                None,
                False,
            )
        )

    except Exception as e:
        eqa_settings.log(
            "action group disbanded: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def action_group_join_notify(system_q, check_line):
    """Perform actions for group joined line types"""

    try:
        leader = re.findall(r"(?<=You notify )\w+", check_line)
        system_q.put(
            eqa_struct.message(
                eqa_settings.eqa_time(),
                "system",
                "group",
                None,
                True,
            )
        )
        system_q.put(
            eqa_struct.message(
                eqa_settings.eqa_time(),
                "system",
                "leader",
                None,
                leader[0],
            )
        )

    except Exception as e:
        eqa_settings.log(
            "action group joined: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def action_group_leader_you(system_q):
    """Perform actions for group leader you line types"""

    try:
        system_q.put(
            eqa_struct.message(
                eqa_settings.eqa_time(),
                "system",
                "leader",
                None,
                "you",
            )
        )

    except Exception as e:
        eqa_settings.log(
            "action group leader you: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def action_group_leader_other(system_q, check_line):
    """Perform actions for group leader you line types"""

    try:
        leader = re.findall(r"^\w+", check_line)
        system_q.put(
            eqa_struct.message(
                eqa_settings.eqa_time(),
                "system",
                "leader",
                None,
                leader[0].lower(),
            )
        )

    except Exception as e:
        eqa_settings.log(
            "action group leader other: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def action_encumbered_off(system_q):
    """Perform actions for encumbered off line types"""

    try:
        system_q.put(
            eqa_struct.message(
                eqa_settings.eqa_time(),
                "system",
                "encumbered",
                None,
                False,
            )
        )

    except Exception as e:
        eqa_settings.log(
            "action encumbered off: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def action_encumbered_on(system_q):
    """Perform actions for encumbered on line types"""

    try:
        system_q.put(
            eqa_struct.message(
                eqa_settings.eqa_time(),
                "system",
                "encumbered",
                None,
                True,
            )
        )

    except Exception as e:
        eqa_settings.log(
            "action encumbered on: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def action_direction(system_q, check_line):
    """Perform actions for direction line types"""

    try:
        direction = re.findall(
            "(?:North(?:East|West)?|South(?:East|West)?|(?:Ea|We)st)",
            check_line,
        )
        system_q.put(
            eqa_struct.message(
                eqa_settings.eqa_time(),
                "system",
                "direction",
                None,
                direction[0],
            )
        )

    except Exception as e:
        eqa_settings.log(
            "action direction: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def action_location(system_q, check_line):
    """Perform actions for direction line types"""

    try:
        y, x, z = re.findall("[-]?(?:\d*\.)?\d+", check_line)
        loc = [y, x, z]
        system_q.put(
            eqa_struct.message(eqa_settings.eqa_time(), "system", "loc", None, loc)
        )

    except Exception as e:
        eqa_settings.log(
            "action location: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def action_you_say_commands(
    timer_q,
    system_q,
    sound_q,
    display_q,
    check_line,
    configs,
    mute_list,
    state,
    player_list,
):
    """Perform actions for parser say commands"""

    try:
        if re.findall(r"(?<=You say, \'parser )[a-zA-Z\d\s]+", check_line) is not None:
            check_line_clean = re.sub(r"[^\w\s\d\,]", "", check_line)
            args = re.findall(r"(?<=You say, parser )[a-zA-Z\d\s]+", check_line_clean)[
                0
            ].split(" ")
            if args[0] == "mute":
                if len(args) == 1:
                    system_q.put(
                        eqa_struct.message(
                            eqa_settings.eqa_time(),
                            "system",
                            "mute",
                            "toggle",
                            "all",
                        )
                    )
                elif args[1] == "speak":
                    system_q.put(
                        eqa_struct.message(
                            eqa_settings.eqa_time(),
                            "system",
                            "mute",
                            "toggle",
                            "speak",
                        )
                    )
                elif args[1] == "alert":
                    system_q.put(
                        eqa_struct.message(
                            eqa_settings.eqa_time(),
                            "system",
                            "mute",
                            "toggle",
                            "alert",
                        )
                    )
                elif args[1] == "clear":
                    mute_list.clear()
                    display_q.put(
                        eqa_struct.display(
                            eqa_settings.eqa_time(),
                            "event",
                            "events",
                            "Muted list cleared",
                        )
                    )
                elif args[1] in configs.alerts.config["line"]:
                    if len(args) == 2:
                        if not (args[1], "all") in mute_list:
                            mute_list.append((args[1], "all"))
                            display_q.put(
                                eqa_struct.display(
                                    eqa_settings.eqa_time(),
                                    "event",
                                    "events",
                                    "Muted: " + args[1],
                                )
                            )
                    elif len(args) == 3:
                        if not (args[1], args[2]) in mute_list:
                            mute_list.append((args[1], args[2]))
                            display_q.put(
                                eqa_struct.display(
                                    eqa_settings.eqa_time(),
                                    "event",
                                    "events",
                                    "Muted: " + args[2] + " in " + args[1],
                                )
                            )
            elif args[0] == "unmute":
                if len(args) == 1:
                    system_q.put(
                        eqa_struct.message(
                            eqa_settings.eqa_time(),
                            "system",
                            "mute",
                            "toggle",
                            "all",
                        )
                    )
                elif args[1] == "speak":
                    system_q.put(
                        eqa_struct.message(
                            eqa_settings.eqa_time(),
                            "system",
                            "mute",
                            "toggle",
                            "speak",
                        )
                    )
                elif args[1] == "alert":
                    system_q.put(
                        eqa_struct.message(
                            eqa_settings.eqa_time(),
                            "system",
                            "mute",
                            "toggle",
                            "alert",
                        )
                    )
                elif args[1] in configs.alerts.config["line"]:
                    if len(args) == 2:
                        if (args[1], "all") in mute_list:
                            mute_list.remove((args[1], "all"))
                            display_q.put(
                                eqa_struct.display(
                                    eqa_settings.eqa_time(),
                                    "event",
                                    "events",
                                    "Unmuted: " + args[1],
                                )
                            )
                    elif len(args) == 3:
                        if (args[1], args[2]) in mute_list:
                            mute_list.remove((args[1], args[2]))
                            display_q.put(
                                eqa_struct.display(
                                    eqa_settings.eqa_time(),
                                    "event",
                                    "events",
                                    "Unmuted: " + args[2] + " in " + args[1],
                                )
                            )
            elif args[0] == "raid":
                system_q.put(
                    eqa_struct.message(
                        eqa_settings.eqa_time(),
                        "system",
                        "raid",
                        "toggle",
                        None,
                    )
                )
            elif args[0] == "consider":
                if state.consider_eval:
                    system_q.put(
                        eqa_struct.message(
                            eqa_settings.eqa_time(),
                            "system",
                            "consider",
                            "eval",
                            False,
                        )
                    )
                else:
                    system_q.put(
                        eqa_struct.message(
                            eqa_settings.eqa_time(),
                            "system",
                            "consider",
                            "eval",
                            True,
                        )
                    )
            elif args[0] == "debug":
                system_q.put(
                    eqa_struct.message(
                        eqa_settings.eqa_time(),
                        "system",
                        "debug",
                        "toggle",
                        None,
                    )
                )
            elif args[0] == "reload":
                system_q.put(
                    eqa_struct.message(
                        eqa_settings.eqa_time(),
                        "system",
                        "reload_config",
                        None,
                        None,
                    )
                )
            elif args[0] == "encounter":
                if len(args) == 1:
                    system_q.put(
                        eqa_struct.message(
                            eqa_settings.eqa_time(),
                            "system",
                            "encounter",
                            "toggle",
                            None,
                        )
                    )
                elif args[1] == "clear":
                    system_q.put(
                        eqa_struct.message(
                            eqa_settings.eqa_time(),
                            "system",
                            "encounter",
                            "clear",
                            None,
                        )
                    )
                elif args[1] == "end":
                    system_q.put(
                        eqa_struct.message(
                            eqa_settings.eqa_time(),
                            "system",
                            "encounter",
                            "end",
                            None,
                        )
                    )
                elif args[1] == "start":
                    system_q.put(
                        eqa_struct.message(
                            eqa_settings.eqa_time(),
                            "system",
                            "encounter",
                            "start",
                            None,
                        )
                    )
            elif args[0] == "what":
                if len(args) == 1:
                    sound_q.put(eqa_struct.sound("speak", "What what?"))
                elif args[1] == "state":
                    sound_q.put(
                        eqa_struct.sound(
                            "speak",
                            "Current State: Playing on: "
                            + state.server
                            + " as "
                            + state.char
                            + " level "
                            + str(state.char_level)
                            + " "
                            + str(state.char_class)
                            + " of "
                            + str(state.char_guild)
                            + ". Bound in "
                            + str(state.bind)
                            + " and currently in "
                            + str(state.zone)
                            + " facing "
                            + str(state.direction)
                            + " around "
                            + str(state.loc)
                            + ". Group state is "
                            + str(state.group)
                            + ". Leader state is "
                            + str(state.leader)
                            + ". Raid state is "
                            + str(state.raid)
                            + ". AFK state is "
                            + str(state.afk)
                            + ". Encumbered state is "
                            + str(state.encumbered)
                            + ". Debug state is "
                            + str(state.debug)
                            + ". Encounter parser state is "
                            + str(state.encounter_parse),
                        )
                    )
                elif args[1] == "context":
                    if not state.group and not state.raid:
                        context = "solo"
                    elif state.group and not state.raid:
                        context = "group"
                    elif state.raid:
                        context = "raid"
                    elif state.afk:
                        context = "afk"
                    sound_q.put(
                        eqa_struct.sound("You are in a " + context + " context.")
                    )
            elif args[0] == "test":
                if len(args) == 1:
                    sound_q.put(
                        eqa_struct.sound(
                            "speak",
                            "The Enrichment Center promises to always provide a safe testing environment.",
                        )
                    )
            elif args[0] == "hello":
                if len(args) == 1:
                    sound_q.put(
                        eqa_struct.sound(
                            "speak",
                            "Hello! Thank you for using this parser. I hope it is useful and fun :P",
                        )
                    )
            elif args[0] == "thanks":
                if len(args) == 1:
                    sound_q.put(
                        eqa_struct.sound(
                            "speak",
                            "No, no. Thank you!",
                        )
                    )
            elif args[0] == "where":
                if len(args) == 1:
                    sound_q.put(
                        eqa_struct.sound(
                            "speak",
                            "I think you're still in "
                            + str(state.zone)
                            + ", but considering the circumstances you could be anywhere.",
                        )
                    )
            elif args[0] == "who":
                if len(args) == 1:
                    sound_q.put(
                        eqa_struct.sound(
                            "speak",
                            "You are " + state.char + ", right?",
                        )
                    )
                elif args[1] in player_list.keys():
                    if (
                        player_list[args[1]]["class"] == None
                        and player_list[args[1]]["guild"] == None
                        and player_list[args[1]]["level"] == 0
                    ):
                        message = "I only know their name"
                    else:
                        message = args[1] + " is "
                        if player_list[args[1]]["level"] > 0:
                            message = (
                                message + " a level " + player_list[args[1]]["level"]
                            )
                        if player_list[args[1]]["class"] is not None:
                            message = message + " " + player_list[args[1]]["class"]
                        else:
                            message = message + " character"
                        if player_list[args[1]]["guild"] is not None:
                            message = message + " in " + player_list[args[1]]["guild"]
                    sound_q.put(eqa_struct.sound("speak", message))
                else:
                    sound_q.put(eqa_struct.sound("speak", "I'm not sure who that is"))
            elif args[0] == "why":
                if len(args) == 1:
                    sound_q.put(
                        eqa_struct.sound(
                            "speak",
                            "Did you choose the "
                            + str(state.char_class)
                            + " life, or did the "
                            + str(state.char_class)
                            + " life choose you?",
                        )
                    )
            elif args[0] == "ping":
                if len(args) == 1:
                    sound_q.put(
                        eqa_struct.sound(
                            "speak",
                            "pong",
                        )
                    )
            elif args[0] == "metronome":
                if len(args) == 1:
                    sound_q.put(
                        eqa_struct.sound(
                            "speak",
                            "Metronome what?",
                        )
                    )
                elif len(args) == 2:
                    if args[1].isdigit():
                        metro_seconds = int(args[1])
                        if metro_seconds < 300:
                            timer_q.put(
                                eqa_struct.timer(
                                    (
                                        datetime.datetime.now()
                                        + datetime.timedelta(seconds=metro_seconds)
                                    ),
                                    "metronome",
                                    str(metro_seconds),
                                    None,
                                )
                            )
                    elif args[1] == "stop":
                        timer_q.put(
                            eqa_struct.timer(None, "metronome_stop", None, None)
                        )
                    else:
                        sound_q.put(
                            eqa_struct.sound(
                                "speak",
                                "That command wasn't quite right",
                            )
                        )
            elif args[0] == "timer":
                if len(args) == 1:
                    sound_q.put(
                        eqa_struct.sound(
                            "speak",
                            "I don't get it. Timer what?",
                        )
                    )
                elif len(args) == 2:
                    if args[1].isdigit():
                        timer_seconds = int(args[1])
                        timer_q.put(
                            eqa_struct.timer(
                                (
                                    datetime.datetime.now()
                                    + datetime.timedelta(seconds=timer_seconds)
                                ),
                                "timer",
                                str(timer_seconds),
                                "times up",
                            )
                        )
                    elif args[1] == "clear":
                        timer_q.put(eqa_struct.timer(None, "clear", None, None))
                    elif args[1] == "respawn":
                        system_q.put(
                            eqa_struct.message(
                                eqa_settings.eqa_time(),
                                "system",
                                "timer",
                                "mob",
                                True,
                            )
                        )
                    else:
                        sound_q.put(
                            eqa_struct.sound(
                                "speak",
                                "Something wasn't quite right with that",
                            )
                        )
                elif len(args) == 3:
                    if args[1] == "respawn" and args[2] == "stop":
                        system_q.put(
                            eqa_struct.message(
                                eqa_settings.eqa_time(),
                                "system",
                                "timer",
                                "mob",
                                False,
                            )
                        )
            else:
                display_q.put(
                    eqa_struct.display(
                        eqa_settings.eqa_time(),
                        "event",
                        "events",
                        "Unknown parser command",
                    )
                )
                sound_q.put(eqa_struct.sound("speak", "Unknown parser command"))

    except Exception as e:
        eqa_settings.log(
            "action you say command: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def action_you_afk_off(system_q):
    """Perform actions for you_afk_off line types"""

    try:
        system_q.put(
            eqa_struct.message(
                eqa_settings.eqa_time(),
                "system",
                "afk",
                None,
                False,
            )
        )

    except Exception as e:
        eqa_settings.log(
            "action you afk: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def action_you_afk_on(system_q):
    """Perform actions for you_afk_on line types"""

    try:
        system_q.put(
            eqa_struct.message(
                eqa_settings.eqa_time(),
                "system",
                "afk",
                None,
                True,
            )
        )

    except Exception as e:
        eqa_settings.log(
            "action you afk: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def action_spell_bind_you(system_q, state):
    """Perform actions for spell bind you line types"""

    try:
        system_q.put(
            eqa_struct.message(
                eqa_settings.eqa_time(),
                "system",
                "bind",
                None,
                str(state.zone),
            )
        )

    except Exception as e:
        eqa_settings.log(
            "action you char bound: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def action_you_char_bound(system_q, check_line):
    """Perform actions for you char bound line types"""

    try:
        bound_zone = re.findall(
            "(?<=You are currently bound in\: )[a-zA-Z\s]+", check_line
        )
        system_q.put(
            eqa_struct.message(
                eqa_settings.eqa_time(),
                "system",
                "bind",
                None,
                bound_zone[0],
            )
        )

    except Exception as e:
        eqa_settings.log(
            "action you char bound: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def action_who_player(configs, system_q, state, line, player_list, class_mapping):
    """Parse who_player to determine name, level, class, and guild to update players_list"""

    try:
        char_level = 0
        char_class = None
        char_guild = None

        # Find level and class
        if re.findall(r"\[\d+ [a-zA-Z\s]+\]", line):
            char_level, char_class = re.findall(r"\d+ [a-zA-Z\s]+", line)[0].split(
                " ", 1
            )
            char_level = int(char_level)
            char_class = class_mapping[char_class.lower()]

        # Find guild
        if re.fullmatch(r".+\<[a-zA-Z\s]+\>(.+|)", line) is not None:
            char_guild = re.findall(r"(?<=\<)[a-zA-Z\s]+", line)[0].lower()

        # Find name
        char_name = re.findall(r"(?<=\]\ )[a-zA-Z]+", line)[0].lower()

        # Update players_list
        if char_name in player_list.keys():
            if char_guild is not None:
                if char_guild != player_list[char_name]["guild"]:
                    player_list[char_name]["guild"] = char_guild
            if char_level > 0:
                if char_level != player_list[char_name]["level"]:
                    player_list[char_name]["level"] = char_level
            if char_class is not None:
                if char_class != player_list[char_name]["class"]:
                    player_list[char_name]["class"] = char_class
        else:
            player_list[char_name] = {
                "class": char_class,
                "level": char_level,
                "guild": char_guild,
            }

        # Update internal character state
        if state.char.lower() == char_name:
            if char_level > 0:
                system_q.put(
                    eqa_struct.message(
                        eqa_settings.eqa_time(),
                        "system",
                        "level",
                        None,
                        char_level,
                    )
                )

            if char_class is not None:
                system_q.put(
                    eqa_struct.message(
                        eqa_settings.eqa_time(),
                        "system",
                        "class",
                        None,
                        char_class.title(),
                    )
                )

            if char_guild is not None:
                system_q.put(
                    eqa_struct.message(
                        eqa_settings.eqa_time(),
                        "system",
                        "guild",
                        None,
                        char_guild,
                    )
                )

    except Exception as e:
        eqa_settings.log(
            "action who player: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def action_you_new_zone(
    base_path, system_q, display_q, sound_q, timer_q, state, configs, check_line
):
    """Perform actions for you new zone line types"""

    try:
        current_zone = re.findall("(?<=You have entered )[a-zA-Z\-'\s]+", check_line)
        system_q.put(
            eqa_struct.message(
                eqa_settings.eqa_time(),
                "system",
                "afk",
                None,
                False,
            )
        )

        if current_zone[0] != state.zone:
            display_q.put(
                eqa_struct.display(
                    eqa_settings.eqa_time(), "update", "zone", current_zone[0]
                )
            )
            system_q.put(
                eqa_struct.message(
                    eqa_settings.eqa_time(),
                    "system",
                    "zone",
                    None,
                    current_zone[0],
                )
            )

        if current_zone[0] not in configs.zones.config["zones"].keys():
            eqa_config.add_zone(current_zone[0], base_path)
        elif current_zone[0] in configs.zones.config["zones"].keys() and not state.raid:
            if (
                configs.zones.config["zones"][current_zone[0]]["raid_mode"]
                and state.auto_raid
            ):
                system_q.put(
                    eqa_struct.message(
                        eqa_settings.eqa_time(),
                        "system",
                        "raid",
                        True,
                        "Raid mode auto-enabled",
                    )
                )
        elif current_zone[0] in configs.zones.config["zones"].keys() and state.raid:
            if (
                not configs.zones.config["zones"][current_zone[0]]["raid_mode"]
                and state.auto_raid
            ):
                system_q.put(
                    eqa_struct.message(
                        eqa_settings.eqa_time(),
                        "system",
                        "raid",
                        False,
                        "Raid mode auto-disabled",
                    )
                )

        if state.spell_timer_self or state.spell_timer_other:
            timer_q.put(
                eqa_struct.timer(
                    datetime.datetime.now(),
                    "new_zone",
                    None,
                    None,
                )
            )

    except Exception as e:
        eqa_settings.log(
            "action you new zone: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def action_matched(line_type, line, base_path, version):
    """Debug function to log all log lines and matches log lines"""

    try:
        matched_log = base_path + "log/debug/matched-lines.txt"
        if os.path.exists(matched_log):
            file_size = os.path.getsize(matched_log)
            if file_size >= 10000000:
                version = version.replace(".", "-")
                archived_log = (
                    base_path
                    + "log/debug/matched-lines_"
                    + version
                    + "_"
                    + str(datetime.datetime.now().date())
                    + ".txt"
                )
                os.rename(matched_log, archived_log)
        matched_log_file = open(matched_log, "a")
        matched_log_file.write("%-30s : %-70s\n" % (line_type, line))
        matched_log_file.close()

    except Exception as e:
        eqa_settings.log(
            "action matched: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


if __name__ == "__main__":
    main()
