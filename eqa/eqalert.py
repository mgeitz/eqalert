#! /usr/bin/env python

"""
   Program:   EQ Alert
   File Name: eqa/eqalert.py
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

import logging
import os
import pkg_resources
import sys
import threading
import time
import queue
import shutil

import eqa.lib.action as eqa_action
import eqa.lib.config as eqa_config
import eqa.lib.curses as eqa_curses
import eqa.lib.encounter as eqa_encounter
import eqa.lib.keys as eqa_keys
import eqa.lib.log as eqa_log
import eqa.lib.parser as eqa_parser
import eqa.lib.settings as eqa_settings
import eqa.lib.sound as eqa_sound
import eqa.lib.state as eqa_state
import eqa.lib.struct as eqa_struct
import eqa.lib.timer as eqa_timer


def startup(base_path):
    """Start things up"""

    try:

        # Make the main folder
        if not os.path.exists(base_path):
            print("Bootstrapping for first run . . .")
            print("    - putting this stuff in " + base_path)
            os.makedirs(base_path)

        # Generating a config file
        if not os.path.exists(base_path + "config.json"):
            print("    - generating json config")
            eqa_config.init(base_path)

        # Read config paths
        config = eqa_config.read_config(base_path)
        log_path = config["settings"]["paths"]["alert_log"]
        data_path = config["settings"]["paths"]["data"]
        encounter_path = config["settings"]["paths"]["encounter"]
        sound_path = config["settings"]["paths"]["sound"]
        tmp_sound_path = config["settings"]["paths"]["tmp_sound"]
        char_log_path = config["settings"]["paths"]["char_log"]

        # Validate char_log directory path
        if not os.path.exists(char_log_path):
            print(
                "There was an issue building initial configuration, please check settings > paths > char_log in config.json"
            )
            exit(1)

        # Make the log directory
        if not os.path.exists(log_path):
            print("    - making a place for logs")
            os.makedirs(log_path)

        # Set log file
        logging.basicConfig(filename=log_path + "eqalert.log", level=logging.INFO)

        # Make the debug directory
        if not os.path.exists(log_path + "debug/"):
            print("    - making a place for optional debug logs")
            os.makedirs(log_path + "debug/")

        # Make the encounter directory
        if not os.path.exists(encounter_path):
            print("    - making a place for encounter logs")
            os.makedirs(encounter_path)

        # Make the sound directory
        if not os.path.exists(sound_path):
            print("    - making a home for alert sounds")
            os.makedirs(sound_path)
        if not os.path.exists(sound_path + "tock.wav"):
            tock_path = pkg_resources.resource_filename("eqa", "sound/tock.wav")
            shutil.move(tock_path, sound_path + "tock.wav")
        if not os.path.exists(sound_path + "tick.wav"):
            tick_path = pkg_resources.resource_filename("eqa", "sound/tick.wav")
            shutil.move(tick_path, sound_path + "tick.wav")

        # Make the tmp sound directory
        if not os.path.exists(tmp_sound_path):
            os.makedirs(tmp_sound_path)

        # Make the data directory
        if not os.path.exists(data_path):
            print("    - making a place for data")
            os.makedirs(data_path)

        # Update config char_logs
        eqa_config.update_logs(base_path)

        config = eqa_config.read_config(base_path)
        server = config["last_state"]["server"]
        char = config["last_state"]["character"]
        char_log = (
            config["settings"]["paths"]["char_log"]
            + config["char_logs"][char + "_" + server]["file_name"]
        )

        # Validate last state char log
        if not os.path.exists(char_log):
            print(
                "Please review `settings > paths` in config.json, a log with that default server and character cannot be found."
            )
            exit(1)

        # Validate config version
        if "version" not in config["settings"]:
            print(
                "Please move or delete your current configuration. A new config.json file must be generated."
            )
            exit(1)
        elif not config["settings"]["version"] == str(
            pkg_resources.get_distribution("eqalert").version
        ):
            old_version = str(config["settings"]["version"]).replace(".", "-")
            archive_config = base_path + "config_" + old_version + ".json"
            print("Your config.json was generated by a older version of eqalert.")
            print("Archiving old config to " + archive_config)
            os.rename(base_path + "config.json", archive_config)
            print("Generating new config.json")
            eqa_config.init(base_path)
            print("Please validate your new config.json and relaunch eqalert.")
            exit(1)

    except Exception as e:
        print(
            "Unfortunately, the startup step failed with: "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
            + "# Sometimes this is solved by allowing config regeneration"
        )
        exit(1)


def main():
    """Main method, does the good stuff"""

    # Paths
    home = os.path.expanduser("~")
    base_path = home + "/.eqa/"

    # Validate start
    startup(base_path)

    # Read in config and state
    config = eqa_config.read_config(base_path)
    server = config["last_state"]["server"]
    char = config["last_state"]["character"]
    state = eqa_config.get_last_state(base_path, char, server)
    char_log = (
        config["settings"]["paths"]["char_log"]
        + config["char_logs"][char + "_" + server]["file_name"]
    )

    # Thread Events
    cfg_reload = threading.Event()
    log_reload = threading.Event()
    exit_flag = threading.Event()

    # Queues
    keyboard_q = queue.Queue()
    action_q = queue.Queue()
    display_q = queue.Queue()
    sound_q = queue.Queue()
    system_q = queue.Queue()
    log_q = queue.Queue()
    encounter_q = queue.Queue()
    timer_q = queue.Queue()

    # Initialize curses
    screen = eqa_curses.init(state)

    # Read Log File
    ## Consume char_log
    ## Produce log_q
    process_log = threading.Thread(
        target=eqa_log.process,
        args=(log_reload, exit_flag, char_log, log_q),
    )
    process_log.daemon = True
    process_log.start()

    # Parse Log Lines to Determine Line Type
    ## Process log_q
    ## Produce action_q

    ### Thread 1
    process_parse = threading.Thread(
        target=eqa_parser.process, args=(exit_flag, log_q, action_q)
    )
    process_parse.daemon = True
    process_parse.start()

    # Read Keyboard Events
    ## Consume keyboard events
    ## Produce keyboard_q
    read_keys = threading.Thread(
        target=eqa_keys.read, args=(exit_flag, keyboard_q, screen)
    )
    read_keys.daemon = True
    read_keys.start()

    # Act on Keyboard Events
    ## Process keyboard_q
    ## Produce display_q, sound_q, system_q
    process_keys = threading.Thread(
        target=eqa_keys.process,
        args=(
            state,
            config,
            display_q,
            keyboard_q,
            system_q,
            cfg_reload,
            exit_flag,
        ),
    )
    process_keys.daemon = True
    process_keys.start()

    # Act on Parsed Log Lines
    ## Consume action_q
    ## Produce display_q, sound_q, system_q

    ### Mute List
    mute_list = []

    ### Thread 1
    process_action = threading.Thread(
        target=eqa_action.process,
        args=(
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
        ),
    )
    process_action.daemon = True
    process_action.start()

    # Produce display_q, system_q
    ## Consume encounter_q

    process_encounter = threading.Thread(
        target=eqa_encounter.process,
        args=(
            config,
            base_path,
            encounter_q,
            system_q,
            display_q,
            exit_flag,
            cfg_reload,
            state,
        ),
    )
    process_encounter.daemon = True
    process_encounter.start()

    # Produce Sound
    ## Consume sound_q

    ### Thread 1
    process_sound_1 = threading.Thread(
        target=eqa_sound.process, args=(config, sound_q, exit_flag, cfg_reload, state)
    )
    process_sound_1.daemon = True
    process_sound_1.start()

    ### Thread 2
    process_sound_2 = threading.Thread(
        target=eqa_sound.process, args=(config, sound_q, exit_flag, cfg_reload, state)
    )
    process_sound_2.daemon = True
    process_sound_2.start()

    ### Thread 3
    process_sound_3 = threading.Thread(
        target=eqa_sound.process, args=(config, sound_q, exit_flag, cfg_reload, state)
    )
    process_sound_3.daemon = True
    process_sound_3.start()

    # Do something to the TUI
    ## Consume display_q
    process_display = threading.Thread(
        target=eqa_curses.display,
        args=(screen, display_q, state, config, exit_flag, cfg_reload),
    )
    process_display.daemon = True
    process_display.start()

    # Produce sound_q, display_q
    ## Consume timer_q

    process_timer = threading.Thread(
        target=eqa_timer.process, args=(timer_q, sound_q, display_q, exit_flag)
    )
    process_timer.daemon = True
    process_timer.start()

    # Signal Startup Complete
    display_q.put(eqa_struct.display(eqa_settings.eqa_time(), "draw", "events", "null"))
    display_q.put(
        eqa_struct.display(eqa_settings.eqa_time(), "event", "events", "Initialized")
    )
    sound_q.put(eqa_struct.sound("speak", "initialized"))

    # Manage State and Config
    ## Consume system_q
    try:
        while not exit_flag.is_set():

            # Sleep between empty checks
            queue_size = system_q.qsize()
            if queue_size < 1:
                time.sleep(0.01)
            else:
                if state.debug == "true":
                    eqa_settings.log("system_q depth: " + str(queue_size))

            # Check queue for message
            if not system_q.empty():
                ## Read new message
                new_message = system_q.get()

                ## If system message
                if new_message.type == "system":
                    ### Update zone
                    if new_message.tx == "zone":
                        state.set_zone(new_message.payload)
                        state.set_direction("unavailable")
                        state.set_loc([0.00, 0.00, 0.00])
                        eqa_config.set_last_state(state, base_path)
                        display_q.put(
                            eqa_struct.display(
                                eqa_settings.eqa_time(), "draw", "redraw", "null"
                            )
                        )
                    ### Update location
                    elif new_message.tx == "loc":
                        state.set_loc(new_message.payload)
                        eqa_config.set_last_state(state, base_path)
                        display_q.put(
                            eqa_struct.display(
                                eqa_settings.eqa_time(), "draw", "redraw", "null"
                            )
                        )
                    ### Update direction
                    elif new_message.tx == "direction":
                        state.set_direction(new_message.payload)
                        eqa_config.set_last_state(state, base_path)
                        display_q.put(
                            eqa_struct.display(
                                eqa_settings.eqa_time(), "draw", "redraw", "null"
                            )
                        )
                    ### Update afk status
                    elif new_message.tx == "afk":
                        system_afk(base_path, state, display_q, new_message)
                    ### Update raid status
                    elif new_message.tx == "raid":
                        system_raid(base_path, state, display_q, sound_q, new_message)
                    ### Update debug status
                    elif new_message.tx == "debug":
                        system_debug(base_path, state, display_q, sound_q, new_message)
                    ### Update encounter parse status
                    elif new_message.tx == "encounter":
                        system_encounter(
                            base_path,
                            state,
                            display_q,
                            sound_q,
                            encounter_q,
                            new_message,
                        )
                    ### Update group status
                    elif new_message.tx == "group":
                        state.set_group(new_message.payload)
                        eqa_config.set_last_state(state, base_path)
                        display_q.put(
                            eqa_struct.display(
                                eqa_settings.eqa_time(), "draw", "redraw", "null"
                            )
                        )
                    ### Update group leader status
                    elif new_message.tx == "leader":
                        state.set_leader(new_message.payload)
                        eqa_config.set_last_state(state, base_path)
                        display_q.put(
                            eqa_struct.display(
                                eqa_settings.eqa_time(), "draw", "redraw", "null"
                            )
                        )
                    ### Update encumbered status
                    elif new_message.tx == "encumbered":
                        state.set_encumbered(new_message.payload)
                        eqa_config.set_last_state(state, base_path)
                        display_q.put(
                            eqa_struct.display(
                                eqa_settings.eqa_time(), "draw", "redraw", "null"
                            )
                        )
                    ### Update automatic timer status
                    elif new_message.tx == "timer":
                        system_timer(state, base_path, display_q, sound_q, new_message)
                    ### Update bind status
                    elif new_message.tx == "bind":
                        state.set_bind(new_message.payload)
                        eqa_config.set_last_state(state, base_path)
                        display_q.put(
                            eqa_struct.display(
                                eqa_settings.eqa_time(), "draw", "redraw", "null"
                            )
                        )
                    ### Update level status
                    elif new_message.tx == "level":
                        state.set_level(new_message.payload)
                        eqa_config.set_last_state(state, base_path)
                        display_q.put(
                            eqa_struct.display(
                                eqa_settings.eqa_time(), "draw", "redraw", "null"
                            )
                        )
                    ### Update class status
                    elif new_message.tx == "class":
                        state.set_class(new_message.payload)
                        eqa_config.set_last_state(state, base_path)
                        display_q.put(
                            eqa_struct.display(
                                eqa_settings.eqa_time(), "draw", "redraw", "null"
                            )
                        )
                    ### Update guild status
                    elif new_message.tx == "guild":
                        state.set_guild(new_message.payload)
                        eqa_config.set_last_state(state, base_path)
                        display_q.put(
                            eqa_struct.display(
                                eqa_settings.eqa_time(), "draw", "redraw", "null"
                            )
                        )
                    ### Update mute status
                    elif new_message.tx == "mute":
                        system_mute(base_path, state, display_q, sound_q, new_message)
                    ### Update character
                    elif new_message.tx == "new_character":
                        new_char_log = (
                            config["settings"]["paths"]["char_log"]
                            + config["char_logs"][new_message.payload]["file_name"]
                        )
                        #### Ensure char/server combo exists as file
                        if os.path.exists(new_char_log):
                            # Record old char state before swapping
                            eqa_config.set_last_state(state, base_path)
                            # Stop watch on current log
                            log_reload.set()
                            process_log.join()
                            log_reload.clear()
                            # Set new character
                            char_name, char_server = new_message.payload.split("_")
                            new_state = eqa_config.get_last_state(
                                base_path, char_name, char_server
                            )
                            state.set_char(char_name)
                            state.set_server(char_server)
                            state.set_chars(new_state.chars)
                            state.set_zone(new_state.zone)
                            state.set_loc(new_state.loc)
                            state.set_direction(new_state.direction)
                            state.set_afk(new_state.afk)
                            state.set_raid(new_state.raid)
                            state.set_group(new_state.group)
                            state.set_leader(new_state.leader)
                            state.set_encumbered(new_state.encumbered)
                            state.set_bind(new_state.bind)
                            state.set_level(new_state.char_level)
                            state.set_class(new_state.char_class)
                            state.set_guild(new_state.char_guild)
                            eqa_config.set_last_state(state, base_path)
                            char_log = new_char_log
                            # Start new log watch
                            process_log = threading.Thread(
                                target=eqa_log.process,
                                args=(log_reload, exit_flag, char_log, log_q),
                            )
                            process_log.daemon = True
                            process_log.start()
                            display_q.put(
                                eqa_struct.display(
                                    eqa_settings.eqa_time(),
                                    "event",
                                    "events",
                                    "Character changed to "
                                    + state.char
                                    + " on "
                                    + state.server,
                                )
                            )
                            sound_q.put(
                                eqa_struct.sound(
                                    "speak",
                                    "Character changed to "
                                    + state.char
                                    + " on "
                                    + state.server,
                                )
                            )
                            display_q.put(
                                eqa_struct.display(
                                    eqa_settings.eqa_time(), "draw", "redraw", "null"
                                )
                            )
                        else:
                            display_q.put(
                                eqa_struct.display(
                                    eqa_settings.eqa_time(),
                                    "event",
                                    "events",
                                    "Unable to change characters, please review logs",
                                )
                            )
                            eqa_settings.log("Could not find file: " + new_char_log)
                    ### Reload config
                    elif new_message.tx == "reload_config":
                        #### Reload config
                        eqa_config.update_logs(base_path)
                        config = eqa_config.read_config(base_path)
                        #### Reread characters
                        new_state = eqa_config.get_last_state(
                            base_path, state.char, state.server
                        )
                        state.set_char(state.char)
                        state.set_server(state.server)
                        state.set_chars(eqa_config.get_config_chars(config))
                        state.set_zone(new_state.zone)
                        state.set_loc(new_state.loc)
                        state.set_direction(new_state.direction)
                        state.set_afk(new_state.afk)
                        state.set_raid(new_state.raid)
                        state.set_group(new_state.group)
                        state.set_leader(new_state.leader)
                        state.set_encumbered(new_state.encumbered)
                        state.set_bind(new_state.bind)
                        state.set_level(new_state.char_level)
                        state.set_class(new_state.char_class)
                        state.set_guild(new_state.char_guild)
                        #### Stop state dependent processes
                        cfg_reload.set()
                        process_action.join()
                        process_encounter.join()
                        process_sound_1.join()
                        process_sound_2.join()
                        process_sound_3.join()
                        process_keys.join()
                        process_display.join()
                        cfg_reload.clear()

                        # Restart the TUI
                        ## Consume display_q
                        process_display = threading.Thread(
                            target=eqa_curses.display,
                            args=(
                                screen,
                                display_q,
                                state,
                                config,
                                exit_flag,
                                cfg_reload,
                            ),
                        )
                        process_display.daemon = True
                        process_display.start()

                        #### Restart process_keys
                        process_keys = threading.Thread(
                            target=eqa_keys.process,
                            args=(
                                state,
                                config,
                                display_q,
                                keyboard_q,
                                system_q,
                                cfg_reload,
                                exit_flag,
                            ),
                        )
                        process_keys.daemon = True
                        process_keys.start()

                        #### Restart process_action

                        ##### Thread 1
                        process_action = threading.Thread(
                            target=eqa_action.process,
                            args=(
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
                            ),
                        )
                        process_action.daemon = True
                        process_action.start()

                        #### Restart process_encounter
                        process_encounter = threading.Thread(
                            target=eqa_encounter.process,
                            args=(
                                config,
                                base_path,
                                encounter_q,
                                system_q,
                                display_q,
                                exit_flag,
                                cfg_reload,
                                state,
                            ),
                        )
                        process_encounter.daemon = True
                        process_encounter.start()

                        #### Restart process_sound

                        ##### Thread 1
                        process_sound_1 = threading.Thread(
                            target=eqa_sound.process,
                            args=(config, sound_q, exit_flag, cfg_reload, state),
                        )
                        process_sound_1.daemon = True
                        process_sound_1.start()

                        ##### Thread 2
                        process_sound_2 = threading.Thread(
                            target=eqa_sound.process,
                            args=(config, sound_q, exit_flag, cfg_reload, state),
                        )
                        process_sound_2.daemon = True
                        process_sound_2.start()

                        ##### Thread 3
                        process_sound_3 = threading.Thread(
                            target=eqa_sound.process,
                            args=(config, sound_q, exit_flag, cfg_reload, state),
                        )
                        process_sound_3.daemon = True
                        process_sound_3.start()

                        #### Notify successful configuration reload
                        display_q.put(
                            eqa_struct.display(
                                eqa_settings.eqa_time(),
                                "event",
                                "events",
                                "Configuration reloaded",
                            )
                        )
                        sound_q.put(eqa_struct.sound("speak", "Configuration reloaded"))
                else:
                    display_q.put(
                        eqa_struct.display(
                            eqa_settings.eqa_time(),
                            "event",
                            "events",
                            new_message.type + ": " + new_message.payload,
                        )
                    )

                system_q.task_done()

    except Exception as e:
        eqa_settings.log(
            "main: Error on line " + str(sys.exc_info()[-1].tb_lineno) + ": " + str(e)
        )
        pass

    # Exit
    display_q.put(
        eqa_struct.display(eqa_settings.eqa_time(), "event", "events", "Exiting")
    )
    read_keys.join()
    process_log.join()
    process_parse.join()
    process_keys.join()
    process_action.join()
    process_encounter.join()
    process_timer.join()
    process_sound_1.join()
    process_sound_2.join()
    process_sound_3.join()
    process_display.join()
    eqa_curses.close_screens(screen)


def system_raid(base_path, state, display_q, sound_q, new_message):
    """Perform system tasks for raid behavior"""

    try:
        if state.raid == "false" and new_message.rx == "toggle":
            state.set_raid("true")
            eqa_config.set_last_state(state, base_path)
            display_q.put(
                eqa_struct.display(
                    eqa_settings.eqa_time(),
                    "event",
                    "events",
                    "Raid mode enabled",
                )
            )
            sound_q.put(eqa_struct.sound("speak", "Raid mode enabled"))
        elif state.raid == "true" and new_message.rx == "toggle":
            state.set_raid("false")
            eqa_config.set_last_state(state, base_path)
            display_q.put(
                eqa_struct.display(
                    eqa_settings.eqa_time(),
                    "event",
                    "events",
                    "Raid mode disabled",
                )
            )
            sound_q.put(eqa_struct.sound("speak", "Raid mode disabled"))
        elif state.raid == "false" and new_message.rx == "true":
            state.set_raid("true")
            eqa_config.set_last_state(state, base_path)
            display_q.put(
                eqa_struct.display(
                    eqa_settings.eqa_time(),
                    "event",
                    "events",
                    new_message.payload,
                )
            )
        elif state.raid == "true" and new_message.rx == "false":
            state.set_raid("false")
            eqa_config.set_last_state(state, base_path)
            display_q.put(
                eqa_struct.display(
                    eqa_settings.eqa_time(),
                    "event",
                    "events",
                    new_message.payload,
                )
            )
        elif (
            new_message.rx == "auto"
            and new_message.payload == "true"
            and state.auto_raid == "false"
        ):
            state.set_auto_raid("true")
            eqa_config.set_last_state(state, base_path)
            display_q.put(
                eqa_struct.display(
                    eqa_settings.eqa_time(),
                    "event",
                    "events",
                    "Raid context will be automatically set by zone",
                )
            )
            sound_q.put(
                eqa_struct.sound(
                    "speak", "Raid context will be automatically set by zone"
                )
            )
        elif (
            new_message.rx == "auto"
            and new_message.payload == "false"
            and state.auto_raid == "true"
        ):
            state.set_auto_raid("false")
            eqa_config.set_last_state(state, base_path)
            display_q.put(
                eqa_struct.display(
                    eqa_settings.eqa_time(),
                    "event",
                    "events",
                    "Raid context will not be automatically updated",
                )
            )
            sound_q.put(
                eqa_struct.sound(
                    "speak", "Raid context will not be automatically updated"
                )
            )
        display_q.put(
            eqa_struct.display(eqa_settings.eqa_time(), "draw", "redraw", "null")
        )

    except Exception as e:
        eqa_settings.log(
            "system raid: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def system_afk(base_path, state, display_q, new_message):
    """Perform system tasks for afk behavior"""

    try:
        if new_message.payload == "true" and state.afk == "false":
            state.set_afk(new_message.payload)
            eqa_config.set_last_state(state, base_path)
            display_q.put(
                eqa_struct.display(
                    eqa_settings.eqa_time(),
                    "event",
                    "events",
                    "You are now AFK",
                )
            )
        elif new_message.payload == "false" and state.afk == "true":
            state.set_afk(new_message.payload)
            eqa_config.set_last_state(state, base_path)
            display_q.put(
                eqa_struct.display(
                    eqa_settings.eqa_time(),
                    "event",
                    "events",
                    "You are no longer AFK",
                )
            )
        display_q.put(
            eqa_struct.display(eqa_settings.eqa_time(), "draw", "redraw", "null")
        )

    except Exception as e:
        eqa_settings.log(
            "system afk: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def system_timer(state, base_path, display_q, sound_q, new_message):
    """Perform system tasks for auto timer behavior"""

    try:
        if new_message.rx == "mob":
            if state.auto_mob_timer == "false" and new_message.payload == "true":
                state.set_auto_mob_timer("true")
                eqa_config.set_last_state(state, base_path)
                display_q.put(
                    eqa_struct.display(
                        eqa_settings.eqa_time(),
                        "event",
                        "events",
                        "Automatic mob respawn timers enabled",
                    )
                )
                sound_q.put(
                    eqa_struct.sound("speak", "Automatic mob respawn timers enabled")
                )
            elif state.auto_mob_timer == "true" and new_message.payload == "false":
                state.set_auto_mob_timer("false")
                eqa_config.set_last_state(state, base_path)
                display_q.put(
                    eqa_struct.display(
                        eqa_settings.eqa_time(),
                        "event",
                        "events",
                        "Automatic mob respawn timers disabled",
                    )
                )
                sound_q.put(
                    eqa_struct.sound("speak", "Automatic mob respawn timers disabled")
                )
        elif new_message.rx == "spell":
            pass
        display_q.put(
            eqa_struct.display(eqa_settings.eqa_time(), "draw", "redraw", "null")
        )

    except Exception as e:
        eqa_settings.log(
            "system debug: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def system_debug(base_path, state, display_q, sound_q, new_message):
    """Perform system tasks for debug behavior"""

    try:
        if state.debug == "false" and new_message.rx == "toggle":
            state.set_debug("true")
            eqa_config.set_last_state(state, base_path)
            display_q.put(
                eqa_struct.display(
                    eqa_settings.eqa_time(),
                    "event",
                    "events",
                    "Debug mode enabled",
                )
            )
            sound_q.put(
                eqa_struct.sound("speak", "Displaying and logging all parser output")
            )
        elif state.debug == "true" and new_message.rx == "toggle":
            state.set_debug("false")
            eqa_config.set_last_state(state, base_path)
            display_q.put(
                eqa_struct.display(
                    eqa_settings.eqa_time(),
                    "event",
                    "events",
                    "Debug mode disabled",
                )
            )
            sound_q.put(eqa_struct.sound("speak", "Debug mode disabled"))
        display_q.put(
            eqa_struct.display(eqa_settings.eqa_time(), "draw", "redraw", "null")
        )

    except Exception as e:
        eqa_settings.log(
            "system debug: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def system_encounter(base_path, state, display_q, sound_q, encounter_q, new_message):
    """Perform system tasks for encounter parse behavior"""

    try:
        if state.encounter_parse == "false" and new_message.rx == "toggle":
            state.set_encounter_parse("true")
            eqa_config.set_last_state(state, base_path)
            display_q.put(
                eqa_struct.display(
                    eqa_settings.eqa_time(),
                    "event",
                    "events",
                    "Encounter Parse Enabled",
                )
            )
            encounter_q.put(
                eqa_struct.message(
                    eqa_settings.eqa_time(), "null", "clear", "null", "null"
                )
            )
            sound_q.put(eqa_struct.sound("speak", "Encounter Parse Enabled"))
        elif state.encounter_parse == "true" and new_message.rx == "toggle":
            state.set_encounter_parse("false")
            eqa_config.set_last_state(state, base_path)
            display_q.put(
                eqa_struct.display(
                    eqa_settings.eqa_time(),
                    "event",
                    "events",
                    "Encounter Parse Disabled",
                )
            )
            sound_q.put(eqa_struct.sound("speak", "Encounter Parse Disabled"))
        elif (
            state.save_parse == "true"
            and new_message.rx == "save"
            and new_message.payload == "false"
        ):
            state.set_encounter_parse_save("false")
            eqa_config.set_last_state(state, base_path)
            display_q.put(
                eqa_struct.display(
                    eqa_settings.eqa_time(),
                    "event",
                    "events",
                    "Encounter parse will not save to a file",
                )
            )
            sound_q.put(
                eqa_struct.sound("speak", "Encounter parser will not save to a file")
            )
        elif (
            state.save_parse == "false"
            and new_message.rx == "save"
            and new_message.payload == "true"
        ):
            state.set_encounter_parse_save("true")
            eqa_config.set_last_state(state, base_path)
            display_q.put(
                eqa_struct.display(
                    eqa_settings.eqa_time(),
                    "event",
                    "events",
                    "Encounter parse will automatically save to a file",
                )
            )
            sound_q.put(
                eqa_struct.sound(
                    "speak", "Encounter parser will automatically save to a file"
                )
            )
        elif new_message.rx == "clear":
            encounter_q.put(
                eqa_struct.message(
                    eqa_settings.eqa_time(), "null", "clear", "null", "null"
                )
            )
        elif new_message.rx == "end":
            encounter_q.put(
                eqa_struct.message(
                    eqa_settings.eqa_time(), "null", "end", "null", "null"
                )
            )
        display_q.put(
            eqa_struct.display(eqa_settings.eqa_time(), "draw", "redraw", "null")
        )

    except Exception as e:
        eqa_settings.log(
            "system encounter: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def system_mute(base_path, state, display_q, sound_q, new_message):
    """Perform system tasks for mute behavior"""

    try:
        if new_message.rx == "toggle" and new_message.payload == "all":
            if state.mute == "false":
                sound_q.put(eqa_struct.sound("mute_speak", "true"))
                sound_q.put(eqa_struct.sound("mute_alert", "true"))
                state.set_mute("true")
                eqa_config.set_last_state(state, base_path)
                display_q.put(
                    eqa_struct.display(
                        eqa_settings.eqa_time(),
                        "event",
                        "events",
                        "Mute Enabled",
                    )
                )
            else:
                sound_q.put(eqa_struct.sound("mute_speak", "false"))
                sound_q.put(eqa_struct.sound("mute_alert", "false"))
                state.set_mute("false")
                eqa_config.set_last_state(state, base_path)
                display_q.put(
                    eqa_struct.display(
                        eqa_settings.eqa_time(),
                        "event",
                        "events",
                        "Mute Disabled",
                    )
                )
                sound_q.put(eqa_struct.sound("speak", "Mute disabled"))
        elif new_message.rx == "toggle" and new_message.payload == "speak":
            if state.mute == "false":
                sound_q.put(eqa_struct.sound("mute_speak", "true"))
                state.set_mute("speak")
                eqa_config.set_last_state(state, base_path)
                display_q.put(
                    eqa_struct.display(
                        eqa_settings.eqa_time(),
                        "event",
                        "events",
                        "Mute Speak Enabled",
                    )
                )
            elif state.mute == "alert":
                sound_q.put(eqa_struct.sound("mute_speak", "true"))
                state.set_mute("true")
                eqa_config.set_last_state(state, base_path)
                display_q.put(
                    eqa_struct.display(
                        eqa_settings.eqa_time(),
                        "event",
                        "events",
                        "Mute Enabled",
                    )
                )
            elif state.mute == "true":
                sound_q.put(eqa_struct.sound("mute_speak", "false"))
                state.set_mute("alert")
                eqa_config.set_last_state(state, base_path)
                display_q.put(
                    eqa_struct.display(
                        eqa_settings.eqa_time(),
                        "event",
                        "events",
                        "Mute Speak Disabled",
                    )
                )
                sound_q.put(eqa_struct.sound("speak", "Mute speak disabled"))
            else:
                sound_q.put(eqa_struct.sound("mute_speak", "false"))
                state.set_mute("false")
                eqa_config.set_last_state(state, base_path)
                display_q.put(
                    eqa_struct.display(
                        eqa_settings.eqa_time(),
                        "event",
                        "events",
                        "Mute Disabled",
                    )
                )
                sound_q.put(eqa_struct.sound("speak", "Mute disabled"))
        elif new_message.rx == "toggle" and new_message.payload == "alert":
            if state.mute == "false":
                sound_q.put(eqa_struct.sound("mute_alert", "true"))
                state.set_mute("alert")
                eqa_config.set_last_state(state, base_path)
                display_q.put(
                    eqa_struct.display(
                        eqa_settings.eqa_time(),
                        "event",
                        "events",
                        "Mute Alert Enabled",
                    )
                )
            elif state.mute == "speak":
                sound_q.put(eqa_struct.sound("mute_alert", "true"))
                state.set_mute("true")
                eqa_config.set_last_state(state, base_path)
                display_q.put(
                    eqa_struct.display(
                        eqa_settings.eqa_time(),
                        "event",
                        "events",
                        "Mute Enabled",
                    )
                )
            elif state.mute == "true":
                sound_q.put(eqa_struct.sound("mute_alert", "false"))
                state.set_mute("speak")
                eqa_config.set_last_state(state, base_path)
                display_q.put(
                    eqa_struct.display(
                        eqa_settings.eqa_time(),
                        "event",
                        "events",
                        "Mute Alert Disabled",
                    )
                )
                sound_q.put(eqa_struct.sound("speak", "Mute alert disabled"))
            else:
                sound_q.put(eqa_struct.sound("mute_alert", "false"))
                state.set_mute("false")
                eqa_config.set_last_state(state, base_path)
                display_q.put(
                    eqa_struct.display(
                        eqa_settings.eqa_time(),
                        "event",
                        "events",
                        "Mute Disabled",
                    )
                )
                sound_q.put(eqa_struct.sound("speak", "Mute disabled"))
        display_q.put(
            eqa_struct.display(eqa_settings.eqa_time(), "draw", "redraw", "null")
        )

    except Exception as e:
        eqa_settings.log(
            "system mute: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


if __name__ == "__main__":
    main()
