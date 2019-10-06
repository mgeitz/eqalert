#! /usr/bin/env python

"""
   Program:   EQ Alert
   File Name: eqa_curses.py
   Copyright (C) 2019 Michael Geitz

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
import os
import time
import sys

import lib.eqa_struct as eqa_struct
import lib.eqa_state as eqa_state
import lib.eqa_settings as eqa_settings

def display(stdscr, display_q, state, raid, exit_flag):
  """
    Process: display_q
    Produce: display event
  """
  events = []
  page = 'events'
  setting = 'character'
  selected_char = 0

  try:
    while not exit_flag.is_set():
      time.sleep(0.001)
      if not display_q.empty():
        display_event = display_q.get()
        display_q.task_done()

        # Display Var Update
        if display_event.type == 'update':
          if display_event.screen == 'setting':
            setting = display_event.payload
            draw_page(stdscr, page, events, state, setting, selected_char, raid)
          elif display_event.screen == 'selected_char':
            selected_char = display_event.payload
            draw_page(stdscr, page, events, state, setting, selected_char, raid)
          elif display_event.screen == 'select_char':
            selected_char = display_event.payload
            state.char = state.chars[selected_char]
            draw_page(stdscr, page, events, state, setting, selected_char, raid)
          elif display_event.screen == 'zone':
            zone = display_event.payload
            draw_page(stdscr, page, events, state, setting, selected_char, raid)
          elif display_event.screen == 'char':
            state.char = display_event.payload
            draw_page(stdscr, page, events, state, setting, selected_char, raid)

        # Display Draw
        elif display_event.type == 'draw':
          if display_event.screen != 'redraw':
            page = display_event.screen
          draw_page(stdscr, page, events, state, setting, selected_char, raid)

        # Draw Update
        elif display_event.type == 'event':
          if display_event.screen == 'events':
            events.append(display_event)
            if page == 'events':
              draw_page(stdscr, page, events, state, setting, selected_char, raid)
          elif display_event.screen == 'clear':
            events = []
            draw_page(stdscr, page, events, state, setting, selected_char, raid)



  except Exception as e:
    eqa_settings.log('display: Error on line ' +
                      str(sys.exc_info()[-1].tb_lineno) + ': ' + str(e))

  sys.exit()


def draw_page(stdscr, page, events, state, setting, selected_char, raid):
  y, x = stdscr.getmaxyx()
  try:
    if x >= 80 and y >= 40:
      if page == 'events':
        draw_events_frame(stdscr, state.char, state.zone, events)
      elif page == 'state':
        draw_state(stdscr, state, raid)
      elif page == 'settings':
        draw_settings(stdscr, state.chars, state.char, setting, selected_char)
      elif page == 'help':
        draw_help(stdscr)
    else:
      draw_toosmall(stdscr)
  except Exception as e:
    eqa_settings.log('draw_page: Error on line ' +
                      str(sys.exc_info()[-1].tb_lineno) + ': ' + str(e))


def init(state):
  """Create new stdscr in terminal"""
  stdscr = curses.initscr()
  os.system('setterm -cursor off')
  curses.start_color()
  curses.use_default_colors()
  curses.noecho()
  curses.cbreak()
  stdscr.keypad(1)
  stdscr.timeout(100)
  curses.init_pair(1, curses.COLOR_WHITE, -1)     # Title
  curses.init_pair(2, curses.COLOR_YELLOW, -1)    # Header
  curses.init_pair(3, curses.COLOR_CYAN, -1)      # Subtext
  curses.init_pair(4, curses.COLOR_MAGENTA, -1)   # Highlight
  curses.init_pair(5, curses.COLOR_GREEN, -1)     # Dunno
  draw_events_frame(stdscr, state.char, state.zone, [])
  return stdscr


def close_screens(stdscr):
  """Terminate stdscr"""
  os.system('setterm -cursor on')
  curses.nocbreak()
  stdscr.keypad(0)
  curses.echo()
  curses.endwin()

def draw_tabs(stdscr, tab):
  """Draw the tabs, duh"""
  y, x = stdscr.getmaxyx()
  center_y = int(y / 2)
  center_x = int(x / 2)

  # Bottom of tabs
  stdscr.addch(2, 0, curses.ACS_LTEE)
  stdscr.addch(2, x - 1, curses.ACS_RTEE)
  for c in range (x - 2):
    stdscr.addch(2, c + 1, curses.ACS_HLINE)

# Events tab
  stdscr.addstr(1, 2, "F1", curses.color_pair(3))
  stdscr.addstr(1, 4, ":", curses.color_pair(1))
  if tab == 'events':
    stdscr.addstr(1, 6, "events", curses.color_pair(4))
  else:
    stdscr.addstr(1, 6, "events", curses.color_pair(2))
  stdscr.addch(0, 13, curses.ACS_TTEE)
  stdscr.addch(1, 13, curses.ACS_VLINE)
  stdscr.addch(2, 13, curses.ACS_BTEE)

  # State tab
  stdscr.addstr(1, 15, "F2", curses.color_pair(3))
  stdscr.addstr(1, 17, ":", curses.color_pair(1))
  if tab == 'state':
    stdscr.addstr(1, 19, "state", curses.color_pair(4))
  else:
    stdscr.addstr(1, 19, "state", curses.color_pair(2))
  stdscr.addch(0, 25, curses.ACS_TTEE)
  stdscr.addch(1, 25, curses.ACS_VLINE)
  stdscr.addch(2, 25, curses.ACS_BTEE)

  # Settings tab
  stdscr.addstr(1, x - 25, "F3", curses.color_pair(3))
  stdscr.addstr(1, x - 23, ":", curses.color_pair(1))
  if tab == 'settings':
    stdscr.addstr(1, x - 21, "settings", curses.color_pair(4))
  else:
    stdscr.addstr(1, x - 21, "settings", curses.color_pair(2))
  stdscr.addch(0, x - 27, curses.ACS_TTEE)
  stdscr.addch(1, x - 27, curses.ACS_VLINE)
  stdscr.addch(2, x - 27, curses.ACS_BTEE)

  # Help tab
  stdscr.addstr(1, x - 10, "F4", curses.color_pair(3))
  stdscr.addstr(1, x - 8, ":", curses.color_pair(1))
  if tab == 'help':
    stdscr.addstr(1, x - 6, "help", curses.color_pair(4))
  else:
    stdscr.addstr(1, x - 6, "help", curses.color_pair(2))
  stdscr.addch(0, x - 12, curses.ACS_TTEE)
  stdscr.addch(1, x - 12, curses.ACS_VLINE)
  stdscr.addch(2, x - 12, curses.ACS_BTEE)

  # Center title
  stdscr.addstr(1, center_x - 4, "EQ ALERT", curses.color_pair(2))


def draw_events_frame(stdscr, char, zone, events):
  """Draw events"""
  y, x = stdscr.getmaxyx()
  center_y = int(y / 2)
  center_x = int(x / 2)

  # Clear and box
  stdscr.clear()
  stdscr.box()

  # Draw tabs
  draw_tabs(stdscr, 'events')

  # Bottom of  events
  stdscr.addch(center_y, 0, curses.ACS_LTEE)
  stdscr.addch(center_y, x - 1, curses.ACS_RTEE)
  for c in range (x - 2):
    stdscr.addch(center_y, c + 1, curses.ACS_HLINE)

  # Character
  stdscr.addstr(center_y + 1, 2, char.title(), curses.color_pair(2))

  # Zone
  stdscr.addstr(center_y + 1, x - len(zone) - 2, zone.title(), curses.color_pair(2))

  # Draw events
  draw_events(stdscr, events)


def draw_events(stdscr, events):
  """Draw events window component of events"""
  y, x = stdscr.getmaxyx()
  center_y = int(y / 2)
  bottom_y = center_y - 4
  top_y = 2

  eventscr = stdscr.derwin(center_y - 3, x - 4, 3, 2)
  eventscr.clear()

  try:
    count = 0
    while count < (bottom_y + 1) and count < len(events):
      event_num = len(events) - count - 1
      event = events[(count * -1) - 1]
      c_y = bottom_y - count
      draw_ftime(eventscr, event.timestamp, c_y)
      eventscr.addch(c_y, 14, curses.ACS_VLINE)
      eventscr.addstr(c_y, 16, str(event.payload), curses.color_pair(1))
      count += 1
  except Exception as e:
      eqa_settings.log('draw events: Error on line ' +
                        str(sys.exc_info()[-1].tb_lineno) + ': '  + str(e))


def draw_ftime(stdscr, timestamp, y):
  """Draw formatted time for events"""
  h, m, second = timestamp.split(":")
  s, ms = second.split('.')

  stdscr.addstr(y, 1, h, curses.color_pair(3))
  stdscr.addstr(y, 3, ':', curses.color_pair(2))
  stdscr.addstr(y, 4, m, curses.color_pair(3))
  stdscr.addstr(y, 6, ':', curses.color_pair(2))
  stdscr.addstr(y, 7, s, curses.color_pair(3))
  stdscr.addstr(y, 9, '.', curses.color_pair(2))
  stdscr.addstr(y, 10, ms, curses.color_pair(3))


def draw_state(stdscr, state, raid):
  """Draw state"""
  y, x = stdscr.getmaxyx()
  center_y = int(y / 2)
  center_x = int(x / 2)

  # Clear and box
  stdscr.clear()
  stdscr.box()

  # Draw tabs
  draw_tabs(stdscr, 'state')

  # Show some state
  try:
    # char
    stdscr.addstr(5, 5, 'Character', curses.color_pair(2))
    stdscr.addstr(5, 16, ': ', curses.color_pair(1))
    stdscr.addstr(5, 18, state.char, curses.color_pair(3))
    # zone
    stdscr.addstr(7, 5, 'Zone', curses.color_pair(2))
    stdscr.addstr(7, 16, ': ', curses.color_pair(1))
    stdscr.addstr(7, 18, state.zone, curses.color_pair(3))
    # loc
    stdscr.addstr(9, 5, 'Location', curses.color_pair(2))
    stdscr.addstr(9, 16, ': ', curses.color_pair(1))
    stdscr.addstr(9, 18, state.loc, curses.color_pair(3))
    # afk state
    stdscr.addstr(11, 5, 'AFK', curses.color_pair(2))
    stdscr.addstr(11, 16, ': ', curses.color_pair(1))
    stdscr.addstr(11, 18, state.afk, curses.color_pair(3))
    # raid state
    stdscr.addstr(13, 5, 'Raid', curses.color_pair(2))
    stdscr.addstr(13, 16, ': ', curses.color_pair(1))
    if not raid.is_set():
      stdscr.addstr(13, 18, 'false', curses.color_pair(3))
    else:
      stdscr.addstr(13, 18, 'true', curses.color_pair(3))
  except Exception as e:
      eqa_settings.log('draw state: Error on line ' +
                        str(sys.exc_info()[-1].tb_lineno) + ': '  + str(e))


def draw_settings(stdscr, chars, char, selected_setting, selected_char):
  """Draw settings"""
  # Clear and box
  stdscr.clear()
  stdscr.box()

  # Draw tabs
  draw_tabs(stdscr, 'settings')

  # Draw chars
  if selected_setting == 'character':
    stdscr.addstr(4, 3, 'Character Selection', curses.A_UNDERLINE | curses.color_pair(2))
  else:
    stdscr.addstr(4, 5, 'Character Selection', curses.color_pair(3))
  stdscr.addstr(14, 5, 'Active Character', curses.color_pair(3))
  stdscr.addstr(14, 21, ':', curses.color_pair(1))
  stdscr.addstr(14, 23, char.title(), curses.color_pair(2))

  draw_chars(stdscr, chars, char, selected_char)


def draw_chars(stdscr, chars, char, selected):
  """Draw character selection component for settings"""
  try:
    y, x = stdscr.getmaxyx()
    charscr_width = int(x / 3)
    charscr_height = 7

    charscr = stdscr.derwin(charscr_height, charscr_width, 5, 3)
    charscr.clear()
    charscr.box()

    count = 0
    if len(chars) < 5:
      while count < len(chars):
        char_name = chars[count]
        if selected == count:
          charscr.addstr(6 - count, 2, char_name.title(), curses.color_pair(1))
        else:
          charscr.addstr(6 - count, 2, char_name.title(), curses.color_pair(2))
        count += 1
    else:
      for count in range(0, 5):
        char_name = chars[(selected - 2 + count) % len(chars)]
        if count == 2:
          charscr.addstr(5 - count, 2, char_name.title(), curses.color_pair(1))
        elif (selected - 2 + count) < len(chars) and (selected - 2 + count) >= 0:
          charscr.addstr(5 - count, 2, char_name.title(), curses.color_pair(2))
        count += 1

  except Exception as e:
      eqa_settings.log('draw chars: Error on line ' +
                       str(sys.exc_info()[-1].tb_lineno) + ': '  + str(e))


def draw_help(stdscr):
  """Draw help"""

  # Clear and box
  stdscr.clear()
  stdscr.box()

  # Draw tabs
  draw_tabs(stdscr, 'help')

  # Commands
  stdscr.addstr(5, 5, "Commands:",curses.color_pair(1))

  # Global commands
  stdscr.addstr(7, 7, "Global",curses.color_pair(1))

  stdscr.addstr(8, 9, "F1", curses.color_pair(2))
  stdscr.addstr(8, 15, ":", curses.color_pair(1))
  stdscr.addstr(8, 17, "Events", curses.color_pair(3))

  stdscr.addstr(9, 9, "F2", curses.color_pair(2))
  stdscr.addstr(9, 15, ":", curses.color_pair(1))
  stdscr.addstr(9, 17, "State", curses.color_pair(3))

  stdscr.addstr(10, 9, "F3", curses.color_pair(2))
  stdscr.addstr(10, 15, ":", curses.color_pair(1))
  stdscr.addstr(10, 17, "Settings", curses.color_pair(3))

  stdscr.addstr(11, 9, "F4", curses.color_pair(2))
  stdscr.addstr(11, 15, ":", curses.color_pair(1))
  stdscr.addstr(11, 17, "Help", curses.color_pair(3))

  stdscr.addstr(12, 9, "q", curses.color_pair(2))
  stdscr.addstr(12, 15, ":", curses.color_pair(1))
  stdscr.addstr(12, 17, "Quit", curses.color_pair(3))

  stdscr.addstr(13, 9, "F12", curses.color_pair(2))
  stdscr.addstr(13, 15, ":", curses.color_pair(1))
  stdscr.addstr(13, 17, "Reload config", curses.color_pair(3))

  # Events commands
  stdscr.addstr(15, 7, "Events",curses.color_pair(1))

  stdscr.addstr(16, 9, "c", curses.color_pair(2))
  stdscr.addstr(16, 15, ":", curses.color_pair(1))
  stdscr.addstr(16, 17, "Clear events", curses.color_pair(3))

  stdscr.addstr(17, 9, "r", curses.color_pair(2))
  stdscr.addstr(17, 15, ":", curses.color_pair(1))
  stdscr.addstr(17, 17, "Toggle raid mode", curses.color_pair(3))

  # Settings commands
  stdscr.addstr(19, 7, "Settings",curses.color_pair(1))

  stdscr.addstr(20, 9, "up", curses.color_pair(2))
  stdscr.addstr(20, 15, ":", curses.color_pair(1))
  stdscr.addstr(20, 17, "Cycle up in selection", curses.color_pair(3))

  stdscr.addstr(21, 9, "down", curses.color_pair(2))
  stdscr.addstr(21, 15, ":", curses.color_pair(1))
  stdscr.addstr(21, 17, "Cycle down in selection", curses.color_pair(3))

  stdscr.addstr(22, 9, "right", curses.color_pair(2))
  stdscr.addstr(22, 15, ":", curses.color_pair(1))
  stdscr.addstr(22, 17, "Toggle selection on", curses.color_pair(3))

  stdscr.addstr(23, 9, "left", curses.color_pair(2))
  stdscr.addstr(23, 15, ":", curses.color_pair(1))
  stdscr.addstr(23, 17, "Toggle selection off", curses.color_pair(3))

  stdscr.addstr(24, 9, "space", curses.color_pair(2))
  stdscr.addstr(24, 15, ":", curses.color_pair(1))
  stdscr.addstr(24, 17, "Cycle selection", curses.color_pair(3))


def draw_toosmall(stdscr):
    """Draw too small warning"""
    stdscr.clear()
    stdscr.box()
    y, x = stdscr.getmaxyx()
    center_y = int(y / 2)
    center_x = int(x / 2)

    stdscr.addstr(center_y, center_x - 10, "Terminal too small.",
        curses.color_pair(1))


if __name__ == '__main__':
  main()
