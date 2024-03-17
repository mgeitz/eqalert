#! /usr/bin/env python

"""
   Program:   EQ Alert
   File Name: eqa/lib/keys.py
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

import curses
import sys
import time

import eqa.lib.settings as eqa_settings
import eqa.lib.struct as eqa_struct


def process(
    state,
    configs,
    display_q,
    keyboard_q,
    system_q,
    timer_q,
    cfg_reload,
    exit_flag,
):
    """
    Process: keyboard_q
    Produce: display_q, system_q
    """

    chars = state.chars
    lines = len(configs.alerts.config["line"].keys())
    key = ""
    page = "events"
    settings = "character"
    selected_char = 0
    selected_line = 0
    option = "debug"

    try:
        while not exit_flag.is_set() and not cfg_reload.is_set():
            # Sleep between empty checks
            if keyboard_q.qsize() < 1:
                time.sleep(0.01)

            # Check queue for message
            if not keyboard_q.empty():
                ## Read new message
                key = keyboard_q.get()

                ## Check for quit event
                if key == ord("q") or key == 27:
                    exit_flag.set()

                ## Handle resize event
                if key == curses.KEY_RESIZE:
                    display_q.put(
                        eqa_struct.display(
                            eqa_settings.eqa_time(), "draw", "redraw", None
                        )
                    )

                ## Handle tab keys
                if key == ord("1"):
                    display_q.put(
                        eqa_struct.display(
                            eqa_settings.eqa_time(), "draw", "events", None
                        )
                    )
                    page = "events"
                elif key == ord("2"):
                    display_q.put(
                        eqa_struct.display(
                            eqa_settings.eqa_time(), "draw", "state", None
                        )
                    )
                    page = "state"
                elif key == ord("3"):
                    display_q.put(
                        eqa_struct.display(
                            eqa_settings.eqa_time(), "draw", "parse", None
                        )
                    )
                    page = "parse"
                elif key == ord("4"):
                    display_q.put(
                        eqa_struct.display(
                            eqa_settings.eqa_time(), "draw", "settings", None
                        )
                    )
                    page = "settings"
                elif key == ord("h"):
                    display_q.put(
                        eqa_struct.display(
                            eqa_settings.eqa_time(), "draw", "help", None
                        )
                    )
                elif key == ord("t"):
                    timer_q.put(eqa_struct.timer(None, "draw_timers", None, None))
                elif key == ord("0"):
                    system_q.put(
                        eqa_struct.message(
                            eqa_settings.eqa_time(),
                            "system",
                            "reload_config",
                            None,
                            None,
                        )
                    )

                ## Events keys
                if page == "events":
                    if key == ord("c"):
                        display_q.put(
                            eqa_struct.display(
                                eqa_settings.eqa_time(), "event", "clear", None
                            )
                        )
                    elif key == ord("r"):
                        system_q.put(
                            eqa_struct.message(
                                eqa_settings.eqa_time(),
                                "system",
                                "raid",
                                "toggle",
                                None,
                            )
                        )
                    elif key == ord("d"):
                        system_q.put(
                            eqa_struct.message(
                                eqa_settings.eqa_time(),
                                "system",
                                "debug",
                                "toggle",
                                None,
                            )
                        )
                    elif key == ord("e"):
                        system_q.put(
                            eqa_struct.message(
                                eqa_settings.eqa_time(),
                                "system",
                                "encounter",
                                "toggle",
                                None,
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
                    elif key == ord("y"):
                        if not state.auto_mob_timer:
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
                            system_q.put(
                                eqa_struct.message(
                                    eqa_settings.eqa_time(),
                                    "system",
                                    "timer",
                                    "mob",
                                    False,
                                )
                            )
                    elif key == ord("p"):
                        if not state.save_parse:
                            system_q.put(
                                eqa_struct.message(
                                    eqa_settings.eqa_time(),
                                    "system",
                                    "encounter",
                                    "save",
                                    True,
                                )
                            )
                        else:
                            system_q.put(
                                eqa_struct.message(
                                    eqa_settings.eqa_time(),
                                    "system",
                                    "encounter",
                                    "save",
                                    False,
                                )
                            )

                ## State keys
                elif page == "state":
                    pass

                ## Settings keys
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
                        elif key == ord("\n") or key == ord(" "):
                            system_q.put(
                                eqa_struct.message(
                                    eqa_settings.eqa_time(),
                                    "system",
                                    "new_character",
                                    None,
                                    chars[selected_char],
                                )
                            )
                        elif key == ord("\t") or key == ord("`"):
                            settings = "option"
                            display_q.put(
                                eqa_struct.display(
                                    eqa_settings.eqa_time(),
                                    "update",
                                    "setting",
                                    "option",
                                )
                            )

                    elif settings == "option":
                        if key == curses.KEY_UP or key == ord("w"):
                            if option == "debug":
                                pass
                            elif option == "mute":
                                option = "debug"
                            elif option == "raid":
                                option = "mute"
                            elif option == "autoraid":
                                option = "raid"
                            elif option == "encounter":
                                option = "autoraid"
                            elif option == "saveencounter":
                                option = "encounter"
                            elif option == "defaulttimer":
                                option = "saveencounter"
                            elif option == "consider":
                                option = "defaulttimer"
                            elif option == "detect_char":
                                option = "consider"
                            elif option == "spell_self":
                                option = "detect_char"
                            elif option == "spell_other":
                                option = "spell_self"
                            elif option == "spell_guild":
                                option = "spell_other"
                            elif option == "spell_guess":
                                option = "spell_guild"
                            elif option == "spell_yours":
                                option = "spell_guess"
                            display_q.put(
                                eqa_struct.display(
                                    eqa_settings.eqa_time(),
                                    "update",
                                    "option",
                                    option,
                                )
                            )
                        elif key == curses.KEY_DOWN or key == ord("s"):
                            if option == "debug":
                                option = "mute"
                            elif option == "mute":
                                option = "raid"
                            elif option == "raid":
                                option = "autoraid"
                            elif option == "autoraid":
                                option = "encounter"
                            elif option == "encounter":
                                option = "saveencounter"
                            elif option == "saveencounter":
                                option = "defaulttimer"
                            elif option == "defaulttimer":
                                option = "consider"
                            elif option == "consider":
                                option = "detect_char"
                            elif option == "detect_char":
                                option = "spell_self"
                            elif option == "spell_self":
                                option = "spell_other"
                            elif option == "spell_other":
                                option = "spell_guild"
                            elif option == "spell_guild":
                                option = "spell_guess"
                            elif option == "spell_guess":
                                option = "spell_yours"
                            elif option == "spell_yours":
                                pass
                            display_q.put(
                                eqa_struct.display(
                                    eqa_settings.eqa_time(),
                                    "update",
                                    "option",
                                    option,
                                )
                            )
                        elif key == curses.KEY_RIGHT or key == ord("d"):
                            if option == "debug" and state.debug:
                                system_q.put(
                                    eqa_struct.message(
                                        eqa_settings.eqa_time(),
                                        "system",
                                        "debug",
                                        "toggle",
                                        None,
                                    )
                                )
                            elif option == "mute" and state.mute:
                                system_q.put(
                                    eqa_struct.message(
                                        eqa_settings.eqa_time(),
                                        "system",
                                        "mute",
                                        "toggle",
                                        "all",
                                    )
                                )
                            elif option == "raid" and state.raid:
                                system_q.put(
                                    eqa_struct.message(
                                        eqa_settings.eqa_time(),
                                        "system",
                                        "raid",
                                        "toggle",
                                        None,
                                    )
                                )
                            elif option == "autoraid" and state.auto_raid:
                                system_q.put(
                                    eqa_struct.message(
                                        eqa_settings.eqa_time(),
                                        "system",
                                        "raid",
                                        "auto",
                                        False,
                                    )
                                )
                            elif option == "encounter" and state.encounter_parse:
                                system_q.put(
                                    eqa_struct.message(
                                        eqa_settings.eqa_time(),
                                        "system",
                                        "encounter",
                                        "toggle",
                                        None,
                                    )
                                )
                            elif option == "saveencounter" and state.save_parse:
                                system_q.put(
                                    eqa_struct.message(
                                        eqa_settings.eqa_time(),
                                        "system",
                                        "encounter",
                                        "save",
                                        False,
                                    )
                                )
                            elif option == "defaulttimer" and state.auto_mob_timer:
                                system_q.put(
                                    eqa_struct.message(
                                        eqa_settings.eqa_time(),
                                        "system",
                                        "timer",
                                        "mob",
                                        False,
                                    )
                                )
                            elif option == "consider" and state.consider_eval:
                                system_q.put(
                                    eqa_struct.message(
                                        eqa_settings.eqa_time(),
                                        "system",
                                        "consider",
                                        "eval",
                                        False,
                                    )
                                )
                            elif option == "detect_char" and state.detect_char:
                                system_q.put(
                                    eqa_struct.message(
                                        eqa_settings.eqa_time(),
                                        "system",
                                        "detect_char",
                                        None,
                                        False,
                                    )
                                )
                            elif option == "spell_self" and state.spell_timer_self:
                                system_q.put(
                                    eqa_struct.message(
                                        eqa_settings.eqa_time(),
                                        "system",
                                        "spell",
                                        "self",
                                        False,
                                    )
                                )
                            elif option == "spell_other" and state.spell_timer_other:
                                system_q.put(
                                    eqa_struct.message(
                                        eqa_settings.eqa_time(),
                                        "system",
                                        "spell",
                                        "other",
                                        False,
                                    )
                                )
                            elif (
                                option == "spell_guild" and state.spell_timer_guild_only
                            ):
                                system_q.put(
                                    eqa_struct.message(
                                        eqa_settings.eqa_time(),
                                        "system",
                                        "spell",
                                        "guild",
                                        False,
                                    )
                                )
                            elif option == "spell_guess" and state.spell_timer_guess:
                                system_q.put(
                                    eqa_struct.message(
                                        eqa_settings.eqa_time(),
                                        "system",
                                        "spell",
                                        "guess",
                                        False,
                                    )
                                )
                            elif (
                                option == "spell_yours" and state.spell_timer_yours_only
                            ):
                                system_q.put(
                                    eqa_struct.message(
                                        eqa_settings.eqa_time(),
                                        "system",
                                        "spell",
                                        "yours",
                                        False,
                                    )
                                )
                        elif key == curses.KEY_LEFT or key == ord("a"):
                            if option == "debug" and not state.debug:
                                system_q.put(
                                    eqa_struct.message(
                                        eqa_settings.eqa_time(),
                                        "system",
                                        "debug",
                                        "toggle",
                                        None,
                                    )
                                )
                            elif option == "mute" and not state.mute:
                                system_q.put(
                                    eqa_struct.message(
                                        eqa_settings.eqa_time(),
                                        "system",
                                        "mute",
                                        "toggle",
                                        "all",
                                    )
                                )
                            elif option == "raid" and not state.raid:
                                system_q.put(
                                    eqa_struct.message(
                                        eqa_settings.eqa_time(),
                                        "system",
                                        "raid",
                                        "toggle",
                                        "all",
                                    )
                                )
                            elif option == "autoraid" and not state.auto_raid:
                                system_q.put(
                                    eqa_struct.message(
                                        eqa_settings.eqa_time(),
                                        "system",
                                        "raid",
                                        "auto",
                                        True,
                                    )
                                )
                            elif option == "encounter" and not state.encounter_parse:
                                system_q.put(
                                    eqa_struct.message(
                                        eqa_settings.eqa_time(),
                                        "system",
                                        "encounter",
                                        "toggle",
                                        None,
                                    )
                                )
                            elif option == "saveencounter" and not state.save_parse:
                                system_q.put(
                                    eqa_struct.message(
                                        eqa_settings.eqa_time(),
                                        "system",
                                        "encounter",
                                        "save",
                                        True,
                                    )
                                )
                            elif option == "defaulttimer" and not state.auto_mob_timer:
                                system_q.put(
                                    eqa_struct.message(
                                        eqa_settings.eqa_time(),
                                        "system",
                                        "timer",
                                        "mob",
                                        True,
                                    )
                                )
                            elif option == "consider" and not state.consider_eval:
                                system_q.put(
                                    eqa_struct.message(
                                        eqa_settings.eqa_time(),
                                        "system",
                                        "consider",
                                        "eval",
                                        True,
                                    )
                                )
                            elif option == "detect_char" and not state.detect_char:
                                system_q.put(
                                    eqa_struct.message(
                                        eqa_settings.eqa_time(),
                                        "system",
                                        "detect_char",
                                        None,
                                        True,
                                    )
                                )
                            elif option == "spell_self" and not state.spell_timer_self:
                                system_q.put(
                                    eqa_struct.message(
                                        eqa_settings.eqa_time(),
                                        "system",
                                        "spell",
                                        "self",
                                        True,
                                    )
                                )
                            elif (
                                option == "spell_other" and not state.spell_timer_other
                            ):
                                system_q.put(
                                    eqa_struct.message(
                                        eqa_settings.eqa_time(),
                                        "system",
                                        "spell",
                                        "other",
                                        True,
                                    )
                                )
                            elif (
                                option == "spell_guild"
                                and not state.spell_timer_guild_only
                            ):
                                system_q.put(
                                    eqa_struct.message(
                                        eqa_settings.eqa_time(),
                                        "system",
                                        "spell",
                                        "guild",
                                        True,
                                    )
                                )
                            elif (
                                option == "spell_guess" and not state.spell_timer_guess
                            ):
                                system_q.put(
                                    eqa_struct.message(
                                        eqa_settings.eqa_time(),
                                        "system",
                                        "spell",
                                        "guess",
                                        True,
                                    )
                                )
                            elif (
                                option == "spell_yours"
                                and not state.spell_timer_yours_only
                            ):
                                system_q.put(
                                    eqa_struct.message(
                                        eqa_settings.eqa_time(),
                                        "system",
                                        "spell",
                                        "yours",
                                        True,
                                    )
                                )
                        elif key == ord("\t") or key == ord("`"):
                            settings = "line"
                            display_q.put(
                                eqa_struct.display(
                                    eqa_settings.eqa_time(),
                                    "update",
                                    "setting",
                                    "line",
                                )
                            )

                    elif settings == "line":
                        if key == curses.KEY_UP or key == ord("w"):
                            if selected_line < lines - 1:
                                selected_line += 1
                                display_q.put(
                                    eqa_struct.display(
                                        eqa_settings.eqa_time(),
                                        "update",
                                        "selected_line",
                                        selected_line,
                                    )
                                )
                        elif key == curses.KEY_DOWN or key == ord("s"):
                            if selected_line > 0:
                                selected_line -= 1
                                display_q.put(
                                    eqa_struct.display(
                                        eqa_settings.eqa_time(),
                                        "update",
                                        "selected_line",
                                        selected_line,
                                    )
                                )
                        elif key == ord("\t") or key == ord("`"):
                            settings = "character"
                            display_q.put(
                                eqa_struct.display(
                                    eqa_settings.eqa_time(),
                                    "update",
                                    "setting",
                                    "character",
                                )
                            )

                keyboard_q.task_done()

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
    print("Test Here")
