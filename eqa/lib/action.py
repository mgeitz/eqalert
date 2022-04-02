#! /usr/bin/env python

"""
   Program:   EQ Alert
   File Name: eqa/lib/action.py
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

import datetime
import sys
import time
import re
import os
import pkg_resources
from datetime import datetime

import eqa.lib.config as eqa_config
import eqa.lib.settings as eqa_settings
import eqa.lib.sound as eqa_sound
import eqa.lib.struct as eqa_struct

mute_list = []


def process(
    config,
    base_path,
    state,
    action_q,
    system_q,
    display_q,
    sound_q,
    exit_flag,
    cfg_reload,
):
    """
    Process: action_q
    Produce: sound_q, display_q, system_q
    """

    try:
        while not exit_flag.is_set() and not cfg_reload.is_set():
            time.sleep(0.01)
            if not action_q.empty():
                new_message = action_q.get()
                action_q.task_done()
                line_type = new_message.type
                line_time = new_message.timestamp
                line_tx = new_message.tx
                line_rx = new_message.rx
                check_line = new_message.payload

                # Debug modes
                if state.debug != "false":
                    if line_type == "undetermined":
                        action_undetermined(check_line, base_path)
                    if state.debug == "all":
                        action_matched(line_type, check_line, base_path)

                # Line specific checks
                if line_type == "location":
                    action_location(system_q, check_line)
                elif line_type == "direction":
                    action_direction(system_q, check_line)
                elif line_type == "motd_welcome":
                    action_motd_welcome(system_q)
                elif line_type == "group_join_notify":
                    action_group_join_notify(system_q, check_line)
                elif line_type == "group_removed":
                    action_group_removed(system_q)
                elif line_type == "group_created":
                    action_group_created(system_q)
                elif line_type == "group_leader_you":
                    action_group_leader_you(system_q)
                elif line_type == "group_leader_other":
                    action_group_leader_other(system_q, check_line)
                elif line_type == "encumbered_off":
                    action_encumbered_off(system_q)
                elif line_type == "encumbered_on":
                    action_encumbered_on(system_q)
                elif line_type == "you_char_bound":
                    action_you_char_bound(system_q, check_line)
                elif line_type == "spell_bind_you":
                    action_spell_bind_you(system_q, state)
                elif line_type == "you_afk_off":
                    action_you_afk_off(system_q)
                elif line_type == "you_afk_on":
                    action_you_afk_on(system_q)
                elif line_type == "who_player":
                    action_who_player(system_q, state, check_line)
                elif line_type == "you_say":
                    if (
                        re.fullmatch(r"^You say, \'parser .+\'$", check_line)
                        is not None
                    ):
                        action_you_say_commands(system_q, check_line, config, mute_list)
                elif line_type == "you_new_zone":
                    action_you_new_zone(
                        base_path,
                        system_q,
                        display_q,
                        sound_q,
                        state,
                        config,
                        check_line,
                    )

                # If line_type exists in the config
                if line_type in config["line"].keys():
                    # If line_type reaction is true
                    if config["line"][line_type]["reaction"] == "alert":
                        for keyphrase, value in config["line"][line_type][
                            "alert"
                        ].items():
                            # If the alert value is true
                            if (
                                str(keyphrase).lower() in check_line.lower()
                                and value == "true"
                            ):
                                if config["line"][line_type]["sound"] != "false":
                                    sound_q.put(eqa_struct.sound("alert", line_type))
                                display_q.put(
                                    eqa_struct.display(
                                        eqa_settings.eqa_time(),
                                        "event",
                                        "events",
                                        line_type + ": " + check_line,
                                    )
                                )
                            # If the alert value is solo_only
                            elif (
                                str(keyphrase).lower() in check_line.lower()
                                and value == "solo_only"
                                and state.group == "false"
                                and state.raid == "false"
                            ):
                                if config["line"][line_type]["sound"] != "false":
                                    sound_q.put(eqa_struct.sound("speak", keyphrase))
                                display_q.put(
                                    eqa_struct.display(
                                        eqa_settings.eqa_time(),
                                        "event",
                                        "events",
                                        "Solo: " + line_type + ": " + check_line,
                                    )
                                )
                            # If the alert value is solo
                            elif (
                                str(keyphrase).lower() in check_line.lower()
                                and value == "solo"
                                and state.group == "false"
                                and state.raid == "false"
                            ):
                                if config["line"][line_type]["sound"] != "false":
                                    sound_q.put(eqa_struct.sound("speak", keyphrase))
                                display_q.put(
                                    eqa_struct.display(
                                        eqa_settings.eqa_time(),
                                        "event",
                                        "events",
                                        "Solo: " + line_type + ": " + check_line,
                                    )
                                )
                            # If the alert value is group
                            elif (
                                str(keyphrase).lower() in check_line.lower()
                                and value == "group"
                                and state.group == "true"
                                and state.raid == "false"
                            ):
                                if keyphrase == "assist" or keyphrase == "rampage":
                                    target = re.findall("^([\w\-]+)", check_line)
                                    payload = keyphrase + " on " + target[0]
                                else:
                                    payload = keyphrase
                                if config["line"][line_type]["sound"] != "false":
                                    sound_q.put(eqa_struct.sound("speak", payload))
                                display_q.put(
                                    eqa_struct.display(
                                        eqa_settings.eqa_time(),
                                        "event",
                                        "events",
                                        "Group: " + line_type + ": " + check_line,
                                    )
                                )
                            # If the alert value is group_only
                            elif (
                                str(keyphrase).lower() in check_line.lower()
                                and value == "group_only"
                                and state.group == "true"
                                and state.raid == "false"
                            ):
                                if keyphrase == "assist" or keyphrase == "rampage":
                                    target = re.findall("^([\w\-]+)", check_line)
                                    payload = keyphrase + " on " + target[0]
                                else:
                                    payload = keyphrase
                                if config["line"][line_type]["sound"] != "false":
                                    sound_q.put(eqa_struct.sound("speak", payload))
                                display_q.put(
                                    eqa_struct.display(
                                        eqa_settings.eqa_time(),
                                        "event",
                                        "events",
                                        "Group: " + line_type + ": " + check_line,
                                    )
                                )
                            # If the alert value is solo, but you are grouped
                            elif (
                                str(keyphrase).lower() in check_line.lower()
                                and value == "solo"
                                and state.group == "true"
                                and state.raid == "false"
                            ):
                                if config["line"][line_type]["sound"] != "false":
                                    sound_q.put(eqa_struct.sound("speak", keyphrase))
                                display_q.put(
                                    eqa_struct.display(
                                        eqa_settings.eqa_time(),
                                        "event",
                                        "events",
                                        "Group: " + line_type + ": " + check_line,
                                    )
                                )
                            # If the alert value is raid
                            elif (
                                str(keyphrase).lower() in check_line.lower()
                                and value == "raid"
                                and state.raid == "true"
                            ):
                                if keyphrase == "assist" or keyphrase == "rampage":
                                    target = re.findall("^([\w\-]+)", check_line)
                                    payload = keyphrase + " on " + target[0]
                                else:
                                    payload = keyphrase
                                if config["line"][line_type]["sound"] != "false":
                                    sound_q.put(eqa_struct.sound("speak", payload))
                                display_q.put(
                                    eqa_struct.display(
                                        eqa_settings.eqa_time(),
                                        "event",
                                        "events",
                                        line_type + ": " + check_line,
                                    )
                                )
                            # If the alert value is group, but you are in a raid
                            elif (
                                str(keyphrase).lower() in check_line.lower()
                                and value == "group"
                                and state.raid == "true"
                            ):
                                if keyphrase == "assist" or keyphrase == "rampage":
                                    target = re.findall("^([\w\-]+)", check_line)
                                    payload = keyphrase + " on " + target[0]
                                else:
                                    payload = keyphrase
                                if config["line"][line_type]["sound"] != "false":
                                    sound_q.put(eqa_struct.sound("speak", payload))
                                display_q.put(
                                    eqa_struct.display(
                                        eqa_settings.eqa_time(),
                                        "event",
                                        "events",
                                        line_type + ": " + check_line,
                                    )
                                )
                            # If the alert value is solo, but you are in a raid
                            elif (
                                str(keyphrase).lower() in check_line.lower()
                                and value == "solo"
                                and state.raid == "true"
                            ):
                                if keyphrase == "assist" or keyphrase == "rampage":
                                    target = re.findall("^([\w\-]+)", check_line)
                                    payload = keyphrase + " on " + target[0]
                                else:
                                    payload = keyphrase
                                if config["line"][line_type]["sound"] != "false":
                                    sound_q.put(eqa_struct.sound("speak", payload))
                                display_q.put(
                                    eqa_struct.display(
                                        eqa_settings.eqa_time(),
                                        "event",
                                        "events",
                                        line_type + ": " + check_line,
                                    )
                                )

                    # Or if line_type reaction is all
                    elif config["line"][line_type]["reaction"] == "all":

                        sender = re.findall(r"^\w+", check_line)
                        if (
                            config["line"][line_type]["sound"] == "true"
                            and not (line_type, sender[0].lower()) in mute_list
                        ):
                            sound_q.put(eqa_struct.sound("speak", check_line))
                        elif config["line"][line_type]["sound"] != "false":
                            sound_q.put(eqa_struct.sound("alert", line_type))
                        display_q.put(
                            eqa_struct.display(
                                eqa_settings.eqa_time(),
                                "event",
                                "events",
                                line_type + ": " + check_line,
                            )
                        )

                    # Or if line_type reaction is solo_only and you are solo and not in a raid
                    elif (
                        config["line"][line_type]["reaction"] == "solo_only"
                        and state.group == "false"
                        and state.raid == "false"
                    ):
                        sender = re.findall(r"^\w+", check_line)
                        if (
                            config["line"][line_type]["sound"] == "true"
                            and not (line_type, sender[0].lower()) in mute_list
                        ):
                            sound_q.put(eqa_struct.sound("speak", check_line))
                        elif config["line"][line_type]["sound"] != "false":
                            sound_q.put(eqa_struct.sound("alert", line_type))
                        display_q.put(
                            eqa_struct.display(
                                eqa_settings.eqa_time(),
                                "event",
                                "events",
                                check_line,
                            )
                        )

                    # Or if line_type reaction is solo and you are solo and not in a raid
                    elif (
                        config["line"][line_type]["reaction"] == "solo"
                        and state.group == "false"
                        and state.raid == "false"
                    ):
                        sender = re.findall(r"^\w+", check_line)
                        if (
                            config["line"][line_type]["sound"] == "true"
                            and not (line_type, sender[0].lower()) in mute_list
                        ):
                            sound_q.put(eqa_struct.sound("speak", check_line))
                        elif config["line"][line_type]["sound"] != "false":
                            sound_q.put(eqa_struct.sound("alert", line_type))
                        display_q.put(
                            eqa_struct.display(
                                eqa_settings.eqa_time(),
                                "event",
                                "events",
                                check_line,
                            )
                        )

                    # Or if line_type reaction is solo and you are grouped but not in a raid
                    elif (
                        config["line"][line_type]["reaction"] == "solo"
                        and state.group == "true"
                        and state.raid == "false"
                    ):
                        sender = re.findall(r"^\w+", check_line)
                        if (
                            config["line"][line_type]["sound"] == "true"
                            and not (line_type, sender[0].lower()) in mute_list
                        ):
                            sound_q.put(eqa_struct.sound("speak", check_line))
                        elif config["line"][line_type]["sound"] != "false":
                            sound_q.put(eqa_struct.sound("alert", line_type))
                        display_q.put(
                            eqa_struct.display(
                                eqa_settings.eqa_time(),
                                "event",
                                "events",
                                check_line,
                            )
                        )

                    # Or if line_type reaction group_only and you are grouped but not in a raid
                    elif (
                        config["line"][line_type]["reaction"] == "group_only"
                        and state.group == "true"
                        and state.raid == "false"
                    ):
                        sender = re.findall(r"^\w+", check_line)
                        if (
                            config["line"][line_type]["sound"] == "true"
                            and not (line_type, sender[0].lower()) in mute_list
                        ):
                            sound_q.put(eqa_struct.sound("speak", check_line))
                        elif config["line"][line_type]["sound"] != "false":
                            sound_q.put(eqa_struct.sound("alert", line_type))
                        display_q.put(
                            eqa_struct.display(
                                eqa_settings.eqa_time(),
                                "event",
                                "events",
                                check_line,
                            )
                        )

                    # Or if line_type reaction is group and you are grouped but not in a raid
                    elif (
                        config["line"][line_type]["reaction"] == "group"
                        and state.group == "true"
                        and state.raid == "false"
                    ):
                        sender = re.findall(r"^\w+", check_line)
                        if (
                            config["line"][line_type]["sound"] == "true"
                            and not (line_type, sender[0].lower()) in mute_list
                        ):
                            sound_q.put(eqa_struct.sound("speak", check_line))
                        elif config["line"][line_type]["sound"] != "false":
                            sound_q.put(eqa_struct.sound("alert", line_type))
                        display_q.put(
                            eqa_struct.display(
                                eqa_settings.eqa_time(),
                                "event",
                                "events",
                                check_line,
                            )
                        )

                    # Or if line_type reaction is solo regardless of group state and in a raid
                    elif (
                        config["line"][line_type]["reaction"] == "solo"
                        and state.raid == "true"
                    ):
                        sender = re.findall(r"^\w+", check_line)
                        if (
                            config["line"][line_type]["sound"] == "true"
                            and not (line_type, sender[0].lower()) in mute_list
                        ):
                            sound_q.put(eqa_struct.sound("speak", check_line))
                        elif config["line"][line_type]["sound"] != "false":
                            sound_q.put(eqa_struct.sound("alert", line_type))
                        display_q.put(
                            eqa_struct.display(
                                eqa_settings.eqa_time(),
                                "event",
                                "events",
                                check_line,
                            )
                        )

                    # Or if line_type reaction is group regardless of group state and in a raid
                    elif (
                        config["line"][line_type]["reaction"] == "group"
                        and state.raid == "true"
                    ):
                        sender = re.findall(r"^\w+", check_line)
                        if (
                            config["line"][line_type]["sound"] == "true"
                            and not (line_type, sender[0].lower()) in mute_list
                        ):
                            sound_q.put(eqa_struct.sound("speak", check_line))
                        elif config["line"][line_type]["sound"] != "false":
                            sound_q.put(eqa_struct.sound("alert", line_type))
                        display_q.put(
                            eqa_struct.display(
                                eqa_settings.eqa_time(),
                                "event",
                                "events",
                                check_line,
                            )
                        )

                    # Or if line_type reaction is raid regardless of group state and in a raid
                    elif (
                        config["line"][line_type]["reaction"] == "raid"
                        and state.raid == "true"
                    ):
                        sender = re.findall(r"^\w+", check_line)
                        if (
                            config["line"][line_type]["sound"] == "true"
                            and not (line_type, sender[0].lower()) in mute_list
                        ):
                            sound_q.put(eqa_struct.sound("speak", check_line))
                        elif config["line"][line_type]["sound"] != "false":
                            sound_q.put(eqa_struct.sound("alert", line_type))
                        display_q.put(
                            eqa_struct.display(
                                eqa_settings.eqa_time(),
                                "event",
                                "events",
                                check_line,
                            )
                        )

                    # Or if line_type reaction is afk and you are afk
                    elif (
                        config["line"][line_type]["reaction"] == "afk"
                        and state.afk == "true"
                    ):
                        sender = re.findall(r"^\w+", check_line)
                        if (
                            config["line"][line_type]["sound"] == "true"
                            and not (line_type, sender[0].lower()) in mute_list
                        ):
                            sound_q.put(eqa_struct.sound("speak", check_line))
                        elif config["line"][line_type]["sound"] != "false":
                            sound_q.put(eqa_struct.sound("alert", line_type))
                        display_q.put(
                            eqa_struct.display(
                                eqa_settings.eqa_time(),
                                "event",
                                "events",
                                check_line,
                            )
                        )

                    # For alerts for all matched lines
                    if config["line"]["all"]["reaction"] == "true":
                        for keyphrase, value in config["alert"]["all"].items():
                            if keyphrase in check_line.lower():
                                if config["line"]["all"]["sound"] != "false":
                                    sound_q.put(eqa_struct.sound("alert", line_type))
                                display_q.put(
                                    eqa_struct.display(
                                        eqa_settings.eqa_time(),
                                        "event",
                                        "events",
                                        line_type + ": " + check_line,
                                    )
                                )

                # If line_type is not in the config
                else:
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
                            "null",
                            "null",
                        )
                    )

    except Exception as e:
        eqa_settings.log(
            "process action: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )

    sys.exit(0)


def action_motd_welcome(system_q):
    """Perform actions for motd welcome line types"""

    try:
        system_q.put(
            eqa_struct.message(
                eqa_settings.eqa_time(),
                "system",
                "group",
                "null",
                "false",
            )
        )
        system_q.put(
            eqa_struct.message(
                eqa_settings.eqa_time(),
                "system",
                "leader",
                "null",
                "false",
            )
        )
        system_q.put(
            eqa_struct.message(
                eqa_settings.eqa_time(),
                "system",
                "afk",
                "null",
                "false",
            )
        )

    except Exception as e:
        eqa_settings.log(
            "action motd welcome: Error on line "
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
                "null",
                "true",
            )
        )
        system_q.put(
            eqa_struct.message(
                eqa_settings.eqa_time(),
                "system",
                "leader",
                "null",
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
                "null",
                "false",
            )
        )
        system_q.put(
            eqa_struct.message(
                eqa_settings.eqa_time(),
                "system",
                "leader",
                "null",
                "false",
            )
        )

    except Exception as e:
        eqa_settings.log(
            "action group removed: Error on line "
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
                "null",
                "true",
            )
        )
        system_q.put(
            eqa_struct.message(
                eqa_settings.eqa_time(),
                "system",
                "leader",
                "null",
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
                "null",
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
                "null",
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
                "null",
                "false",
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
                "null",
                "true",
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
                "null",
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
            eqa_struct.message(eqa_settings.eqa_time(), "system", "loc", "null", loc)
        )

    except Exception as e:
        eqa_settings.log(
            "action location: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def action_you_say_commands(system_q, check_line, config, mute_list):
    """Perform actions for parser say commands"""

    try:
        if re.fullmatch(r"^You say, \'parser (un|)mute\'$", check_line) is not None:
            system_q.put(
                eqa_struct.message(
                    eqa_settings.eqa_time(),
                    "system",
                    "mute",
                    "toggle",
                    "all",
                )
            )
        elif (
            re.fullmatch(r"^You say, \'parser (un|)mute speak\'$", check_line)
            is not None
        ):
            system_q.put(
                eqa_struct.message(
                    eqa_settings.eqa_time(),
                    "system",
                    "mute",
                    "toggle",
                    "speak",
                )
            )
        elif (
            re.fullmatch(r"^You say, \'parser mute speak [a-zA-Z\s]+\'$", check_line)
            is not None
        ):
            mute_candidate = re.findall(
                r"(?<=You say, \'parser mute speak )\w+ \w+", check_line
            )
            mute_line, mute_player = mute_candidate[0].lower().split(" ")
            if (
                mute_line in config["line"]
                and config["line"][mute_line]["reaction"] == "speak"
                and (mute_line, mute_player) not in mute_list
            ):
                mute_list.append((mute_line, mute_player))
                display_q.put(
                    eqa_struct.display(
                        eqa_settings.eqa_time(),
                        "event",
                        "events",
                        mute_player.title() + " muted for line type " + mute_line,
                    )
                )
        elif (
            re.fullmatch(
                r"^You say, \'parser unmute speak [a-zA-Z\s]+\'$",
                check_line,
            )
            is not None
        ):
            mute_candidate = re.findall(
                r"(?<=You say, \'parser unmute speak )\w+ \w+", check_line
            )
            mute_line, mute_player = mute_candidate[0].lower().split(" ")
            if (mute_line, mute_player) in mute_list:
                mute_list.remove((mute_line, mute_player))
                display_q.put(
                    eqa_struct.display(
                        eqa_settings.eqa_time(),
                        "event",
                        "events",
                        mute_player.title() + " unmuted for line type " + mute_line,
                    )
                )
        elif (
            re.fullmatch(r"^You say, \'parser (un|)mute alert\'$", check_line)
            is not None
        ):
            system_q.put(
                eqa_struct.message(
                    eqa_settings.eqa_time(),
                    "system",
                    "mute",
                    "toggle",
                    "alert",
                )
            )
        elif (
            re.fullmatch(r"^You say, \'parser mute list clear\'$", check_line)
            is not None
        ):
            mute_list.clear()
            display_q.put(
                eqa_struct.display(
                    eqa_settings.eqa_time(),
                    "event",
                    "events",
                    "Muted list cleared",
                )
            )
        elif re.fullmatch(r"^You say, \'parser raid\'$", check_line) is not None:
            system_q.put(
                eqa_struct.message(
                    eqa_settings.eqa_time(),
                    "system",
                    "raid",
                    "toggle",
                    "null",
                )
            )
        elif re.fullmatch(r"^You say, \'parser debug\'$", check_line) is not None:
            system_q.put(
                eqa_struct.message(
                    eqa_settings.eqa_time(),
                    "system",
                    "debug",
                    "toggle",
                    "null",
                )
            )
        elif re.fullmatch(r"^You say, \'parser reload\'$", check_line) is not None:
            system_q.put(
                eqa_struct.message(
                    eqa_settings.eqa_time(),
                    "system",
                    "reload_config",
                    "null",
                    "null",
                )
            )

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
                "null",
                "false",
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
                "null",
                "true",
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
                "null",
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
                "null",
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


def action_who_player(system_q, state, line):
    """Perform actions for who_player line types"""

    try:
        if state.char.lower() in line.lower():
            if re.findall(r"\d+ [a-zA-Z\s]+", line) is not None:
                char_level, char_class = re.findall(r"\d+ [a-zA-Z\s]+", line)[0].split(
                    " ", 1
                )
                system_q.put(
                    eqa_struct.message(
                        eqa_settings.eqa_time(),
                        "system",
                        "level",
                        "null",
                        char_level,
                    )
                )
                system_q.put(
                    eqa_struct.message(
                        eqa_settings.eqa_time(),
                        "system",
                        "class",
                        "null",
                        char_class,
                    )
                )
            if re.fullmatch(r".+\<[a-zA-Z\s]+\>(.+|)", line) is not None:
                char_guild = re.findall(r"(?<=\<)[a-zA-Z\s]+", line)[0]
                system_q.put(
                    eqa_struct.message(
                        eqa_settings.eqa_time(),
                        "system",
                        "guild",
                        "null",
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
    base_path, system_q, display_q, sound_q, state, config, check_line
):
    """Perform actions for you new zone line types"""

    try:
        current_zone = re.findall("(?<=You have entered )[a-zA-Z\s]+", check_line)
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
                "null",
                current_zone[0],
            )
        )
        if current_zone[0] not in config["zones"].keys():
            eqa_config.add_zone(current_zone[0], base_path)
        elif current_zone[0] in config["zones"].keys() and not state.raid == "true":
            if config["zones"][current_zone[0]] == "raid":
                system_q.put(
                    eqa_struct.message(
                        eqa_settings.eqa_time(),
                        "system",
                        "raid",
                        "true",
                        "Raid mode auto-enabled",
                    )
                )
        elif current_zone[0] in config["zones"].keys() and state.raid == "true":
            if config["zones"][current_zone[0]] != "raid":
                system_q.put(
                    eqa_struct.message(
                        eqa_settings.eqa_time(),
                        "system",
                        "raid",
                        "false",
                        "Raid mode auto-disabled",
                    )
                )

    except Exception as e:
        eqa_settings.log(
            "action you new zone: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def action_matched(line_type, line, base_path):
    """Debug function to log all log lines and matches log lines"""

    try:

        matched_log = base_path + "log/debug/matched-lines.txt"
        if os.path.exists(matched_log):
            file_size = os.path.getsize(matched_log)
            if file_size > 5000000:
                version = str(
                    pkg_resources.get_distribution("eqalert").version
                ).replace(".", "-")
                archived_log = (
                    base_path
                    + "log/debug/matched-lines_"
                    + version
                    + "_"
                    + str(datetime.now().date())
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


def action_undetermined(line, base_path):
    """Debug function to log unmatched log lines"""

    try:

        undetermined_log = base_path + "log/debug/undetermined-lines.txt"
        if os.path.exists(undetermined_log):
            file_size = os.path.getsize(undetermined_log)
            if file_size > 5000000:
                version = str(
                    pkg_resources.get_distribution("eqalert").version
                ).replace(".", "-")
                archived_log = (
                    base_path
                    + "log/debug/undetermined-lines_"
                    + version
                    + "_"
                    + str(datetime.now().date())
                    + ".txt"
                )
                os.rename(undetermined_log, archived_log)
        undetermined_log_file = open(undetermined_log, "a")
        undetermined_log_file.write(line + "\n")
        undetermined_log_file.close()

    except Exception as e:
        eqa_settings.log(
            "action undetermined: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


if __name__ == "__main__":
    main()
