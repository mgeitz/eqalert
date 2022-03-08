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

import eqa.lib.config as eqa_config
import eqa.lib.settings as eqa_settings
import eqa.lib.sound as eqa_sound
import eqa.lib.struct as eqa_struct


def process(
    action_q,
    system_q,
    display_q,
    sound_q,
    heal_q,
    damage_q,
    exit_flag,
    heal_parse,
    spell_parse,
    raid,
    cfg_reload,
    config,
    base_path,
):
    """
    Process: action_q
    Produce: sound_q, display_q, system_q, heal_q, damage_q
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

                # Line specific checks
                if line_type == "undetermined":
                    undetermined_line(check_line, base_path)
                elif line_type == "location":
                    y, x, z = re.findall("[-]?(?:\d*\.)?\d+", check_line)
                    loc = [y, x, z]
                    system_q.put(
                        eqa_struct.message(
                            eqa_settings.eqa_time(), "system", "loc", "null", loc
                        )
                    )
                elif line_type == "direction":
                    direction = re.findall('(?:North(?:East|West)?|South(?:East|West)?|(?:Ea|We)st)', check_line)
                    system_q.put(
                        eqa_struct.message(
                            eqa_settings.eqa_time(),
                            "system",
                            "direction",
                            "null",
                            direction[0],
                        )
                    )
                elif line_type.startswith("you_afk"):
                    if line_type == "you_afk_on":
                        display_q.put(
                            eqa_struct.display(
                                eqa_settings.eqa_time(),
                                "event",
                                "events",
                                "You are now AFK",
                            )
                        )
                        system_q.put(
                            eqa_struct.message(
                                eqa_settings.eqa_time(), "system", "afk", "null", "true"
                            )
                        )
                    elif line_type == "you_afk_off":
                        display_q.put(
                            eqa_struct.display(
                                eqa_settings.eqa_time(),
                                "event",
                                "events",
                                "You are no longer AFK",
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
                elif line_type == "you_new_zone":
                    nz_iter = 0
                    current_zone = ""
                    # what the fuck
                    current_zone = re.findall('(?<=You have entered)[a-zA-Z\s]+', line)
                    sound_q.put(eqa_struct.sound("speak", current_zone[0]))
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
                    if current_zone not in config["zones"].keys():
                        eqa_config.add_zone(current_zone, base_path)
                    elif current_zone in config["zones"].keys() and not raid.is_set():
                        if config["zones"][current_zone] == "raid":
                            raid.set()
                            display_q.put(
                                eqa_struct.display(
                                    eqa_settings.eqa_time(),
                                    "event",
                                    "events",
                                    "Raid mode auto-enabled",
                                )
                            )
                            sound_q.put(eqa_struct.sound("speak", "Raid mode enabled"))
                    elif current_zone in config["zones"].keys() and raid.is_set():
                        if config["zones"][current_zone] != "raid":
                            raid.clear()
                            display_q.put(
                                eqa_struct.display(
                                    eqa_settings.eqa_time(),
                                    "event",
                                    "events",
                                    "Raid mode auto-disabled",
                                )
                            )
                            sound_q.put(eqa_struct.sound("speak", "Raid mode disabled"))

                # If line_type is a parsable type
                if line_type in config["line"].keys():
                    # If line_type is parsed for as true
                    if config["line"][line_type]["reaction"] == "true":
                        for keyphrase, value in config["line"][line_type][
                            "alert"
                        ].items():
                            if str(keyphrase).lower() in check_line.lower() and value == "true":
                                sound_q.put(eqa_struct.sound("alert", line_type))
                                display_q.put(
                                    eqa_struct.display(
                                        eqa_settings.eqa_time(),
                                        "event",
                                        "events",
                                        line_type + ": " + check_line,
                                    )
                                )
                            elif (
                                str(keyphrase).lower() in check_line.lower()
                                and value == "raid"
                                and raid.is_set()
                            ):
                                if keyphrase == "assist" or keyphrase == "rampage":
                                    target = re.findall('^([\w\-]+)', line)
                                    payload = keyphrase + " on " + target[0]
                                else:
                                    payload = keyphrase
                                sound_q.put(eqa_struct.sound("speak", payload))
                                display_q.put(
                                    eqa_struct.display(
                                        eqa_settings.eqa_time(),
                                        "event",
                                        "events",
                                        line_type + ": " + check_line,
                                    )
                                )

                    # Or if line_type is parsed for as all
                    elif config["line"][line_type]["reaction"] == "all":
                        # Heal parse
                        if heal_parse.is_set() and line_type == "you_healed":
                            pass

                        # Spell damage parse
                        elif spell_parse.is_set() and line_type == "spell_damage":
                            pass

                        # DoT damage parse
                        elif spell_parse.is_set() and line_type == "dot_damage":
                            pass

                        # Notify on all other all alerts
                        else:
                            sound_q.put(eqa_struct.sound("alert", line_type))
                            display_q.put(
                                eqa_struct.display(
                                    eqa_settings.eqa_time(),
                                    "event",
                                    "events",
                                    line_type + ": " + check_line,
                                )
                            )

                    # Or if line_type is parsed for as a spoken alert
                    elif config["line"][line_type]["reaction"] == "speak":
                        display_q.put(
                            eqa_struct.display(
                                eqa_settings.eqa_time(), "event", "events", check_line
                            )
                        )
                        sound_q.put(eqa_struct.sound("speak", check_line))

                    # For triggers requiring all line_types
                    if config["line"]["all"]["reaction"] == "true":
                        for keyphrase, value in config["alert"]["all"].items():
                            if keyphrase in check_line.lower():
                                sound_q.put(eqa_struct.sound("alert", line_type))
                                display_q.put(
                                    eqa_struct.display(
                                        eqa_settings.eqa_time(),
                                        "event",
                                        "events",
                                        line_type + ": " + check_line,
                                    )
                                )

                # If line_type is not a parsable type
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


def undetermined_line(line, base_path):
    """Temp function to log undetermined log lines"""
    f = open(base_path + "log/undetermined.txt", "a")
    f.write(line + "\n")
    f.close()


if __name__ == "__main__":
    main()
