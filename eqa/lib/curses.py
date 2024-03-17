#! /usr/bin/env python

"""
   Program:   EQ Alert
   File Name: eqa/lib/curses.py
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
import heapq
import os
import sys
import time
import math
import random
import re
from datetime import datetime

import eqa.lib.struct as eqa_struct
import eqa.lib.state as eqa_state
import eqa.lib.settings as eqa_settings


def display(stdscr, display_q, state, configs, exit_flag, cfg_reload, version):
    """
    Process: display_q
    Produce: display event
    """
    events = []
    debug_events = []
    page = "events"
    last_page = "events"
    s_setting = "character"
    s_char = 0
    s_opt = "debug"
    s_line = 0
    encounter_report = None
    timers = None

    try:
        while not exit_flag.is_set() and not cfg_reload.is_set():
            # Sleep between empty checks
            if display_q.qsize() < 1:
                time.sleep(0.01)

            # Check queue for message
            if not display_q.empty():
                ## Read new message
                display_event = display_q.get()

                ## Display Var Update
                if display_event.type == "update":
                    if display_event.screen == "setting":
                        s_setting = display_event.payload
                    elif display_event.screen == "option":
                        s_opt = display_event.payload
                    elif display_event.screen == "selected_line":
                        s_line = display_event.payload
                    elif display_event.screen == "selected_char":
                        s_char = display_event.payload
                    elif display_event.screen == "select_char":
                        s_char = display_event.payload
                        state.char = state.chars[selected_char]
                    elif display_event.screen == "zone":
                        zone = display_event.payload
                    elif display_event.screen == "char":
                        state.char = display_event.payload
                    elif display_event.screen == "encounter":
                        encounter_report = display_event.payload
                    draw_page(
                        stdscr,
                        page,
                        events,
                        debug_events,
                        state,
                        configs,
                        s_setting,
                        s_char,
                        s_opt,
                        s_line,
                        encounter_report,
                        version,
                        timers,
                    )

                ## Display Draw
                elif display_event.type == "draw":
                    if display_event.screen == "help":
                        if page == "help":
                            page = last_page
                        elif page != "timers":
                            last_page = page
                            page = display_event.screen
                        else:
                            page = display_event.screen
                    elif display_event.screen == "timers":
                        if page == "timers":
                            page = last_page
                        elif page != "help":
                            last_page = page
                            timers = display_event.payload
                            page = display_event.screen
                        else:
                            timers = display_event.payload
                            page = display_event.screen
                    elif display_event.screen == "redraw":
                        if page == "help" or page == "timers":
                            draw_page(
                                stdscr,
                                page,
                                events,
                                debug_events,
                                state,
                                configs,
                                s_setting,
                                s_char,
                                s_opt,
                                s_line,
                                encounter_report,
                                version,
                                timers,
                            )
                    else:
                        page = display_event.screen

                    draw_page(
                        stdscr,
                        page,
                        events,
                        debug_events,
                        state,
                        configs,
                        s_setting,
                        s_char,
                        s_opt,
                        s_line,
                        encounter_report,
                        version,
                        timers,
                    )

                ## Draw Update
                elif display_event.type == "event":
                    if display_event.screen == "events":
                        events.append(display_event)
                        if page == "events":
                            draw_page(
                                stdscr,
                                page,
                                events,
                                debug_events,
                                state,
                                configs,
                                s_setting,
                                s_char,
                                s_opt,
                                s_line,
                                encounter_report,
                                version,
                                timers,
                            )
                    elif display_event.screen == "debug":
                        debug_events.append(display_event)
                        draw_page(
                            stdscr,
                            page,
                            events,
                            debug_events,
                            state,
                            configs,
                            s_setting,
                            s_char,
                            s_opt,
                            s_line,
                            encounter_report,
                            version,
                            timers,
                        )
                    elif display_event.screen == "clear":
                        events = []
                        debug_events = []
                        draw_page(
                            stdscr,
                            page,
                            events,
                            debug_events,
                            state,
                            configs,
                            s_setting,
                            s_char,
                            s_opt,
                            s_line,
                            encounter_report,
                            version,
                            timers,
                        )
                display_q.task_done()

    except Exception as e:
        eqa_settings.log(
            "display: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )

    sys.exit()


def draw_page(
    stdscr,
    page,
    events,
    debug_events,
    state,
    configs,
    s_setting,
    s_char,
    s_opt,
    s_line,
    encounter_report,
    version,
    timers,
):
    y, x = stdscr.getmaxyx()
    try:
        if x >= 80 and y >= 40:
            if page == "events":
                draw_events_frame(
                    stdscr, state, events, debug_events, encounter_report, version
                )
            elif page == "state":
                draw_state(stdscr, state, version)
            elif page == "settings":
                draw_settings(
                    stdscr, state, configs, s_setting, s_char, s_opt, s_line, version
                )
            elif page == "parse":
                draw_parse(stdscr, state, encounter_report, version)
            elif page == "help":
                draw_help(stdscr)
            elif page == "timers":
                copy_timers = timers.copy()
                draw_timers(stdscr, copy_timers)
        else:
            draw_toosmall(stdscr)
    except Exception as e:
        eqa_settings.log(
            "draw_page: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def init(state, version):
    try:
        """Create new stdscr in terminal"""
        stdscr = curses.initscr()
        os.system("setterm -cursor off")
        curses.start_color()
        curses.use_default_colors()
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(1)
        stdscr.timeout(100)
        curses.init_pair(1, curses.COLOR_WHITE, -1)  # Title
        curses.init_pair(2, curses.COLOR_YELLOW, -1)  # Header
        curses.init_pair(3, curses.COLOR_CYAN, -1)  # Subtext
        curses.init_pair(4, curses.COLOR_MAGENTA, -1)  # Highlight
        curses.init_pair(5, curses.COLOR_GREEN, -1)  # Dunno
        curses.init_pair(6, curses.COLOR_RED, -1)  # Dunno
        draw_events_frame(stdscr, state, [], [], None, version)
        return stdscr

    except Exception as e:
        eqa_settings.log(
            "draw init: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def close_screens(stdscr):
    """Terminate stdscr"""
    os.system("setterm -cursor on")
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()


def draw_tabs(stdscr, tab, version):
    """Draw top row tab selection"""

    try:
        y, x = stdscr.getmaxyx()
        center_y = int(y / 2)
        center_x = int(x / 2)

        # Bottom of tabs
        stdscr.addch(2, 0, curses.ACS_LTEE)
        stdscr.addch(2, x - 1, curses.ACS_RTEE)
        for c in range(x - 2):
            stdscr.addch(2, c + 1, curses.ACS_HLINE)

        # Events tab
        stdscr.addstr(1, 2, "1", curses.color_pair(3))
        stdscr.addstr(1, 3, ":", curses.color_pair(1))
        if tab == "events":
            stdscr.addstr(1, 5, "events", curses.color_pair(4))
        else:
            stdscr.addstr(1, 5, "events", curses.color_pair(2))
        stdscr.addch(0, 12, curses.ACS_TTEE)
        stdscr.addch(1, 12, curses.ACS_VLINE)
        stdscr.addch(2, 12, curses.ACS_BTEE)

        # State tab
        stdscr.addstr(1, 14, "2", curses.color_pair(3))
        stdscr.addstr(1, 15, ":", curses.color_pair(1))
        if tab == "state":
            stdscr.addstr(1, 17, "state", curses.color_pair(4))
        else:
            stdscr.addstr(1, 17, "state", curses.color_pair(2))
        stdscr.addch(0, 23, curses.ACS_TTEE)
        stdscr.addch(1, 23, curses.ACS_VLINE)
        stdscr.addch(2, 23, curses.ACS_BTEE)

        # Parse tab
        stdscr.addstr(1, x - 24, "3", curses.color_pair(3))
        stdscr.addstr(1, x - 23, ":", curses.color_pair(1))
        if tab == "parse":
            stdscr.addstr(1, x - 21, "parse", curses.color_pair(4))
        else:
            stdscr.addstr(1, x - 21, "parse", curses.color_pair(2))
        stdscr.addch(0, x - 26, curses.ACS_TTEE)
        stdscr.addch(1, x - 26, curses.ACS_VLINE)
        stdscr.addch(2, x - 26, curses.ACS_BTEE)

        # Settings tab
        stdscr.addstr(1, x - 13, "4", curses.color_pair(3))
        stdscr.addstr(1, x - 12, ":", curses.color_pair(1))
        if tab == "settings":
            stdscr.addstr(1, x - 10, "settings", curses.color_pair(4))
        else:
            stdscr.addstr(1, x - 10, "settings", curses.color_pair(2))
        stdscr.addch(0, x - 15, curses.ACS_TTEE)
        stdscr.addch(1, x - 15, curses.ACS_VLINE)
        stdscr.addch(2, x - 15, curses.ACS_BTEE)

        # Center title
        offset = math.ceil(len(version) / 2)
        stdscr.addstr(
            1, center_x - 4 - offset, "EQ ALERT " + version, curses.color_pair(2)
        )

    except Exception as e:
        eqa_settings.log(
            "draw tabs: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def draw_events_frame(stdscr, state, events, debug_events, encounter_report, version):
    """Draw events"""

    try:
        # Clear and box
        stdscr.clear()
        stdscr.box()

        # Draw tabs
        draw_tabs(stdscr, "events", version)

        # Draw status
        draw_events_status_bar(stdscr, state)

        # Draw events panel
        draw_events(stdscr, events)

        # Draw lower panel
        if state.debug:
            draw_events_debug(stdscr, debug_events)
        elif state.encounter_parse and encounter_report is not None:
            draw_events_encounter(stdscr, encounter_report)
        else:
            draw_events_default_lower(stdscr)

    except Exception as e:
        eqa_settings.log(
            "draw events frame: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def draw_events_status_bar(stdscr, state):
    """Draw events status bar"""

    try:
        y, x = stdscr.getmaxyx()
        center_y = int(y / 2)
        center_x = int(x / 2)

        # Draw status bar
        ## Top of stats bar
        stdscr.addch(center_y - 1, 0, curses.ACS_LTEE)
        stdscr.addch(center_y - 1, x - 1, curses.ACS_RTEE)
        for c in range(x - 2):
            stdscr.addch(center_y - 1, c + 1, curses.ACS_HLINE)

        ## Character
        stdscr.addstr(center_y, 2, state.char.title(), curses.color_pair(2))

        ## Guild
        if state.char_guild is not None:
            stdscr.addstr(
                center_y,
                3 + len(state.char),
                state.char_guild.title(),
                curses.color_pair(2),
            )

        ## Level
        if state.char_level is not None:
            stdscr.addstr(center_y + 1, 2, str(state.char_level), curses.color_pair(2))

        ## Class
        if state.char_class is not None:
            stdscr.addstr(
                center_y + 1,
                3 + len(str(state.char_level)),
                state.char_class.title(),
                curses.color_pair(2),
            )

        ## Zone
        if state.zone is not None:
            stdscr.addstr(
                center_y,
                x - len(state.zone) - 2,
                state.zone.title(),
                curses.color_pair(2),
            )

        ## Direction
        if state.direction is not None:
            stdscr.addstr(
                center_y + 1,
                x - len(state.direction) - 2,
                state.direction.title(),
                curses.color_pair(2),
            )

        ## Location
        if state.loc != ["0.00", "0.00", "0.00"]:
            if state.direction is not None:
                offset = (
                    len(str(state.direction))
                    + len(str(state.loc[0]))
                    + len(str(state.loc[1]))
                    + len(str(state.loc[2]))
                )
            else:
                offset = (
                    len(str(state.loc[0]))
                    + len(str(state.loc[1]))
                    + len(str(state.loc[2]))
                )
            stdscr.addstr(
                center_y + 1,
                x - offset - 7,
                str(state.loc[0]) + ", " + str(state.loc[1]) + ", " + str(state.loc[2]),
                curses.color_pair(2),
            )

        ## Server
        offset = math.ceil(len(str(state.server)) / 2)
        stdscr.addstr(center_y, center_x - offset, state.server, curses.color_pair(2))

        ## Context

        ### AFK (clobbers other status)
        if state.afk:
            stdscr.addstr(center_y + 1, center_x - 1, "AFK", curses.color_pair(2))

        ### Solo
        elif not state.group and not state.raid:
            stdscr.addstr(center_y + 1, center_x - 2, "Solo", curses.color_pair(2))

        ### Grouped
        elif state.group:
            current_leader = state.leader

            ### Grouped / Raiding
            if not state.raid:
                group_type = " Group"
            else:
                group_type = " Raid Group"

            ### Group Leader
            if current_leader == "you":
                group_leader = "Your"
                leader_len = 4 + len(group_type)
            else:
                group_leader = current_leader.title() + "'s"
                leader_len = len(group_leader) + len(group_type)

            stdscr.addstr(
                center_y + 1,
                center_x - math.ceil(leader_len / 2),
                group_leader + group_type,
                curses.color_pair(2),
            )

        ### Raiding Ungrouped
        elif state.raid and not state.group:
            stdscr.addstr(center_y + 1, center_x - 2, "Raid", curses.color_pair(2))

        ## Bottom of stats bar
        stdscr.addch(center_y + 2, 0, curses.ACS_LTEE)
        stdscr.addch(center_y + 2, x - 1, curses.ACS_RTEE)
        for c in range(x - 2):
            stdscr.addch(center_y + 2, c + 1, curses.ACS_HLINE)

    except Exception as e:
        eqa_settings.log(
            "draw events status bar: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def draw_events(stdscr, events):
    """Draw events window component of events"""

    try:
        y, x = stdscr.getmaxyx()
        center_y = int(y / 2)
        event_win_y = center_y - 4
        event_win_x = x - 4
        eventscr = stdscr.derwin(event_win_y, event_win_x, 3, 2)
        eventscr.clear()

        count = 1
        max_event_string_x = event_win_x - 17
        while (count - 1) < event_win_y and count < len(events):
            event = events[-count]
            draw_ftime(eventscr, event.timestamp, event_win_y - count)
            eventscr.addch(event_win_y - count, 14, curses.ACS_VLINE)
            eventscr.addstr(
                event_win_y - count,
                16,
                str(event.payload)[:max_event_string_x],
                curses.color_pair(1),
            )
            count += 1

    except Exception as e:
        eqa_settings.log(
            "draw events: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def draw_events_debug(stdscr, debug_events):
    """Draw events lower panel as debugs"""

    try:
        y, x = stdscr.getmaxyx()
        center_y = int(y / 2)
        debug_win_y = center_y - 4
        debug_win_x = x - 4
        debugscr = stdscr.derwin(debug_win_y, debug_win_x, center_y + 3, 2)
        debugscr.clear()

        count = 1
        max_debug_string_x = debug_win_x - 34
        while (count - 1) < debug_win_y and count < len(debug_events):
            event = debug_events[-count]
            line_type = event.payload[0]
            line = event.payload[1]
            debugscr.addstr(
                debug_win_y - count, 1, line_type[:29], curses.color_pair(3)
            )
            debugscr.addch(debug_win_y - count, 31, curses.ACS_VLINE)
            debugscr.addstr(
                debug_win_y - count,
                33,
                str(line)[:max_debug_string_x],
                curses.color_pair(1),
            )
            count += 1

    except Exception as e:
        eqa_settings.log(
            "draw debug events: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def draw_events_default_lower(stdscr):
    """Draw default lower pane"""

    try:
        y, x = stdscr.getmaxyx()
        center_y = int(y / 2)
        default_win_y = center_y - 4
        default_win_x = x - 4
        defscr = stdscr.derwin(default_win_y, default_win_x, center_y + 3, 2)
        defscr.clear()

        responses = [
            "Press 'h' to access the help menu",
            "Press 'h' to access the help menu",
            "Press 'h' to access the help menu",
            "Press 'h' to access the help menu",
            "Press 'h' to access the help menu",
            "Press 'h' to access the help menu",
            "Press 'h' to access the help menu",
            "Press 'h' to access the help menu",
            "Press 'h' to access the help menu",
            "Press 'h' to access the help menu",
            "Use `/char` to view your bind point",
            "Set `/loc` to common macros",
            "Firiona Vie is a lie",
            "Use 'shift + t' to look behind you",
            "Press 'd' to toggle debug mode",
            "Press 'e' to toggle encounter parsing",
            "Press 'm' to toggle mute",
            "Press 'p' to toggle encounter parse saves",
            "Press 't' to toggle automatic respawn timers",
            "`/say parser why`",
            "Thanks Daldaen",
            "Edit config/line-alerts/*.json to customize alerts",
            "Remember to water your house plants",
            "Sending Fippy Darkpaw batphone . . .",
            "Use `/book #` to quickly access spells",
            "Always train each skill to at least 1",
            "Use `/list` if you want a bad experience",
            "Have a nice " + datetime.today().strftime("%A"),
            "Use `/hidecorpse looted` to reduce client lag",
            "Remember to load junk buffs first",
            "Using `/viewport x y w h` can restore a 4:3 ratio",
            "Using `/viewport reset` will reset your viewport",
            "There are 93 emote commands",
            "EverQuest released March 16 1999",
            "FPS determines the rate of turning",
            "This window is "
            + str(default_win_x)
            + " by "
            + str(default_win_y)
            + " cells",
            "Use 'shift + left click' to move item stacks",
            "Use `/autoinventory` when foraging",
            "Use 'ctrl + left click' to move a single item",
            "Remember to train sense heading",
            "Always tip your porter",
            "Using `/who` will update your eqalert char info",
            "Always use levitate in Kelethin",
            "Have you spent your DKP today?",
            "Please submit any bugs to github",
            "A good day for Project 1999",
            "Is Phinigel Autropos up?",
            "How secret is Secrets' secret secrets?",
            "Sirken might say A+ to that",
            "Rogean is watching",
            "We don't talk about Derubael",
            "Nilbog will fix it",
            "Fill your ammo slot to leave corpses",
            "Use `/pause #` to add delays to your macros",
            "Relive the classic Everquest experience",
            "Right click to lock UI elements",
            "Use 'alt + o' to view in-game options",
            "There are 11 different tradeskills",
            "Pending Lore for 24 years now",
            "Check out aLovingRobot on youtube",
            "Thanks for using EQAlert",
            "When in doubt, `/q` out",
            "Remember to be kind",
            "Hydration is critical",
            "Does stamina work yet?",
            "Check out the Project 1999 Forums!",
            "Use `/inv` to send or accept group invites",
            "Try `/disband` to resolve the group invite bug"
            "Normal track sort orders new to old spawns",
            "Project 1999 released October 2009",
            "You can buy carrots in Rivervale",
            "Each server has a Magelo on the wiki",
            "Don't panic and always carry a DA Idol",
            "Is Wuoshi up?",
            "Use `/load ui` if you must leave an empty corpse",
            "Use `/em [anything]` to create custom emotes",
            "Some mobs won't flee if they have friends nearby",
            "Use `/corpse` to drag a corpse",
            "Some mobs aggro when a corpse is dragged",
            "You can use your corpse to store lore items",
            "You can use your corpse to store no rent items",
            "In a pinch, you can use sneak to bank",
            "You can use parser say commands in macros",
            "Use instant click items to refresh your GCD",
            "Trading coins will briefly remove their weight",
            "Diagonal running is the fastest",
            "Using 'F7' can target anyone for any buff",
            "You can send tells between servers",
            "'PgUp' & 'PgDn' modify the z-axis in 3rd person",
            "You can use `/` to replace `/who`",
        ]
        response = random.choice(responses)

        draw_mascot_message(defscr, response)

    except Exception as e:
        eqa_settings.log(
            "draw events default: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def draw_events_encounter(stdscr, encounter_report):
    """Draw events lower panel as encounter"""

    try:
        y, x = stdscr.getmaxyx()
        center_y = int(y / 2)
        encounter_win_y = center_y - 4
        encounter_win_x = x - 4
        mid_encounter_win_x = int(encounter_win_x / 2)
        mid_encounter_win_y = int(encounter_win_y / 2)
        encounterscr = stdscr.derwin(encounter_win_y, encounter_win_x, center_y + 3, 2)
        encounterscr.clear()

        # Center Line
        center_line = 0
        while center_line < encounter_win_y:
            encounterscr.addch(center_line, mid_encounter_win_x, curses.ACS_VLINE)
            center_line += 1

        # Target Title
        name_padding = (
            int(mid_encounter_win_x / 2)
            - int(len(encounter_report["target"]["name"]) / 2)
            - len(encounter_report["encounter_summary"]["duration"])
            - 2
        )
        target_title = (
            encounter_report["target"]["name"]
            + " in "
            + encounter_report["encounter_summary"]["duration"]
        )
        encounterscr.addstr(0, name_padding, target_title, curses.color_pair(5))

        # Target Underline
        first_quarter = int(mid_encounter_win_x / 2)
        underline = 4
        while underline < (mid_encounter_win_x - 4):
            if underline == first_quarter:
                encounterscr.addch(1, underline, curses.ACS_TTEE, curses.color_pair(3))
            else:
                encounterscr.addch(1, underline, curses.ACS_HLINE, curses.color_pair(3))
            underline += 1

        # Target Mid-line
        midline = 2
        while midline < (encounter_win_y - 1):
            encounterscr.addch(
                midline, first_quarter, curses.ACS_VLINE, curses.color_pair(3)
            )
            midline += 1

        # Target Stats
        count = 2
        for entry in encounter_report["target"]:
            if entry != "name" and entry != "killed":
                encounterscr.addstr(
                    count,
                    4,
                    str(entry.title())[:first_quarter].replace("_", " ").title(),
                    curses.color_pair(5),
                )
                if "dps" in entry or "activity" in entry:
                    value = str(format(float(encounter_report["target"][entry]), ".2f"))
                else:
                    value = str(encounter_report["target"][entry])
                encounterscr.addstr(
                    count,
                    first_quarter + 2,
                    value[:first_quarter].replace("_", " ").title(),
                    curses.color_pair(1),
                )
                count += 1

        # Participant Stats
        participant = 0
        third_quarter = first_quarter + mid_encounter_win_x
        players = list(encounter_report["participants"].keys())

        if len(players) > 0:
            # Top P1 Title
            name_padding = third_quarter - int(len(players[0]) / 2)
            encounterscr.addstr(
                0, name_padding, players[0].title(), curses.color_pair(5)
            )

            # Top P1 Underline
            underline = mid_encounter_win_x + 4
            while underline < (encounter_win_x - 4):
                if underline == third_quarter:
                    encounterscr.addch(
                        1, underline, curses.ACS_TTEE, curses.color_pair(3)
                    )
                else:
                    encounterscr.addch(
                        1, underline, curses.ACS_HLINE, curses.color_pair(3)
                    )
                underline += 1

            # Top P1 Mid-line
            midline = 2
            while midline < (mid_encounter_win_y - 1):
                encounterscr.addch(
                    midline, third_quarter, curses.ACS_VLINE, curses.color_pair(3)
                )
                midline += 1

            # Top P1 Stats
            count = 2
            for entry in encounter_report["participants"][players[0]]:
                if count >= mid_encounter_win_y:
                    break
                encounterscr.addstr(
                    count,
                    mid_encounter_win_x + 4,
                    str(entry)[:first_quarter].replace("_", " ").title(),
                    curses.color_pair(5),
                )
                if "dps" in entry or "activity" in entry:
                    value = str(
                        format(
                            float(encounter_report["participants"][players[0]][entry]),
                            ".2f",
                        )
                    )
                else:
                    value = str(encounter_report["participants"][players[0]][entry])
                encounterscr.addstr(
                    count,
                    third_quarter + 2,
                    str(value)[:first_quarter].replace("_", " ").title(),
                    curses.color_pair(1),
                )
                count += 1

        if len(players) > 1:
            # Top P2 Title
            name_padding = third_quarter - int(len(players[1]) / 2)
            encounterscr.addstr(
                mid_encounter_win_y,
                name_padding,
                players[1].title(),
                curses.color_pair(5),
            )

            # Top P2 Underline
            underline = mid_encounter_win_x + 4
            while underline < (encounter_win_x - 4):
                if underline == third_quarter:
                    encounterscr.addch(
                        mid_encounter_win_y + 1,
                        underline,
                        curses.ACS_TTEE,
                        curses.color_pair(3),
                    )
                else:
                    encounterscr.addch(
                        mid_encounter_win_y + 1,
                        underline,
                        curses.ACS_HLINE,
                        curses.color_pair(3),
                    )
                underline += 1

            # Top P2 Mid-line
            midline = mid_encounter_win_y + 2
            while midline < (encounter_win_y - 1):
                encounterscr.addch(
                    midline, third_quarter, curses.ACS_VLINE, curses.color_pair(3)
                )
                midline += 1

            # Top P2 Stats
            count = mid_encounter_win_y + 2
            for entry in encounter_report["participants"][players[1]]:
                if count >= encounter_win_y - 1:
                    break
                encounterscr.addstr(
                    count,
                    mid_encounter_win_x + 4,
                    str(entry)[:first_quarter].replace("_", " ").title(),
                    curses.color_pair(5),
                )
                if "dps" in entry or "activity" in entry:
                    value = str(
                        format(
                            float(encounter_report["participants"][players[1]][entry]),
                            ".2f",
                        )
                    )
                else:
                    value = str(encounter_report["participants"][players[1]][entry])
                encounterscr.addstr(
                    count,
                    third_quarter + 2,
                    value[:first_quarter].replace("_", " ").title(),
                    curses.color_pair(1),
                )
                count += 1

    except Exception as e:
        eqa_settings.log(
            "draw encounter events: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def draw_ftime(stdscr, timestamp, y):
    """Draw formatted time for events"""
    try:
        h, m, second = timestamp.split(":")
        s, ms = second.split(".")

        stdscr.addstr(y, 1, h, curses.color_pair(3))
        stdscr.addstr(y, 3, ":", curses.color_pair(2))
        stdscr.addstr(y, 4, m, curses.color_pair(3))
        stdscr.addstr(y, 6, ":", curses.color_pair(2))
        stdscr.addstr(y, 7, s, curses.color_pair(3))
        stdscr.addstr(y, 9, ".", curses.color_pair(2))
        stdscr.addstr(y, 10, ms, curses.color_pair(3))

    except Exception as e:
        eqa_settings.log(
            "draw ftime: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def draw_parse(stdscr, state, encounter_report, version):
    """Draw parse"""
    y, x = stdscr.getmaxyx()

    # Clear and box
    stdscr.clear()
    stdscr.box()

    # Draw tabs
    draw_tabs(stdscr, "parse", version)

    try:
        encounterscr = stdscr.derwin(int(y / 2) - 3, x - 2, 3, 1)
        encounterscr.clear()
        encounter_y, encounter_x = encounterscr.getmaxyx()
        center_y = int(encounter_y / 2)
        center_x = int(encounter_x / 2)
        first_quarter = int(encounter_x / 4)
        third_quarter = center_x + first_quarter
        first_third = int(encounter_x / 3)
        second_third = first_third + first_third
        playerscr = stdscr.derwin(int(y / 2) - 1, encounter_x, int(y / 2), 1)
        playerscr_y, playerscr_x = playerscr.getmaxyx()
        playerscr.clear()

        # If we're parsing encounters
        if state.encounter_parse:
            ## If we have a report to show
            if encounter_report is not None:
                target_name = encounter_report["target"]["name"].title()

                # Target Line
                underline = 3
                while underline < (center_x - 2):
                    encounterscr.addch(
                        1, underline, curses.ACS_HLINE, curses.color_pair(3)
                    )
                    underline += 1

                ### Target Title
                # encounterscr.addch(1, ((center_x - (len(targetname) / 2)) - 1), curses.ACS_RTEE, curses.color_pair(1))
                encounterscr.addstr(
                    1,
                    first_quarter - int(len(target_name) / 2),
                    " " + target_name + " ",
                    curses.color_pair(2),
                )

                ### Target Stats
                count = 3
                for entry in encounter_report["target"]:
                    if entry != "name" and entry != "killed":
                        encounterscr.addstr(
                            count,
                            3,
                            str(entry.title())[:first_quarter]
                            .replace("_", " ")
                            .title(),
                            curses.color_pair(5),
                        )
                        if "dps" in entry or "activity" in entry:
                            value = str(
                                format(float(encounter_report["target"][entry]), ".2f")
                            )
                        else:
                            value = str(encounter_report["target"][entry])
                        encounterscr.addstr(
                            count,
                            22,
                            value[:first_quarter].replace("_", " ").title(),
                            curses.color_pair(1),
                        )
                        count += 1

                    #### Killed
                    elif entry == "killed":
                        encounterscr.addstr(
                            3,
                            first_third,
                            "Killed:",
                            curses.color_pair(6),
                        )
                        kill_count = 4
                        for victim in encounter_report["target"]["killed"].keys():
                            encounterscr.addstr(
                                kill_count,
                                first_third + 2,
                                victim[:12].title(),
                                curses.color_pair(3),
                            )
                            encounterscr.addstr(
                                kill_count,
                                first_third + 14,
                                encounter_report["target"]["killed"][victim],
                                curses.color_pair(1),
                            )
                            kill_count += 1

                ### Encounter Line
                underline = center_x + 2
                while underline < (encounter_x - 2):
                    encounterscr.addch(
                        1, underline, curses.ACS_HLINE, curses.color_pair(3)
                    )
                    underline += 1

                ### Encounter Title
                encounterscr.addstr(
                    1,
                    third_quarter - 9,
                    " Encounter Summary ",
                    curses.color_pair(2),
                )

                ### Encounter Summary
                count = 3
                for entry in encounter_report["encounter_summary"]:
                    encounterscr.addstr(
                        count,
                        center_x + 2,
                        str(entry.title())[:first_quarter].replace("_", " ").title(),
                        curses.color_pair(5),
                    )
                    if entry == "location":
                        value = re.sub(
                            r"[^\d+\.\,\-\s]",
                            "",
                            encounter_report["encounter_summary"][entry],
                        )
                    else:
                        value = encounter_report["encounter_summary"][entry]
                    encounterscr.addstr(
                        count,
                        center_x + 21,
                        str(value)[:first_quarter].replace("_", " ").title(),
                        curses.color_pair(1),
                    )
                    count += 1

                ### Player Line
                underline = 2
                while underline < (playerscr_x - 2):
                    playerscr.addch(
                        0, underline, curses.ACS_HLINE, curses.color_pair(3)
                    )
                    underline += 1

                ### Player Title
                playerscr.addstr(
                    0, int(playerscr_x / 2) - 4, " Players ", curses.color_pair(2)
                )

                ### Player Summary
                player_x = 1
                player_y = 2
                for player in encounter_report["participants"].keys():
                    if len(encounter_report["participants"][player].keys()) + 1 > (
                        playerscr_y - player_y
                    ):
                        player_y = 2
                        if player_x <= second_third:
                            player_x += first_third
                        else:
                            # We're out of screen space
                            break
                    playerscr.addstr(
                        player_y, player_x, player.title() + ":", curses.color_pair(3)
                    )
                    player_y += 1
                    for stat in encounter_report["participants"][player].keys():
                        playerscr.addstr(
                            player_y,
                            player_x + 2,
                            stat[:first_quarter].title().replace("_", " "),
                            curses.color_pair(5),
                        )
                        if "dps" in stat or "activity" in stat:
                            value = str(
                                format(
                                    float(
                                        encounter_report["participants"][player][stat]
                                    ),
                                    ".2f",
                                )
                            )
                        else:
                            value = str(encounter_report["participants"][player][stat])
                        playerscr.addstr(
                            player_y,
                            player_x + 22,
                            value[:first_quarter].title().replace("_", " "),
                            curses.color_pair(1),
                        )
                        player_y += 1
                    if player_y > (int(y / 2) - 10):
                        player_y = 2
                        if player_x <= second_third:
                            player_x += first_third
                        else:
                            # We're out of screen space
                            break
                    else:
                        player_y += 1
            else:
                draw_mascot_message(encounterscr, "No encounter parse yet")
        else:
            draw_mascot_message(encounterscr, "Encounter parsing disabled")

    except Exception as e:
        eqa_settings.log(
            "draw parse: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def draw_state(stdscr, state, version):
    """Draw state"""
    y, x = stdscr.getmaxyx()
    center_y = int(y / 2)
    center_x = int(x / 2)

    # Clear and box
    stdscr.clear()
    stdscr.box()

    # Draw tabs
    draw_tabs(stdscr, "state", version)

    # Show some state
    try:
        # server state
        stdscr.addstr(5, 5, "Server", curses.color_pair(2))
        stdscr.addstr(5, 16, ": ", curses.color_pair(1))
        stdscr.addstr(5, 18, state.server.title(), curses.color_pair(3))

        # char
        stdscr.addstr(6, 5, "Character", curses.color_pair(2))
        stdscr.addstr(6, 16, ": ", curses.color_pair(1))
        stdscr.addstr(6, 18, state.char.title(), curses.color_pair(3))

        # class
        stdscr.addstr(8, 5, "Class", curses.color_pair(2))
        stdscr.addstr(8, 16, ": ", curses.color_pair(1))
        if state.char_class is not None:
            stdscr.addstr(8, 18, state.char_class.title(), curses.color_pair(3))
        else:
            stdscr.addstr(8, 18, "Unavailable", curses.color_pair(3))

        # level
        stdscr.addstr(9, 5, "Level", curses.color_pair(2))
        stdscr.addstr(9, 16, ": ", curses.color_pair(1))
        if state.char_level is not None:
            stdscr.addstr(9, 18, str(state.char_level).title(), curses.color_pair(3))
        else:
            stdscr.addstr(9, 18, "Unavailable", curses.color_pair(3))

        # guild
        stdscr.addstr(10, 5, "Guild", curses.color_pair(2))
        stdscr.addstr(10, 16, ": ", curses.color_pair(1))
        if state.char_guild is not None:
            stdscr.addstr(10, 18, state.char_guild.title(), curses.color_pair(3))
        else:
            stdscr.addstr(10, 18, "Unavailable", curses.color_pair(3))

        # bind state
        stdscr.addstr(12, 5, "Bind", curses.color_pair(2))
        stdscr.addstr(12, 16, ": ", curses.color_pair(1))
        if state.bind is not None:
            stdscr.addstr(12, 18, state.bind.title(), curses.color_pair(3))
        else:
            stdscr.addstr(12, 18, "Unavailable", curses.color_pair(3))

        # encumbered state
        stdscr.addstr(13, 5, "Encumbered", curses.color_pair(2))
        stdscr.addstr(13, 16, ": ", curses.color_pair(1))
        stdscr.addstr(13, 18, str(state.encumbered), curses.color_pair(3))

        # afk state
        stdscr.addstr(14, 5, "AFK", curses.color_pair(2))
        stdscr.addstr(14, 16, ": ", curses.color_pair(1))
        stdscr.addstr(14, 18, str(state.afk), curses.color_pair(3))

        # group state
        stdscr.addstr(16, 5, "Group", curses.color_pair(2))
        stdscr.addstr(16, 16, ": ", curses.color_pair(1))
        stdscr.addstr(16, 18, str(state.group), curses.color_pair(3))

        # leader state
        if state.group:
            stdscr.addstr(16, 25, "Leader", curses.color_pair(2))
            stdscr.addstr(16, 32, ": ", curses.color_pair(1))
            stdscr.addstr(16, 34, str(state.leader), curses.color_pair(3))

        # raid state
        stdscr.addstr(17, 5, "Raid", curses.color_pair(2))
        stdscr.addstr(17, 16, ": ", curses.color_pair(1))
        stdscr.addstr(17, 18, str(state.raid), curses.color_pair(3))

        # zone
        stdscr.addstr(19, 5, "Zone", curses.color_pair(2))
        stdscr.addstr(19, 16, ": ", curses.color_pair(1))
        if state.zone is not None:
            stdscr.addstr(19, 18, state.zone.title(), curses.color_pair(3))
        else:
            stdscr.addstr(19, 18, "Unavailable", curses.color_pair(3))

        # loc
        stdscr.addstr(20, 5, "Location", curses.color_pair(2))
        stdscr.addstr(20, 16, ": ", curses.color_pair(1))
        stdscr.addstr(20, 18, str(state.loc[0]), curses.color_pair(3))
        stdscr.addstr(20, 24, " : ", curses.color_pair(2))
        stdscr.addstr(20, 26, str(state.loc[1]), curses.color_pair(3))
        stdscr.addstr(20, 32, " : ", curses.color_pair(2))
        stdscr.addstr(20, 34, str(state.loc[2]), curses.color_pair(3))

        # direction
        stdscr.addstr(21, 5, "Direction", curses.color_pair(2))
        stdscr.addstr(21, 16, ": ", curses.color_pair(1))
        if state.direction is not None:
            stdscr.addstr(21, 18, state.direction.title(), curses.color_pair(3))
        else:
            stdscr.addstr(21, 18, "Unavailable", curses.color_pair(3))

        # debug state
        stdscr.addstr(23, 5, "Debug", curses.color_pair(2))
        stdscr.addstr(23, 16, ": ", curses.color_pair(1))
        stdscr.addstr(23, 18, str(state.debug), curses.color_pair(3))

        # mute state
        stdscr.addstr(24, 5, "Mute", curses.color_pair(2))
        stdscr.addstr(24, 16, ": ", curses.color_pair(1))
        stdscr.addstr(24, 18, str(state.mute), curses.color_pair(3))

        # encounter parse state
        stdscr.addstr(25, 5, "Encounter", curses.color_pair(2))
        stdscr.addstr(25, 16, ": ", curses.color_pair(1))
        stdscr.addstr(25, 18, str(state.encounter_parse), curses.color_pair(3))

        # consider evaluation state
        stdscr.addstr(26, 5, "Consider", curses.color_pair(2))
        stdscr.addstr(26, 16, ": ", curses.color_pair(1))
        stdscr.addstr(26, 18, str(state.consider_eval), curses.color_pair(3))

    except Exception as e:
        eqa_settings.log(
            "draw state: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def draw_settings(stdscr, state, configs, s_setting, s_char, s_opt, s_line, version):
    """Draw settings"""

    try:
        # Clear and box
        stdscr.clear()
        stdscr.box()
        y, x = stdscr.getmaxyx()

        # Draw tabs
        draw_tabs(stdscr, "settings", version)

        # Char Select Window
        charscr = stdscr.derwin(int(y / 2) - 4, int(x / 2) - 4, 4, 4)
        char_y, char_x = charscr.getmaxyx()
        charscr.box()

        ## Char Select Title
        charscr.addch(0, int(char_x / 2) - 10, curses.ACS_RTEE)
        if s_setting == "character":
            charscr.addstr(
                0, int(char_x / 2) - 9, " Character Select ", curses.color_pair(4)
            )
        else:
            charscr.addstr(
                0, int(char_x / 2) - 9, " Character Select ", curses.color_pair(2)
            )
        charscr.addch(0, int(char_x / 2) + 9, curses.ACS_LTEE)

        ## Draw Char Select
        draw_settings_char_select(charscr, configs, state, s_char, s_setting)

        # Options Window
        optscr = stdscr.derwin(int(y / 2) - 4, int(x / 2) - 4, int(y / 2) + 2, 4)
        opt_y, opt_x = optscr.getmaxyx()
        optscr.box()

        ## Options Title
        optscr.addch(0, int(opt_x / 2) - 6, curses.ACS_RTEE)
        if s_setting == "option":
            optscr.addstr(0, int(opt_x / 2) - 5, " Options ", curses.color_pair(4))
        else:
            optscr.addstr(0, int(opt_x / 2) - 5, " Options ", curses.color_pair(2))
        optscr.addch(0, int(opt_x / 2) + 4, curses.ACS_LTEE)

        ## Options
        draw_settings_options(optscr, configs, state, s_opt, s_setting)

        # Line Type
        linescr = stdscr.derwin(y - 6, int(x / 2) - 6, 4, int(x / 2) + 2)
        line_y, line_x = linescr.getmaxyx()
        linescr.box()

        ## Line Type Editor Title
        linescr.addch(0, int(line_x / 2) - 8, curses.ACS_RTEE)
        if s_setting == "line":
            linescr.addstr(
                0, int(line_x / 2) - 7, " Alert Config ", curses.color_pair(4)
            )
        else:
            linescr.addstr(
                0, int(line_x / 2) - 7, " Alert Config ", curses.color_pair(2)
            )
        linescr.addch(0, int(line_x / 2) + 7, curses.ACS_LTEE)

        ## Draw Line Type Editor
        draw_settings_line_editor(linescr, configs, state, s_line, s_setting)

    except Exception as e:
        eqa_settings.log(
            "draw settings: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def draw_settings_char_select(charscr, configs, state, s_char, s_setting):
    """Draw settings character selection window"""

    try:
        char_y, char_x = charscr.getmaxyx()
        char_name, char_server = state.chars[s_char].split("_")
        first_q = int(char_x / 5)
        second_third = int((char_x / 3) * 2)

        # Active Character
        charscr.addstr(2, first_q - 5, "Active:", curses.color_pair(1))
        charscr.addstr(2, first_q + 3, state.char.title(), curses.color_pair(5))
        charscr.addstr(2, first_q + 4 + len(state.char), "on", curses.color_pair(1))
        charscr.addstr(
            2, first_q + 7 + len(state.char), state.server.title(), curses.color_pair(5)
        )

        # Character Select
        charscr.addstr(6, first_q - 5, "Select:", curses.color_pair(1))
        if s_setting == "character":
            charscr.addstr(6, first_q + 3, char_name.title(), curses.color_pair(4))
            charscr.addstr(6, first_q + 4 + len(char_name), "on", curses.color_pair(1))
            charscr.addstr(
                6,
                first_q + 7 + len(char_name),
                char_server.title(),
                curses.color_pair(4),
            )
        else:
            charscr.addstr(6, first_q + 3, char_name.title(), curses.color_pair(3))
            charscr.addstr(6, first_q + 4 + len(char_name), "on", curses.color_pair(1))
            charscr.addstr(
                6,
                first_q + 7 + len(char_name),
                char_server.title(),
                curses.color_pair(3),
            )

        # Character Select Arrows
        if s_char == 0:
            charscr.addch(5, first_q + 3, curses.ACS_UARROW, curses.color_pair(2))
        elif s_char == len(state.chars) - 1:
            charscr.addch(7, first_q + 3, curses.ACS_DARROW, curses.color_pair(2))
        else:
            charscr.addch(5, first_q + 3, curses.ACS_UARROW, curses.color_pair(2))
            charscr.addch(7, first_q + 3, curses.ACS_DARROW, curses.color_pair(2))

        # Character Select Stats
        charscr.addstr(10, first_q, "Class:", curses.color_pair(1))
        selected_char_class = configs.characters.config["char_logs"][
            state.chars[s_char]
        ]["char_state"]["class"]
        if selected_char_class is not None:
            message = selected_char_class.title()
        else:
            message = "Unavailable"
        charscr.addstr(
            10,
            first_q + 7,
            message,
            curses.color_pair(3),
        )
        charscr.addstr(11, first_q, "Level:", curses.color_pair(1))
        selected_char_level = configs.characters.config["char_logs"][
            state.chars[s_char]
        ]["char_state"]["level"]
        if selected_char_level is not None:
            message = str(selected_char_level)
        else:
            message = "Unavailable"
        charscr.addstr(
            11,
            first_q + 7,
            message,
            curses.color_pair(3),
        )
        charscr.addstr(12, first_q, "Guild:", curses.color_pair(1))
        selected_char_guild = configs.characters.config["char_logs"][
            state.chars[s_char]
        ]["char_state"]["guild"]
        if selected_char_guild is not None:
            message = selected_char_guild.title()
        else:
            message = "Unavailable"
        charscr.addstr(
            12,
            first_q + 7,
            message,
            curses.color_pair(3),
        )
        charscr.addstr(13, first_q, "Zone:", curses.color_pair(1))
        selected_char_zone = configs.characters.config["char_logs"][
            state.chars[s_char]
        ]["char_state"]["zone"]
        if selected_char_zone is not None:
            message = selected_char_zone.title()
        else:
            message = "Unavailable"
        charscr.addstr(
            13,
            first_q + 7,
            message,
            curses.color_pair(3),
        )
        charscr.addstr(14, first_q, "Bind:", curses.color_pair(1))
        selected_char_bind = configs.characters.config["char_logs"][
            state.chars[s_char]
        ]["char_state"]["bind"]
        if selected_char_bind is not None:
            message = selected_char_bind.title()
        else:
            message = "Unavailable"
        charscr.addstr(
            14,
            first_q + 7,
            message,
            curses.color_pair(3),
        )

    except Exception as e:
        eqa_settings.log(
            "draw settings char select: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def draw_settings_options(optscr, configs, state, s_option, s_setting):
    """Draw settings options window"""

    try:
        opy_y, opt_x = optscr.getmaxyx()
        first_q = int(opt_x / 5)
        second_third = int((opt_x / 3) * 2)

        # Debug
        if s_option == "debug" and s_setting == "option":
            optscr.addstr(5, first_q - 1, "Debug Mode", curses.color_pair(4))
            optscr.addstr(
                2,
                first_q - 2,
                "Log and display all parser output",
                curses.color_pair(3),
            )
        else:
            optscr.addstr(5, first_q, "Debug Mode", curses.color_pair(1))
        optscr.addstr(5, second_third, "[", curses.color_pair(3))
        if state.debug:
            optscr.addstr(5, second_third + 1, "on", curses.color_pair(5))
        else:
            optscr.addstr(5, second_third + 4, "off", curses.color_pair(6))
        optscr.addstr(5, second_third + 7, "]", curses.color_pair(3))

        # Mute
        if s_option == "mute" and s_setting == "option":
            optscr.addstr(6, first_q - 1, "Mute", curses.color_pair(4))
            optscr.addstr(2, first_q - 2, "Mute all audio alerts", curses.color_pair(3))
        else:
            optscr.addstr(6, first_q, "Mute", curses.color_pair(1))
        optscr.addstr(6, second_third, "[", curses.color_pair(3))
        if state.mute:
            optscr.addstr(6, second_third + 1, "on", curses.color_pair(5))
        else:
            optscr.addstr(6, second_third + 4, "off", curses.color_pair(6))
        optscr.addstr(6, second_third + 7, "]", curses.color_pair(3))

        # Raid
        if s_option == "raid" and s_setting == "option":
            optscr.addstr(7, first_q - 1, "Raid Mode", curses.color_pair(4))
            optscr.addstr(
                2, first_q - 2, "Manually toggle raid context", curses.color_pair(3)
            )
        else:
            optscr.addstr(7, first_q, "Raid Mode", curses.color_pair(1))
        optscr.addstr(7, second_third, "[", curses.color_pair(3))
        if state.raid:
            optscr.addstr(7, second_third + 1, "on", curses.color_pair(5))
        else:
            optscr.addstr(7, second_third + 4, "off", curses.color_pair(6))
        optscr.addstr(7, second_third + 7, "]", curses.color_pair(3))

        # Raid Auto
        if s_option == "autoraid" and s_setting == "option":
            optscr.addstr(8, first_q - 1, "Auto-set Raid Mode", curses.color_pair(4))
            optscr.addstr(
                2,
                first_q - 2,
                "Automatically set raid context by zone",
                curses.color_pair(3),
            )
        else:
            optscr.addstr(8, first_q, "Auto-set Raid Mode", curses.color_pair(1))
        optscr.addstr(8, second_third, "[", curses.color_pair(3))
        if state.auto_raid:
            optscr.addstr(8, second_third + 1, "on", curses.color_pair(5))
        else:
            optscr.addstr(8, second_third + 4, "off", curses.color_pair(6))
        optscr.addstr(8, second_third + 7, "]", curses.color_pair(3))

        # Encounter
        if s_option == "encounter" and s_setting == "option":
            optscr.addstr(9, first_q - 1, "Encounter Parse", curses.color_pair(4))
            optscr.addstr(
                2,
                first_q - 2,
                "Automatically parse combat encounters",
                curses.color_pair(3),
            )
        else:
            optscr.addstr(9, first_q, "Encounter Parse", curses.color_pair(1))
        optscr.addstr(9, second_third, "[", curses.color_pair(3))
        if state.encounter_parse:
            optscr.addstr(9, second_third + 1, "on", curses.color_pair(5))
        else:
            optscr.addstr(9, second_third + 4, "off", curses.color_pair(6))
        optscr.addstr(9, second_third + 7, "]", curses.color_pair(3))

        # Encounter Save
        if s_option == "saveencounter" and s_setting == "option":
            optscr.addstr(10, first_q - 1, "Save Encounter Parse", curses.color_pair(4))
            optscr.addstr(
                2,
                first_q - 2,
                "Save combat encounters to a .json file",
                curses.color_pair(3),
            )
        else:
            optscr.addstr(10, first_q, "Save Encounter Parse", curses.color_pair(1))
        optscr.addstr(10, second_third, "[", curses.color_pair(3))
        if state.save_parse:
            optscr.addstr(10, second_third + 1, "on", curses.color_pair(5))
        else:
            optscr.addstr(10, second_third + 4, "off", curses.color_pair(6))
        optscr.addstr(10, second_third + 7, "]", curses.color_pair(3))

        # Default Timer
        if s_option == "defaulttimer" and s_setting == "option":
            optscr.addstr(
                11, first_q - 1, "Auto-set Respawn Timer", curses.color_pair(4)
            )
            optscr.addstr(
                2,
                first_q - 2,
                "Automatically set mob respawn timers",
                curses.color_pair(3),
            )
        else:
            optscr.addstr(11, first_q, "Auto-set Respawn Timer", curses.color_pair(1))
        optscr.addstr(11, second_third, "[", curses.color_pair(3))
        if state.auto_mob_timer:
            optscr.addstr(11, second_third + 1, "on", curses.color_pair(5))
        else:
            optscr.addstr(11, second_third + 4, "off", curses.color_pair(6))
        optscr.addstr(11, second_third + 7, "]", curses.color_pair(3))

        # Consider
        if s_option == "consider" and s_setting == "option":
            optscr.addstr(12, first_q - 1, "Consider Evaluation", curses.color_pair(4))
            optscr.addstr(
                2,
                first_q - 2,
                "Evaluate mob consider output",
                curses.color_pair(3),
            )
        else:
            optscr.addstr(12, first_q, "Consider Evaluation", curses.color_pair(1))
        optscr.addstr(12, second_third, "[", curses.color_pair(3))
        if state.consider_eval:
            optscr.addstr(12, second_third + 1, "on", curses.color_pair(5))
        else:
            optscr.addstr(12, second_third + 4, "off", curses.color_pair(6))
        optscr.addstr(12, second_third + 7, "]", curses.color_pair(3))

        # Detect Character
        if s_option == "detect_char" and s_setting == "option":
            optscr.addstr(
                13, first_q - 1, "Auto-Detect Character", curses.color_pair(4)
            )
            optscr.addstr(
                2,
                first_q - 2,
                "Automatically detect character log",
                curses.color_pair(3),
            )
        else:
            optscr.addstr(13, first_q, "Auto-Detect Character", curses.color_pair(1))
        optscr.addstr(13, second_third, "[", curses.color_pair(3))
        if state.detect_char:
            optscr.addstr(13, second_third + 1, "on", curses.color_pair(5))
        else:
            optscr.addstr(13, second_third + 4, "off", curses.color_pair(6))
        optscr.addstr(13, second_third + 7, "]", curses.color_pair(3))

        # Spell Timer Self
        if s_option == "spell_self" and s_setting == "option":
            optscr.addstr(14, first_q - 1, "Self Spell Timers", curses.color_pair(4))
            optscr.addstr(
                2,
                first_q - 2,
                "Spells targetting you",
                curses.color_pair(3),
            )
        else:
            optscr.addstr(14, first_q, "Self Spell Timers", curses.color_pair(1))
        optscr.addstr(14, second_third, "[", curses.color_pair(3))
        if state.spell_timer_self:
            optscr.addstr(14, second_third + 1, "on", curses.color_pair(5))
        else:
            optscr.addstr(14, second_third + 4, "off", curses.color_pair(6))
        optscr.addstr(14, second_third + 7, "]", curses.color_pair(3))

        # Spell Timer Other
        if s_option == "spell_other" and s_setting == "option":
            optscr.addstr(15, first_q - 1, "Other Spell Timers", curses.color_pair(4))
            optscr.addstr(
                2,
                first_q - 2,
                "Spells targetting others",
                curses.color_pair(3),
            )
        else:
            optscr.addstr(15, first_q, "Other Spell Timers", curses.color_pair(1))
        optscr.addstr(15, second_third, "[", curses.color_pair(3))
        if state.spell_timer_other:
            optscr.addstr(15, second_third + 1, "on", curses.color_pair(5))
        else:
            optscr.addstr(15, second_third + 4, "off", curses.color_pair(6))
        optscr.addstr(15, second_third + 7, "]", curses.color_pair(3))

        # Spell Timer Guild Only
        if s_option == "spell_guild" and s_setting == "option":
            optscr.addstr(16, first_q - 1, "Guild Timer Filter", curses.color_pair(4))
            optscr.addstr(
                2,
                first_q - 2,
                "Filter for spells on guildies",
                curses.color_pair(3),
            )
        else:
            optscr.addstr(16, first_q, "Guild Timer Filter", curses.color_pair(1))
        optscr.addstr(16, second_third, "[", curses.color_pair(3))
        if state.spell_timer_guild_only:
            optscr.addstr(16, second_third + 1, "on", curses.color_pair(5))
        else:
            optscr.addstr(16, second_third + 4, "off", curses.color_pair(6))
        optscr.addstr(16, second_third + 7, "]", curses.color_pair(3))

        # Spell Timer Guessing
        if s_option == "spell_guess" and s_setting == "option":
            optscr.addstr(17, first_q - 1, "Guess Spells", curses.color_pair(4))
            optscr.addstr(
                2,
                first_q - 2,
                "Make a guess instead of nothing",
                curses.color_pair(3),
            )
        else:
            optscr.addstr(17, first_q, "Guess Spells", curses.color_pair(1))
        optscr.addstr(17, second_third, "[", curses.color_pair(3))
        if state.spell_timer_guess:
            optscr.addstr(17, second_third + 1, "on", curses.color_pair(5))
        else:
            optscr.addstr(17, second_third + 4, "off", curses.color_pair(6))
        optscr.addstr(17, second_third + 7, "]", curses.color_pair(3))

        # Spell Timer Yours Only
        if s_option == "spell_yours" and s_setting == "option":
            optscr.addstr(18, first_q - 1, "Your Timer Filter", curses.color_pair(4))
            optscr.addstr(
                2,
                first_q - 2,
                "Filter for only your spells",
                curses.color_pair(3),
            )
        else:
            optscr.addstr(18, first_q, "Your Timer Filter", curses.color_pair(1))
        optscr.addstr(18, second_third, "[", curses.color_pair(3))
        if state.spell_timer_yours_only:
            optscr.addstr(18, second_third + 1, "on", curses.color_pair(5))
        else:
            optscr.addstr(18, second_third + 4, "off", curses.color_pair(6))
        optscr.addstr(18, second_third + 7, "]", curses.color_pair(3))

    except Exception as e:
        eqa_settings.log(
            "draw settings options: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def draw_settings_line_editor(linescr, configs, state, s_line, s_setting):
    """Draw settings alert config editor window"""

    try:
        line_y, line_x = linescr.getmaxyx()
        first_q = int(line_x / 5)
        last_q = int((line_x / 5) * 4)
        config_line_type = list(configs.alerts.config["line"].keys())[s_line]

        # Description
        if s_setting == "line":
            linescr.addstr(
                line_y - 3,
                int(line_x / 2) - 15,
                "Edit config/line-alerts/ to modify",
                curses.color_pair(3),
            )

        # Line Type Selection
        linescr.addstr(4, first_q - 5, "Line Type:", curses.color_pair(1))
        if s_setting == "line":
            linescr.addstr(4, first_q + 6, config_line_type, curses.color_pair(4))
        else:
            linescr.addstr(4, first_q + 6, config_line_type, curses.color_pair(3))

        # Line Type Selection Arrows
        if s_line == 0:
            linescr.addch(3, first_q + 6, curses.ACS_UARROW, curses.color_pair(2))
        elif s_line == len(configs.alerts.config["line"].keys()) - 1:
            linescr.addch(5, first_q + 6, curses.ACS_DARROW, curses.color_pair(2))
        else:
            linescr.addch(3, first_q + 6, curses.ACS_UARROW, curses.color_pair(2))
            linescr.addch(5, first_q + 6, curses.ACS_DARROW, curses.color_pair(2))

        # View Line Type Reaction
        linescr.addstr(7, first_q - 1, "Reaction:", curses.color_pair(1))
        linescr.addstr(
            7,
            first_q + 10,
            str(configs.alerts.config["line"][config_line_type]["reaction"]).title(),
            curses.color_pair(3),
        )

        # View Line Type Sound
        linescr.addstr(9, first_q - 1, "Sound:", curses.color_pair(1))
        linescr.addstr(
            9,
            first_q + 10,
            str(configs.alerts.config["line"][config_line_type]["sound"]).title(),
            curses.color_pair(3),
        )

        # View Line Type Alerts
        linescr.addstr(11, first_q - 1, "Alerts:", curses.color_pair(1))
        alert_num = len(configs.alerts.config["line"][config_line_type]["alert"].keys())
        if alert_num == 0:
            linescr.addstr(11, first_q + 10, "None", curses.color_pair(3))
        else:
            count = 12
            for key in configs.alerts.config["line"][config_line_type]["alert"].keys():
                linescr.addstr(count, first_q, key, curses.color_pair(2))
                linescr.addstr(
                    count,
                    last_q,
                    configs.alerts.config["line"][config_line_type]["alert"][
                        key
                    ].title(),
                    curses.color_pair(3),
                )
                if count >= line_y - 3:
                    break
                else:
                    count += 1

    except Exception as e:
        eqa_settings.log(
            "draw settings alert config editor: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def draw_mascot_message(scr, message):
    """Draw settings options window"""

    try:
        win_y, win_x = scr.getmaxyx()
        mid_win_y = int(win_y / 2)
        mid_win_x = int(win_x / 2)
        first_quarter_x = int(win_x / 4)
        first_quarter_y = int(win_y / 4)

        scr.addstr(
            first_quarter_y,
            first_quarter_x,
            "   (\\{\\",
            curses.color_pair(1),
        )
        scr.addstr(
            first_quarter_y,
            first_quarter_x + 7,
            "              *",
            curses.color_pair(3),
        )
        scr.addstr(
            first_quarter_y + 1,
            first_quarter_x,
            "   { { \\",
            curses.color_pair(1),
        )
        scr.addstr(
            first_quarter_y + 1,
            first_quarter_x + 9,
            ",~,",
            curses.color_pair(5),
        )
        scr.addstr(
            first_quarter_y + 1,
            first_quarter_x + 12,
            "   * *",
            curses.color_pair(3),
        )
        scr.addstr(
            first_quarter_y + 2,
            first_quarter_x,
            "  { {   \\",
            curses.color_pair(1),
        )
        scr.addstr(
            first_quarter_y + 2,
            first_quarter_x + 9,
            ")))",
            curses.color_pair(5),
        )
        scr.addstr(
            first_quarter_y + 2,
            first_quarter_x + 12,
            "  **",
            curses.color_pair(3),
        )
        scr.addstr(
            first_quarter_y + 3, first_quarter_x + 20, message, curses.color_pair(4)
        )
        scr.addstr(first_quarter_y + 3, first_quarter_x, "   { {", curses.color_pair(1))
        scr.addstr(
            first_quarter_y + 3, first_quarter_x + 8, "(((", curses.color_pair(5)
        )
        scr.addstr(first_quarter_y + 3, first_quarter_x + 13, "/", curses.color_pair(2))
        scr.addstr(
            first_quarter_y + 4, first_quarter_x, "    {/{/", curses.color_pair(1)
        )
        scr.addstr(
            first_quarter_y + 4, first_quarter_x + 8, "; ,\\", curses.color_pair(5)
        )
        scr.addstr(first_quarter_y + 4, first_quarter_x + 12, "/", curses.color_pair(2))
        scr.addstr(
            first_quarter_y + 5, first_quarter_x, "       (( '", curses.color_pair(5)
        )
        scr.addstr(
            first_quarter_y + 6, first_quarter_x, "        \\` \\", curses.color_pair(5)
        )
        scr.addstr(
            first_quarter_y + 7, first_quarter_x, "        (/  \\", curses.color_pair(5)
        )
        scr.addstr(
            first_quarter_y + 8,
            first_quarter_x,
            "        `)  `\\",
            curses.color_pair(5),
        )

    except Exception as e:
        eqa_settings.log(
            "draw settings options: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def draw_timers(stdscr, timers):
    """Draw timers pop up"""

    try:
        y, x = stdscr.getmaxyx()

        timer_scr = stdscr.derwin(
            int(y / 2) + int(y / 4), int(x / 2) + int(x / 4), int(y / 8), int(x / 8)
        )
        timer_scr.clear()
        timer_scr.box()

        timer_y, timer_x = timer_scr.getmaxyx()
        mid_timer_y = int(timer_y / 2)
        mid_timer_x = int(timer_x / 2)

        # Title
        timer_scr.addstr(2, mid_timer_x - 7, "Active Timers", curses.color_pair(2))

        # Ensure there are timers to show
        if timers is not None:
            if len(timers) > 0:
                print_timer_y = 4
                now = datetime.now()
                ## Show timers
                while len(timers) > 0:
                    ### Break if there are more timers than room
                    if print_timer_y > int(timer_y * 0.9):
                        break
                    ### Get timer
                    timer = heapq.heappop(timers)
                    if timer.type == "timer" or timer.type == "spell":
                        ### Duration remaining
                        time_remaining = timer.time - now
                        time_remaining_days = time_remaining.days
                        time_remaining_seconds = time_remaining.seconds
                        timer_hours = (
                            time_remaining_days * 24 + time_remaining_seconds // 3600
                        )
                        timer_minutes = (time_remaining_seconds % 3600) // 60
                        timer_seconds = time_remaining_seconds % 60
                        if timer_minutes < 1 and timer_hours == 0:
                            color = 6
                        elif timer_minutes < 2 and timer_hours == 0:
                            color = 4
                        elif timer_minutes < 5 and timer_hours == 0:
                            color = 2
                        else:
                            color = 5
                        timer_scr.addstr(
                            print_timer_y,
                            5,
                            f"{timer_hours:02}",
                            curses.color_pair(color),
                        )
                        timer_scr.addstr(
                            print_timer_y,
                            5 + len(f"{timer_hours:02}"),
                            ":",
                            curses.color_pair(1),
                        )
                        timer_scr.addstr(
                            print_timer_y,
                            6 + len(f"{timer_hours:02}"),
                            f"{timer_minutes:02}",
                            curses.color_pair(color),
                        )
                        timer_scr.addstr(
                            print_timer_y,
                            8 + len(f"{timer_hours:02}"),
                            ":",
                            curses.color_pair(1),
                        )
                        timer_scr.addstr(
                            print_timer_y,
                            9 + len(f"{timer_hours:02}"),
                            f"{timer_seconds:02}",
                            curses.color_pair(color),
                        )
                        timestamp_len = 11 + len(f"{timer_hours:02}")
                        ### Timer details
                        if timer.type == "spell":
                            timer_scr.addstr(
                                print_timer_y,
                                2 + timestamp_len,
                                timer.caster,
                                curses.color_pair(3),
                            )
                            timer_scr.addch(
                                print_timer_y,
                                2 + timestamp_len + len(timer.caster),
                                curses.ACS_RARROW,
                            )
                            timer_scr.addstr(
                                print_timer_y,
                                4 + timestamp_len + len(timer.caster),
                                timer.target,
                                curses.color_pair(3),
                            )
                            timer_scr.addstr(
                                print_timer_y,
                                6
                                + timestamp_len
                                + len(timer.caster)
                                + len(timer.target),
                                timer.spell.replace("_", " "),
                                curses.color_pair(color),
                            )
                        else:
                            message = timer.payload
                            timer_scr.addstr(
                                print_timer_y,
                                2 + timestamp_len,
                                message,
                                curses.color_pair(3),
                            )
                        print_timer_y = print_timer_y + 1
            else:
                draw_mascot_message(timer_scr, "No active timers")
        else:
            draw_mascot_message(timer_scr, "No active timers")

    except Exception as e:
        eqa_settings.log(
            "draw timers: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def draw_help(stdscr):
    """Draw help"""

    try:
        y, x = stdscr.getmaxyx()

        helpscr = stdscr.derwin(
            int(y / 2) + int(y / 4), int(x / 2) + int(x / 4), int(y / 8), int(x / 8)
        )
        helpscr.clear()
        helpscr.box()

        help_y, help_x = helpscr.getmaxyx()
        mid_help_y = int(help_y / 2)
        mid_help_x = int(help_x / 2)

        # Title
        helpscr.addstr(2, mid_help_x - 9, "EQ Alert Help Menu", curses.color_pair(2))

        # Commands
        helpscr.addstr(5, 5, "Keyboard Controls:", curses.color_pair(1))

        # Global commands
        helpscr.addstr(7, 7, "Global", curses.color_pair(1))

        helpscr.addstr(8, 9, "0", curses.color_pair(2))
        helpscr.addstr(8, 15, ":", curses.color_pair(1))
        helpscr.addstr(8, 17, "Reload config", curses.color_pair(3))

        helpscr.addstr(9, 9, "1", curses.color_pair(2))
        helpscr.addstr(9, 15, ":", curses.color_pair(1))
        helpscr.addstr(9, 17, "Events", curses.color_pair(3))

        helpscr.addstr(10, 9, "2", curses.color_pair(2))
        helpscr.addstr(10, 15, ":", curses.color_pair(1))
        helpscr.addstr(10, 17, "State", curses.color_pair(3))

        helpscr.addstr(11, 9, "3", curses.color_pair(2))
        helpscr.addstr(11, 15, ":", curses.color_pair(1))
        helpscr.addstr(11, 17, "Parse", curses.color_pair(3))

        helpscr.addstr(12, 9, "4", curses.color_pair(2))
        helpscr.addstr(12, 15, ":", curses.color_pair(1))
        helpscr.addstr(12, 17, "Settings", curses.color_pair(3))

        helpscr.addstr(13, 9, "q", curses.color_pair(2))
        helpscr.addstr(13, 15, ":", curses.color_pair(1))
        helpscr.addstr(13, 17, "Quit", curses.color_pair(3))

        helpscr.addstr(14, 9, "h", curses.color_pair(2))
        helpscr.addstr(14, 15, ":", curses.color_pair(1))
        helpscr.addstr(14, 17, "Help", curses.color_pair(3))

        helpscr.addstr(15, 9, "t", curses.color_pair(2))
        helpscr.addstr(15, 15, ":", curses.color_pair(1))
        helpscr.addstr(15, 17, "Timers", curses.color_pair(3))

        # Events commands
        helpscr.addstr(17, 7, "Events", curses.color_pair(1))

        helpscr.addstr(18, 9, "c", curses.color_pair(2))
        helpscr.addstr(18, 15, ":", curses.color_pair(1))
        helpscr.addstr(18, 17, "Clear events", curses.color_pair(3))

        helpscr.addstr(19, 9, "d", curses.color_pair(2))
        helpscr.addstr(19, 15, ":", curses.color_pair(1))
        helpscr.addstr(19, 17, "Toggle debug mode", curses.color_pair(3))

        helpscr.addstr(20, 9, "e", curses.color_pair(2))
        helpscr.addstr(20, 15, ":", curses.color_pair(1))
        helpscr.addstr(20, 17, "Toggle encounter parsing", curses.color_pair(3))

        helpscr.addstr(21, 9, "m", curses.color_pair(2))
        helpscr.addstr(21, 15, ":", curses.color_pair(1))
        helpscr.addstr(21, 17, "Toggle mute", curses.color_pair(3))

        helpscr.addstr(22, 9, "p", curses.color_pair(2))
        helpscr.addstr(22, 15, ":", curses.color_pair(1))
        helpscr.addstr(22, 17, "Toggle encounter parse save", curses.color_pair(3))

        helpscr.addstr(23, 9, "r", curses.color_pair(2))
        helpscr.addstr(23, 15, ":", curses.color_pair(1))
        helpscr.addstr(23, 17, "Toggle raid mode", curses.color_pair(3))

        helpscr.addstr(24, 9, "y", curses.color_pair(2))
        helpscr.addstr(24, 15, ":", curses.color_pair(1))
        helpscr.addstr(
            24, 17, "Toggle automatic mob respawn timers", curses.color_pair(3)
        )

        # Settings commands
        helpscr.addstr(26, 7, "Settings", curses.color_pair(1))

        helpscr.addstr(27, 9, "up", curses.color_pair(2))
        helpscr.addstr(27, 15, ":", curses.color_pair(1))
        helpscr.addstr(27, 17, "Up in selection", curses.color_pair(3))

        helpscr.addstr(28, 9, "down", curses.color_pair(2))
        helpscr.addstr(28, 15, ":", curses.color_pair(1))
        helpscr.addstr(28, 17, "Down in selection", curses.color_pair(3))

        helpscr.addstr(29, 9, "right", curses.color_pair(2))
        helpscr.addstr(29, 15, ":", curses.color_pair(1))
        helpscr.addstr(29, 17, "Selection options", curses.color_pair(3))

        helpscr.addstr(30, 9, "left", curses.color_pair(2))
        helpscr.addstr(30, 15, ":", curses.color_pair(1))
        helpscr.addstr(30, 17, "Selection options", curses.color_pair(3))

        helpscr.addstr(31, 9, "space", curses.color_pair(2))
        helpscr.addstr(31, 15, ":", curses.color_pair(1))
        helpscr.addstr(31, 17, "Select", curses.color_pair(3))

        helpscr.addstr(32, 9, "enter", curses.color_pair(2))
        helpscr.addstr(32, 15, ":", curses.color_pair(1))
        helpscr.addstr(32, 17, "Select", curses.color_pair(3))

        helpscr.addstr(33, 9, "tab", curses.color_pair(2))
        helpscr.addstr(33, 15, ":", curses.color_pair(1))
        helpscr.addstr(33, 17, "Cycle category", curses.color_pair(3))

    except Exception as e:
        eqa_settings.log(
            "draw help: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def draw_toosmall(stdscr):
    """Draw too small warning"""

    try:
        stdscr.clear()
        stdscr.box()
        y, x = stdscr.getmaxyx()
        center_y = int(y / 2)
        center_x = int(x / 2)

        stdscr.addstr(
            center_y, center_x - 9, "Terminal too small", curses.color_pair(1)
        )

    except Exception as e:
        eqa_settings.log(
            "draw too small: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


if __name__ == "__main__":
    print("Test Here")
