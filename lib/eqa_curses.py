"""
eqalert curses
"""

import curses
import os
import time

import eqa_struct
import eqa_settings

def display(stdscr, display_q, message_q, zone, char, chars, exit_flag):

  events = []
  page = 'events'

  try:
    while not exit_flag.is_set():
      time.sleep(0.001)
      if not display_q.empty():
        display_event = display_q.get()
        display_q.task_done()

        # Display Var Update
        if display_event.type == 'update':
          if display_event.screen == 'zone':
            zone = display_event.payload
            draw_page(stdscr, page, events, char, zone)
          elif display_event.screen == 'char':
            char = display_event.payload
            draw_page(stdscr, page, events, char, zone)

        # Display Draw
        elif display_event.type == 'draw':
          if display_event.screen != 'redraw':
            page = display_event.screen
          draw_page(stdscr, page, events, char, zone)

        # Draw Update
        elif display_event.type == 'event':
          if display_event.screen == 'events':
            events.append(display_event)
            if page == 'events':
              draw_page(stdscr, page, events, char, zone)
          elif display_event.screen == 'clear':
            events = []
            draw_page(stdscr, page, events, char, zone)



  except Exception as e:
    eqa_settings.log('display: ' + str(e))
    pass


def draw_page(stdscr, page, events, char, zone):
  y, x = stdscr.getmaxyx()
  if x >= 80 and y >= 40:
    if page == 'events':
      draw_events_frame(stdscr, char, zone, events)
    elif page == 'state':
      draw_state(stdscr)
    elif page == 'settings':
      draw_settings(stdscr)
    elif page == 'help':
      draw_help(stdscr)
  else:
    draw_toosmall(stdscr)

def init(char, zone):
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
  draw_events_frame(stdscr, char, zone, [])
  return stdscr


def close_stdscrs(stdscr):
  """Terminate stdscr"""
  os.system('setterm -cursor on')
  curses.nocbreak()
  stdscr.keypad(0)
  curses.echo()
  curses.endwin()

def draw_tabs(stdscr, tab):
  """Draw the tabs, duh"""
  y, x = stdscr.getmaxyx()
  center_y = y / 2
  center_x = x / 2

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
  """Draws the main window and tabs using curses"""
  y, x = stdscr.getmaxyx()
  center_y = y / 2
  center_x = x / 2

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
  stdscr.addstr(center_y + 1, 2, char, curses.color_pair(2))

  # Zone
  stdscr.addstr(center_y + 1, x - len(zone) - 2, zone, curses.color_pair(2))

  # Draw events
  draw_events(stdscr, events)


def draw_ftime(stdscr, timestamp, y):
  h, m, second = timestamp.split(":")
  s, ms = second.split('.')

  stdscr.addstr(y, 1, h, curses.color_pair(3))
  stdscr.addstr(y, 3, ':', curses.color_pair(2))
  stdscr.addstr(y, 4, m, curses.color_pair(3))
  stdscr.addstr(y, 6, ':', curses.color_pair(2))
  stdscr.addstr(y, 7, s, curses.color_pair(3))
  stdscr.addstr(y, 9, '.', curses.color_pair(2))
  stdscr.addstr(y, 10, ms, curses.color_pair(3))


def draw_events(stdscr, events):
  """Draw events"""
  y, x = stdscr.getmaxyx()
  center_y = y / 2
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
      eqa_settings.log('draw events: ' + str(e))


def draw_state(stdscr):
  """Draws the main window and tabs using curses"""
  y, x = stdscr.getmaxyx()
  center_y = y / 2
  center_x = x / 2

  # Clear and box
  stdscr.clear()
  stdscr.box()

  # Draw tabs
  draw_tabs(stdscr, 'state')


def draw_settings(stdscr):
  """Draws the main window and tabs using curses"""
  y, x = stdscr.getmaxyx()
  center_y = y / 2
  center_x = x / 2

  # Clear and box
  stdscr.clear()
  stdscr.box()

  # Draw tabs
  draw_tabs(stdscr, 'settings')


def draw_help(stdscr):
  """Draws help menu."""

  # Clear and box
  stdscr.clear()
  stdscr.box()

  # Draw tabs
  draw_tabs(stdscr, 'help')

  # Commands
  stdscr.addstr(5, 5, "Commands:",curses.color_pair(1))

  # Global commands
  stdscr.addstr(7, 7, "Global:",curses.color_pair(1))

  stdscr.addstr(8, 9, "F1", curses.color_pair(2))
  stdscr.addstr(8, 11, ":", curses.color_pair(1))
  stdscr.addstr(8, 13, "Events", curses.color_pair(3))

  stdscr.addstr(9, 9, "F2", curses.color_pair(2))
  stdscr.addstr(9, 11, ":", curses.color_pair(1))
  stdscr.addstr(9, 13, "State", curses.color_pair(3))

  stdscr.addstr(10, 9, "F3", curses.color_pair(2))
  stdscr.addstr(10, 11, ":", curses.color_pair(1))
  stdscr.addstr(10, 13, "Settings", curses.color_pair(3))

  stdscr.addstr(11, 9, "F4", curses.color_pair(2))
  stdscr.addstr(11, 11, ":", curses.color_pair(1))
  stdscr.addstr(11, 13, "Help", curses.color_pair(3))

  stdscr.addstr(12, 9, "q", curses.color_pair(2))
  stdscr.addstr(12, 11, ":", curses.color_pair(1))
  stdscr.addstr(12, 13, "Quit", curses.color_pair(3))

  # Events commands
  stdscr.addstr(14, 7, "Events:",curses.color_pair(1))

  stdscr.addstr(15, 9, "c", curses.color_pair(2))
  stdscr.addstr(15, 11, ":", curses.color_pair(1))
  stdscr.addstr(15, 13, "Clear events", curses.color_pair(3))

  stdscr.addstr(16, 9, "r", curses.color_pair(2))
  stdscr.addstr(16, 11, ":", curses.color_pair(1))
  stdscr.addstr(16, 13, "Toggle raid mode", curses.color_pair(3))

  # Settings commands
  stdscr.addstr(18, 7, "Settings:",curses.color_pair(1))

  stdscr.addstr(19, 9, "r", curses.color_pair(2))
  stdscr.addstr(19, 11, ":", curses.color_pair(1))
  stdscr.addstr(19, 13, "Toggle raid mode", curses.color_pair(3))


def draw_toosmall(stdscr):
    """Draws stdscr when too small"""
    stdscr.clear()
    stdscr.box()
    y, x = stdscr.getmaxyx()
    center_y = y / 2
    center_x = x / 2

    stdscr.addstr(center_y, center_x - 10, "Terminal too small.",
        curses.color_pair(1))


def draw_char_menu(stdscr, chars):
    """Draws char menu."""
    stdscr.clear()
    stdscr.box()
    y, x = stdscr.getmaxyx()
    center_y = y / 2
    center_x = x / 2

    stdscr.addstr(0, center_x - 6, "|           |",
        curses.color_pair(1))
    stdscr.addstr(0, center_x - 4, "Char Menu",
        curses.color_pair(2))

    stdscr.addstr(1, center_x - x / 2 + 1, "F1 :",
        curses.color_pair(2))
    stdscr.addstr(1, 5 + center_x - x / 2, "  Console",
        curses.color_pair(3))

    count = 0
    for toon in chars:
        stdscr.addstr(6 + count + 1, center_x - x / 3, str(count + 1) + ":",
            curses.color_pair(1))
        stdscr.addstr(6 + count + 1, center_x - x / 3 + 17, str(toon).title(),
            curses.color_pair(2))
        count = count + 1


def char_menu(stdscr, chars):
  """Controls char menu commands."""
  key = ''
  new_char = char

  draw_char_menu(stdscr, chars)

  selected = False
  while key != ord('q') and key != curses.KEY_F1 and key != 27 and not selected:
    key = stdscr.getch()
    if key == curses.KEY_RESIZE:
      return
    count = 1
    for toon in chars:
      if key == ord(str(count)):
        new_char = chars[count - 1]
        selected = True
        break
      count = count + 1
  return new_char
