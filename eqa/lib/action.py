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

import eqa.lib.config as eqa_config
import eqa.lib.settings as eqa_settings
import eqa.lib.sound as eqa_sound
import eqa.lib.struct as eqa_struct


def process(
    config,
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
):
    """
    Process: action_q
    Produce: sound_q, display_q, system_q, encounter_q
    """

    try:
        while not exit_flag.is_set() and not cfg_reload.is_set():

            # Sleep between empty checks
            queue_size = action_q.qsize()
            if queue_size < 1:
                time.sleep(0.01)
            else:
                if state.debug == "true":
                    eqa_settings.log("action_q depth: " + str(queue_size))

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
                if state.debug == "true":
                    action_matched(line_type, check_line, base_path)
                    display_q.put(
                        eqa_struct.display(
                            eqa_settings.eqa_time(),
                            "event",
                            "debug",
                            (line_type, check_line),
                        )
                    )

                ## Encounter Parsing
                if state.encounter_parse == "true":
                    if line_type.startswith("combat_"):
                        encounter_q.put(
                            eqa_struct.message(
                                line_time,
                                line_type,
                                "combat",
                                "null",
                                check_line,
                            )
                        )
                    elif line_type.startswith("you_auto_attack_"):
                        encounter_q.put(
                            eqa_struct.message(
                                line_time,
                                line_type,
                                "combat",
                                "null",
                                check_line,
                            )
                        )
                    elif line_type.startswith("mob_slain_"):
                        encounter_q.put(
                            eqa_struct.message(
                                line_time,
                                line_type,
                                "stop",
                                "null",
                                check_line,
                            )
                        )
                    elif line_type == "spell_cast_other":
                        encounter_q.put(
                            eqa_struct.message(
                                line_time,
                                line_type,
                                "spell",
                                "null",
                                check_line,
                            )
                        )
                    elif line_type == "spell_cast_you":
                        encounter_q.put(
                            eqa_struct.message(
                                line_time,
                                line_type,
                                "spell",
                                "null",
                                check_line,
                            )
                        )
                    elif line_type == "you_new_zone":
                        encounter_q.put(
                            eqa_struct.message(
                                line_time,
                                line_type,
                                "stop",
                                "null",
                                check_line,
                            )
                        )
                    elif line_type.startswith("experience_"):
                        encounter_q.put(
                            eqa_struct.message(
                                line_time,
                                line_type,
                                "stop",
                                "null",
                                check_line,
                            )
                        )
                    elif line_type == "faction_line":
                        encounter_q.put(
                            eqa_struct.message(
                                line_time,
                                line_type,
                                "stop",
                                "null",
                                check_line,
                            )
                        )
                    elif line_type.startswith("spell_"):
                        encounter_q.put(
                            eqa_struct.message(
                                line_time,
                                line_type,
                                "spell",
                                "null",
                                check_line,
                            )
                        )
                ## Default Timers
                if state.auto_mob_timer == "true":
                    if (
                        line_type == "experience_solo"
                        or line_type == "experience_group"
                    ):
                        timer_seconds = config["zones"][str(state.zone).title()][
                            "timer"
                        ]
                        timer_q.put(
                            eqa_struct.timer(
                                (
                                    datetime.datetime.now()
                                    + datetime.timedelta(seconds=int(timer_seconds))
                                ),
                                "timer",
                                str(timer_seconds),
                                "Pop " + str(state.zone),
                            )
                        )

                ## State Building Line Types
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
                elif line_type == "group_disbanded":
                    action_group_disbanded(system_q)
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
                elif line_type == "say_you":
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
                            config,
                            mute_list,
                            state,
                        )
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

                ## If line_type exists in the config
                if line_type in config["line"].keys():

                    reaction = config["line"][line_type]["reaction"]

                    ### Handle Alert Reactions
                    if reaction == "alert":
                        reaction_alert(
                            line_type,
                            check_line,
                            config,
                            sound_q,
                            display_q,
                            state,
                            mute_list,
                        )

                    ### Handle Context Reactions
                    elif reaction != "false":
                        reaction_context(
                            line_type,
                            check_line,
                            config,
                            sound_q,
                            display_q,
                            state,
                            mute_list,
                            reaction,
                        )

                    ### Handle alert reactions for all lines
                    if config["line"]["all"]["reaction"] == "alert":
                        reaction_alert(
                            "all",
                            check_line,
                            config,
                            sound_q,
                            display_q,
                            state,
                            mute_list,
                        )

                    ### Handle context reaction for all lines
                    elif config["line"]["all"]["reaction"] != "false":
                        reaction_context(
                            "all",
                            check_line,
                            config,
                            sound_q,
                            display_q,
                            state,
                            mute_list,
                            config["line"]["all"]["reaction"],
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
                            "null",
                            "null",
                        )
                    )

                action_q.task_done()

    except Exception as e:
        eqa_settings.log(
            "process action: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )

    sys.exit(0)


def send_alerts(line_type, check_line, config, sound_q, display_q, mute_list):
    """Send messages to sound and display queues"""

    try:
        # Check Sender
        sender = re.findall(r"^([\w\-]+)", check_line)

        if config["line"][line_type]["sound"] == "true":
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

        elif config["line"][line_type]["sound"] != "false":
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
    line_type, check_line, config, sound_q, display_q, keyphrase, context, mute_list
):
    """Send keyphrase messages to sound and display queues"""

    try:
        # Check Sender
        sender = re.findall(r"^([\w\-]+)", check_line)

        if config["line"][line_type]["sound"] == "true":
            if keyphrase == "assist" or keyphrase == "rampage" or keyphrase == "spot":
                payload = keyphrase + " on " + sender[0]
            else:
                payload = keyphrase
            if (
                not (line_type, sender[0].lower()) in mute_list
                and not (line_type, "all") in mute_list
            ):
                if context == "true":
                    sound_q.put(eqa_struct.sound("speak", check_line))
                elif context != "false":
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

        elif config["line"][line_type]["sound"] != "false":
            if keyphrase == "assist" or keyphrase == "rampage" or keyphrase == "spot":
                payload = keyphrase + " on " + sender[0]
            else:
                payload = keyphrase
            if (
                not (line_type, sender[0].lower()) in mute_list
                and not (line_type, "all") in mute_list
            ):
                if context == "true":
                    sound_q.put(eqa_struct.sound("alert", line_type))
                elif context != "false":
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
    line_type, check_line, config, sound_q, display_q, state, mute_list, reaction
):
    """Reactions for when reaction is a context"""

    try:
        # Or if line_type reaction is all
        if reaction == "all":
            send_alerts(
                line_type,
                check_line,
                config,
                sound_q,
                display_q,
                mute_list,
            )

        # Or if line_type reaction is solo_only and you are solo and not in a raid
        elif (
            reaction == "solo_only" and state.group == "false" and state.raid == "false"
        ):
            send_alerts(
                line_type,
                check_line,
                config,
                sound_q,
                display_q,
                mute_list,
            )

        # Or if line_type reaction is solo and you are solo and not in a raid
        elif reaction == "solo" and state.group == "false" and state.raid == "false":
            send_alerts(
                line_type,
                check_line,
                config,
                sound_q,
                display_q,
                mute_list,
            )

        # Or if line_type reaction is solo and you are grouped but not in a raid
        elif reaction == "solo" and state.group == "true" and state.raid == "false":
            send_alerts(
                line_type,
                check_line,
                config,
                sound_q,
                display_q,
                mute_list,
            )

        # Or if line_type reaction is solo_group_only and you are not in a raid
        elif reaction == "solo_group_only" and state.raid == "false":
            send_alerts(
                line_type,
                check_line,
                config,
                sound_q,
                display_q,
                mute_list,
            )

        # Or if line_type reaction group_only and you are grouped but not in a raid
        elif (
            reaction == "group_only" and state.group == "true" and state.raid == "false"
        ):
            send_alerts(
                line_type,
                check_line,
                config,
                sound_q,
                display_q,
                mute_list,
            )

        # Or if line_type reaction is group and you are grouped but not in a raid
        elif reaction == "group" and state.group == "true" and state.raid == "false":
            send_alerts(
                line_type,
                check_line,
                config,
                sound_q,
                display_q,
                mute_list,
            )

        # Or if line_type reaction is solo regardless of group state and in a raid
        elif reaction == "solo" and state.raid == "true":
            send_alerts(
                line_type,
                check_line,
                config,
                sound_q,
                display_q,
                mute_list,
            )

        # Or if line_type reaction is group regardless of group state and in a raid
        elif reaction == "group" and state.raid == "true":
            send_alerts(
                line_type,
                check_line,
                config,
                sound_q,
                display_q,
                mute_list,
            )

        # Or if line_type reaction is raid regardless of group state and in a raid
        elif reaction == "raid" and state.raid == "true":
            send_alerts(
                line_type,
                check_line,
                config,
                sound_q,
                display_q,
                mute_list,
            )

        # Or if line_type reaction is afk and you are afk
        elif reaction == "afk" and state.afk == "true":
            send_alerts(
                line_type,
                check_line,
                config,
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


def reaction_alert(line_type, check_line, config, sound_q, display_q, state, mute_list):
    """Reactions for when reaction is alert"""

    try:
        for keyphrase, value in config["line"][line_type]["alert"].items():
            # If the alert value is true
            if str(keyphrase).lower() in check_line.lower():
                if value == "true":
                    send_keyphrase_alerts(
                        line_type,
                        check_line,
                        config,
                        sound_q,
                        display_q,
                        keyphrase,
                        value,
                        mute_list,
                    )
                # If the alert value is solo_only
                elif (
                    value == "solo_only"
                    and state.group == "false"
                    and state.raid == "false"
                ):
                    send_keyphrase_alerts(
                        line_type,
                        check_line,
                        config,
                        sound_q,
                        display_q,
                        keyphrase,
                        value,
                        mute_list,
                    )
                # If the alert value is solo
                elif (
                    value == "solo" and state.group == "false" and state.raid == "false"
                ):
                    send_keyphrase_alerts(
                        line_type,
                        check_line,
                        config,
                        sound_q,
                        display_q,
                        keyphrase,
                        value,
                        mute_list,
                    )
                # If the alert value is group
                elif (
                    value == "group" and state.group == "true" and state.raid == "false"
                ):
                    send_keyphrase_alerts(
                        line_type,
                        check_line,
                        config,
                        sound_q,
                        display_q,
                        keyphrase,
                        value,
                        mute_list,
                    )
                # If the alert value is group_only
                elif (
                    value == "group_only"
                    and state.group == "true"
                    and state.raid == "false"
                ):
                    send_keyphrase_alerts(
                        line_type,
                        check_line,
                        config,
                        sound_q,
                        display_q,
                        keyphrase,
                        value,
                        mute_list,
                    )
                # If the alert value is solo, but you are grouped
                elif (
                    value == "solo" and state.group == "true" and state.raid == "false"
                ):
                    send_keyphrase_alerts(
                        line_type,
                        check_line,
                        config,
                        sound_q,
                        display_q,
                        keyphrase,
                        value,
                        mute_list,
                    )
                # If the alert value is solo_group_only
                elif value == "solo_group_only" and state.raid == "false":
                    send_keyphrase_alerts(
                        line_type,
                        check_line,
                        config,
                        sound_q,
                        display_q,
                        keyphrase,
                        value,
                        mute_list,
                    )
                # If the alert value is raid
                elif value == "raid" and state.raid == "true":
                    send_keyphrase_alerts(
                        line_type,
                        check_line,
                        config,
                        sound_q,
                        display_q,
                        keyphrase,
                        value,
                        mute_list,
                    )
                # If the alert value is group, but you are in a raid
                elif value == "group" and state.raid == "true":
                    send_keyphrase_alerts(
                        line_type,
                        check_line,
                        config,
                        sound_q,
                        display_q,
                        keyphrase,
                        value,
                        mute_list,
                    )
                # If the alert value is solo, but you are in a raid
                elif value == "solo" and state.raid == "true":
                    send_keyphrase_alerts(
                        line_type,
                        check_line,
                        config,
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


def action_group_disbanded(system_q):
    """Perform actions for group disbanded line types"""

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


def action_you_say_commands(
    timer_q, system_q, sound_q, display_q, check_line, config, mute_list, state
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
                elif args[1] in config["line"]:
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
                elif args[1] in config["line"]:
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
                        "null",
                    )
                )
            elif args[0] == "debug":
                system_q.put(
                    eqa_struct.message(
                        eqa_settings.eqa_time(),
                        "system",
                        "debug",
                        "toggle",
                        "null",
                    )
                )
            elif args[0] == "reload":
                system_q.put(
                    eqa_struct.message(
                        eqa_settings.eqa_time(),
                        "system",
                        "reload_config",
                        "null",
                        "null",
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
                            "null",
                        )
                    )
                elif args[1] == "clear":
                    system_q.put(
                        eqa_struct.message(
                            eqa_settings.eqa_time(),
                            "system",
                            "encounter",
                            "clear",
                            "null",
                        )
                    )
                elif args[1] == "end":
                    system_q.put(
                        eqa_struct.message(
                            eqa_settings.eqa_time(),
                            "system",
                            "encounter",
                            "end",
                            "null",
                        )
                    )
                elif args[1] == "start":
                    system_q.put(
                        eqa_struct.message(
                            eqa_settings.eqa_time(),
                            "system",
                            "encounter",
                            "start",
                            "null",
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
                            + state.char_level
                            + " "
                            + state.char_class
                            + " of "
                            + state.char_guild
                            + ". Bound in "
                            + state.bind
                            + " and currently in "
                            + state.zone
                            + " facing "
                            + state.direction
                            + " around "
                            + str(state.loc)
                            + ". Group state is "
                            + state.group
                            + ". Leader state is "
                            + state.leader
                            + ". Raid state is "
                            + state.raid
                            + ". AFK state is "
                            + state.afk
                            + ". Encumbered state is "
                            + state.encumbered
                            + ". Debug state is "
                            + state.debug
                            + ". Encounter parser state is "
                            + state.encounter_parse,
                        )
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
                            + state.zone
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
            elif args[0] == "why":
                if len(args) == 1:
                    sound_q.put(
                        eqa_struct.sound(
                            "speak",
                            "Did you choose the "
                            + state.char_class
                            + " life, or did the "
                            + state.char_class
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
                                "true",
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
                                "false",
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
        current_zone = re.findall("(?<=You have entered )[a-zA-Z\-'\s]+", check_line)
        system_q.put(
            eqa_struct.message(
                eqa_settings.eqa_time(),
                "system",
                "afk",
                "null",
                "false",
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
                    "null",
                    current_zone[0],
                )
            )

        if current_zone[0] not in config["zones"].keys():
            eqa_config.add_zone(current_zone[0], base_path)
        elif current_zone[0] in config["zones"].keys() and not state.raid == "true":
            if (
                config["zones"][current_zone[0]]["raid_mode"] == "true"
                and config["settings"]["raid_mode"]["auto_set"] == "true"
            ):
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
            if (
                config["zones"][current_zone[0]]["raid_mode"] == "false"
                and config["settings"]["raid_mode"]["auto_set"] == "true"
            ):
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
