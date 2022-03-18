#! /usr/bin/env python

"""
   Program:   EQ Alert
   File Name: eqa/lib/keys.py
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

import curses
import sys
import time

import eqa.lib.settings as eqa_settings
import eqa.lib.struct as eqa_struct


def process(
    chars,
    display_q,
    keyboard_q,
    system_q,
    cfg_reload,
    exit_flag,
):
    """
    Process: keyboard_q
    Produce: display_q, system_q
    """

    key = ""
    page = "events"
    settings = "character"
    selected_char = 0

    while not exit_flag.is_set() and not cfg_reload.is_set():
        try:
            # Get key
            time.sleep(0.01)
            if not keyboard_q.empty():
                key = keyboard_q.get()
                keyboard_q.task_done()

                # Check for quit event
                if key == ord("q") or key == 27:
                    exit_flag.set()

                # Handle resize event
                if key == curses.KEY_RESIZE:
                    display_q.put(
                        eqa_struct.display(
                            eqa_settings.eqa_time(), "draw", "redraw", "null"
                        )
                    )

                # Handle tab keys
                if key == curses.KEY_F1:
                    display_q.put(
                        eqa_struct.display(
                            eqa_settings.eqa_time(), "draw", "events", "null"
                        )
                    )
                    page = "events"
                elif key == curses.KEY_F2:
                    display_q.put(
                        eqa_struct.display(
                            eqa_settings.eqa_time(), "draw", "state", "null"
                        )
                    )
                    page = "state"
                elif key == curses.KEY_F3:
                    display_q.put(
                        eqa_struct.display(
                            eqa_settings.eqa_time(), "draw", "settings", "null"
                        )
                    )
                    page = "settings"
                elif key == curses.KEY_F4:
                    display_q.put(
                        eqa_struct.display(
                            eqa_settings.eqa_time(), "draw", "help", "null"
                        )
                    )
                    page = "help"
                elif key == curses.KEY_F12:
                    system_q.put(
                        eqa_struct.message(
                            eqa_settings.eqa_time(),
                            "system",
                            "reload_config",
                            "null",
                            "null",
                        )
                    )

                # Events keys
                if page == "events":
                    if key == ord("c"):
                        display_q.put(
                            eqa_struct.display(
                                eqa_settings.eqa_time(), "event", "clear", "null"
                            )
                        )
                    elif key == ord("r"):
                        system_q.put(
                            eqa_struct.message(
                                eqa_settings.eqa_time(),
                                "system",
                                "raid",
                                "toggle",
                                "null",
                            )
                        )
                    elif key == ord("d"):
                        system_q.put(
                            eqa_struct.message(
                                eqa_settings.eqa_time(),
                                "system",
                                "debug",
                                "toggle",
                                "null",
                            )
                        )
                    elif key == ord("m"):
                        system_q.put(
                            eqa_struct.message(
                                eqa_settings.eqa_time(),
                                "system",
                                "mute",
                                "toggle",
                                "all",
                            )
                        )

                # State keys
                elif page == "state":
                    pass

                # Settings keys
                elif page == "settings":
                    if settings == "character":
                        if key == curses.KEY_UP or key == ord("w"):
                            if selected_char < len(chars) - 1:
                                selected_char += 1
                                display_q.put(
                                    eqa_struct.display(
                                        eqa_settings.eqa_time(),
                                        "update",
                                        "selected_char",
                                        selected_char,
                                    )
                                )
                        elif key == curses.KEY_DOWN or key == ord("s"):
                            if selected_char > 0:
                                selected_char -= 1
                                display_q.put(
                                    eqa_struct.display(
                                        eqa_settings.eqa_time(),
                                        "update",
                                        "selected_char",
                                        selected_char,
                                    )
                                )
                        elif key == curses.KEY_RIGHT or key == ord("d"):
                            display_q.put(
                                eqa_struct.display(
                                    eqa_settings.eqa_time(),
                                    "update",
                                    "zone",
                                    "unavailable",
                                )
                            )
                            system_q.put(
                                eqa_struct.message(
                                    eqa_settings.eqa_time(),
                                    "system",
                                    "new_character",
                                    "null",
                                    chars[selected_char],
                                )
                            )
                        elif key == ord(" "):
                            pass
                            # cycle to next setting

                # Help keys
                elif page == "help":
                    pass

        except Exception as e:
            eqa_settings.log("process keys: " + str(e))
            eqa_settings.log("setting exit_flag")
            exit_flag.set()
            sys.exit()

    sys.exit(0)


def read(exit_flag, keyboard_q, stdscr):
    """
    Consume: keyboard events
    Produce: keyboard_q
    """

    key = ""
    try:
        while not exit_flag.is_set():
            key = stdscr.getch()
            keyboard_q.put(key)
        sys.exit(0)
    except Exception as e:
        eqa_settings.log("read keys: " + str(e))
        sys.exit(0)


if __name__ == "__main__":
    main()
