"""
eqalert curses
"""

import curses
import os
import time

import eqa_struct
import eqa_settings

def display(screen, display_q, message_q, zone, char, chars, exit_flag):

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
            draw_page(screen, page, events, char, zone)
          elif display_event.screen == 'char':
            char = display_event.payload
            draw_page(screen, page, events, char, zone)

        # Display Draw
        elif display_event.type == 'draw':
          if display_event.screen == "events":
            page = 'events'
            draw_page(screen, page, events, char, zone)
          elif display_event.screen == 'state':
            page = 'state'
            draw_page(screen, page, events, char, zone)
          elif display_event.screen == 'settings':
            page = 'settings'
            draw_page(screen, page, events, char, zone)
          elif display_event.screen == 'help':
            page = 'help'
            draw_page(screen, page, events, char, zone)

        # Draw Update
        elif display_event.type == 'event':
          if display_event.screen == 'events':
            events.append([display_event])
            if page == 'events':
              draw_events(screen, char, zone, events)
          elif display_event.screen == 'clear':
            events = []



  except Exception as e:
    eqa_settings.log(e)
    pass


def draw_page(screen, page, events, char, zone):
  y, x = screen.getmaxyx()
  if x >= 80 and y >= 40:
    if page == 'events':
      draw_events_frame(screen, char, zone, events)
    elif page == 'state':
      draw_state(screen)
    elif page == 'settings':
      draw_settings(screen)
    elif page == 'help':
      draw_help(screen)
  else:
    draw_toosmall(screen)

def init(char, zone):
  """Create new screen in terminal"""
  screen = curses.initscr()
  os.system('setterm -cursor off')
  curses.start_color()
  curses.use_default_colors()
  curses.noecho()
  curses.cbreak()
  screen.keypad(1)
  screen.timeout(100)
  curses.init_pair(1, curses.COLOR_WHITE, -1)     # Title
  curses.init_pair(2, curses.COLOR_YELLOW, -1)    # Header
  curses.init_pair(3, curses.COLOR_CYAN, -1)      # Subtext
  curses.init_pair(4, curses.COLOR_MAGENTA, -1)   # Highlight
  curses.init_pair(5, curses.COLOR_GREEN, -1)     # Dunno
  draw_events_frame(screen, char, zone, [])
  return screen


def close_screens(screen):
  """Terminate screen"""
  os.system('setterm -cursor on')
  curses.nocbreak()
  screen.keypad(0)
  curses.echo()
  curses.endwin()


def draw_events_frame(screen, char, zone, events):
  """Draws the main window and tabs using curses"""
  y, x = screen.getmaxyx()
  center_y = y / 2
  center_x = x / 2

  # Clear and box
  screen.clear()
  screen.box()

  # Events tab
  screen.addstr(1, 2, "F1", curses.color_pair(3))
  screen.addstr(1, 4, ":", curses.color_pair(1))
  screen.addstr(1, 6, "events", curses.color_pair(4))
  screen.addstr(1, 13, curses.ACS_VLINE, curses.color_pair(1))

  # State tab
  screen.addstr(1, 15, "F2", curses.color_pair(3))
  screen.addstr(1, 17, ":", curses.color_pair(1))
  screen.addstr(1, 19, "state", curses.color_pair(2))
  screen.addstr(1, 21, curses.ACS_VLINE, curses.color_pair(1))

  # Settings tab
  screen.addstr(1, x - 23, "F3", curses.color_pair(3))
  screen.addstr(1, x - 21, ":", curses.color_pair(1))
  screen.addstr(1, x - 20, "settings", curses.color_pair(2))
  screen.addstr(1, x - 25, curses.ACS_VLINE, curses.color_pair(1))

  # Help tab
  screen.addstr(1, x - 9, "F4", curses.color_pair(3))
  screen.addstr(1, x - 8, ":", curses.color_pair(1))
  screen.addstr(1, x - 6, "help", curses.color_pair(2))
  screen.addstr(1, x - 11, curses.ACS_VLINE, curses.color_pair(1))

  # Center title
  screen.addstr(1, center_x - 4, "EQ ALERT", curses.color_pair(2))

  # Bottom of tabs
  for c in range (x):
    screen.addch(2, c, curses.ACS_HLINE)

  # Bottom of events
  for c in range (x):
    screen.addch(center_y, c, curses.ACS_HLINE)

  # Character
  screen.addstr(center_y + 1, 1, char, curses.color_pair(2))

  # Zone
  screen.addstr(center_y + 1, x - len(zone) - 1, zone, curses.color_pair(2))

  # Draw events
  draw_events(screen, events)


def draw_events(screen, events):
  y, x = screen.getmaxyx()
  center_y = y / 2
  center_x = x / 2
  bottom_y = center_y - 1
  top_y = 3

  event_box = screen.derwin(center_y - 3, x - 4, 2, 2)
  event_box.clear()
  #event_box.box()

  count = 0
  while count < (bottom_y - top_y) or count < len(events):
    c_y = bottom_y + count
    event_num = len(events) - count - 1
    event = events[(count + 1) * -1]
    timestamp = event.timestamp
    screen.addstr(c_y, 2, event.timestamp, curses.color_pair(1))
    screen.addstr(c_y, 14, curses.ACS_VLINE, curses.color_pair(5))
    screen.addstr(c_y, 16, event.payload, curses.color_pair(1))
    count += 1


def draw_state(screen):
  """Draws the main window and tabs using curses"""
  y, x = screen.getmaxyx()
  center_y = y / 2
  center_x = x / 2

  # Clear and box
  screen.clear()
  screen.box()

  # Events tab
  screen.addstr(1, 2, "F1", curses.color_pair(3))
  screen.addstr(1, 4, ":", curses.color_pair(1))
  screen.addstr(1, 6, "events", curses.color_pair(2))
  screen.addstr(1, 13, curses.ACS_VLINE, curses.color_pair(1))

  # State tab
  screen.addstr(1, 15, "F2", curses.color_pair(3))
  screen.addstr(1, 17, ":", curses.color_pair(1))
  screen.addstr(1, 19, "state", curses.color_pair(4))
  screen.addstr(1, 21, curses.ACS_VLINE, curses.color_pair(1))

  # Settings tab
  screen.addstr(1, x - 23, "F3", curses.color_pair(3))
  screen.addstr(1, x - 21, ":", curses.color_pair(1))
  screen.addstr(1, x - 20, "settings", curses.color_pair(2))
  screen.addstr(1, x - 25, curses.ACS_VLINE, curses.color_pair(1))

  # Help tab
  screen.addstr(1, x - 9, "F4", curses.color_pair(3))
  screen.addstr(1, x - 8, ":", curses.color_pair(1))
  screen.addstr(1, x - 6, "help", curses.color_pair(2))
  screen.addstr(1, x - 11, curses.ACS_VLINE, curses.color_pair(1))

  # Center title
  screen.addstr(1, center_x - 4, "EQ ALERT", curses.color_pair(2))

  # Bottom of tabs
  for c in range (x):
    screen.addch(2, c, curses.ACS_HLINE)


def draw_settings_frame(screen):
  """Draws the main window and tabs using curses"""
  y, x = screen.getmaxyx()
  center_y = y / 2
  center_x = x / 2

  # Clear and box
  screen.clear()
  screen.box()

  # Events tab
  screen.addstr(1, 2, "F1", curses.color_pair(3))
  screen.addstr(1, 4, ":", curses.color_pair(1))
  screen.addstr(1, 6, "events", curses.color_pair(2))
  screen.addstr(1, 13, curses.ACS_VLINE, curses.color_pair(1))

  # State tab
  screen.addstr(1, 15, "F2", curses.color_pair(3))
  screen.addstr(1, 17, ":", curses.color_pair(1))
  screen.addstr(1, 19, "state", curses.color_pair(2))
  screen.addstr(1, 21, curses.ACS_VLINE, curses.color_pair(1))

  # Settings tab
  screen.addstr(1, x - 23, "F3", curses.color_pair(3))
  screen.addstr(1, x - 21, ":", curses.color_pair(1))
  screen.addstr(1, x - 20, "settings", curses.color_pair(4))
  screen.addstr(1, x - 25, curses.ACS_VLINE, curses.color_pair(1))

  # Help tab
  screen.addstr(1, x - 9, "F4", curses.color_pair(3))
  screen.addstr(1, x - 8, ":", curses.color_pair(1))
  screen.addstr(1, x - 6, "help", curses.color_pair(2))
  screen.addstr(1, x - 11, curses.ACS_VLINE, curses.color_pair(1))

  # Center title
  screen.addstr(1, center_x - 4, "EQ ALERT", curses.color_pair(2))

  # Bottom of tabs
  for c in range (x):
    screen.addch(2, c, curses.ACS_HLINE)


def draw_healparse(screen, healed):
    """Draws the heal parse box"""
    by, bx = screen.getmaxyx()
    offset_y = 14
    offset_x = bx / 12
    textbox = screen.derwin(offset_y - 5, (bx / 3) + 3, offset_y + 10, offset_x)
    textbox.clear()
    textbox.box()

    screen.addstr(offset_y + 10, offset_x * 3 - 4, "|       |",
        curses.color_pair(1))
    screen.addstr(offset_y + 10, offset_x * 3 - 2, "Heals",
        curses.color_pair(2))

    count = 1
    for (key, value) in healed.iteritems():
        screen.addstr(offset_y + count + 10, offset_x + 1,
            key, curses.color_pair(2))
        screen.addstr(offset_y + count + 10, offset_x + 2 - len(str(value)) + offset_x * 4,
            str(value), curses.color_pair(2))
        count = count + 1


def draw_spelldps(screen, sdamaged, sdps):
    """Draws the spell parse box"""
    by, bx = screen.getmaxyx()
    offset_y = 14
    offset_x = (bx / 2)
    textbox = screen.derwin(offset_y - 5, (bx / 3), offset_y + 10, offset_x)
    textbox.clear()
    textbox.box()

    screen.addstr(offset_y + 10, (bx / 2) + (bx / 6) - 7, "|            |",
        curses.color_pair(1))
    screen.addstr(offset_y + 10, (bx / 2) + (bx / 6) - 4, "Damage",
        curses.color_pair(2))

    screen.addstr(offset_y + 11, (bx / 2) + 1,
        "DPS:", curses.color_pair(2))
    screen.addstr(offset_y + 11, (bx / 2) + (bx / 3) - 1 - len(str(sdps)),
        str(sdps), curses.color_pair(2))

    count = 2
    for (key, value) in sdamaged.iteritems():
        screen.addstr(offset_y + count + 10, (bx / 2) + 1,
            key, curses.color_pair(2))
        screen.addstr(offset_y + count + 10, (bx / 2) + (bx / 3) - 1 - len(str(value)),
            str(value), curses.color_pair(2))
        count = count + 1


def draw_help(screen):
  """Draws help menu."""
  y, x = screen.getmaxyx()
  center_y = y / 2
  center_x = x / 2

  # Clear and box
  screen.clear()
  screen.box()

  # Events tab
  screen.addstr(1, 2, "F1", curses.color_pair(3))
  screen.addstr(1, 4, ":", curses.color_pair(1))
  screen.addstr(1, 6, "events", curses.color_pair(2))
  screen.addstr(1, 13, curses.ACS_VLINE, curses.color_pair(1))

  # State tab
  screen.addstr(1, 15, "F2", curses.color_pair(3))
  screen.addstr(1, 17, ":", curses.color_pair(1))
  screen.addstr(1, 19, "state", curses.color_pair(2))
  screen.addstr(1, 21, curses.ACS_VLINE, curses.color_pair(1))

  # Settings tab
  screen.addstr(1, x - 23, "F3", curses.color_pair(3))
  screen.addstr(1, x - 21, ":", curses.color_pair(1))
  screen.addstr(1, x - 20, "settings", curses.color_pair(2))
  screen.addstr(1, x - 25, curses.ACS_VLINE, curses.color_pair(1))

  # Help tab
  screen.addstr(1, x - 9, "F4", curses.color_pair(3))
  screen.addstr(1, x - 8, ":", curses.color_pair(1))
  screen.addstr(1, x - 6, "help", curses.color_pair(4))
  screen.addstr(1, x - 11, curses.ACS_VLINE, curses.color_pair(1))

  # Center title
  screen.addstr(1, center_x - 4, "EQ ALERT", curses.color_pair(2))

  # Bottom of tabs
  for c in range (x):
    screen.addch(2, c, curses.ACS_HLINE)

  screen.addstr(5, center_x - x / 3, "Commands:",
    curses.color_pair(1))
  screen.addstr(7, center_x - x / 3, "Key             :",
    curses.color_pair(1))
  screen.addstr(7, center_x - x / 3 + 17, "  state",
    curses.color_pair(1))

  screen.addstr(9, center_x - x / 3, "q:              :",
    curses.color_pair(2))
  screen.addstr(9, center_x - x / 3 + 17, "  Quit",
    curses.color_pair(3))

  screen.addstr(10, center_x - x / 3, "h:              :",
    curses.color_pair(2))
  screen.addstr(10, center_x - x / 3 + 17, "  Toggle heal parse",
    curses.color_pair(3))

  screen.addstr(11, center_x - x / 3, "s:              :",
    curses.color_pair(2))
  screen.addstr(11, center_x - x / 3 + 17, "  Toggle spell parse",
    curses.color_pair(3))

  screen.addstr(12, center_x - x / 3, "p:              :",
    curses.color_pair(2))
  screen.addstr(12, center_x - x / 3 + 17, "  Toggle all parses",
    curses.color_pair(3))

  screen.addstr(13, center_x - x / 3, "c:              :",
    curses.color_pair(2))
  screen.addstr(13, center_x - x / 3 + 17, "  Clear event box",
    curses.color_pair(3))

  screen.addstr(14, center_x - x / 3, "r:              :",
    curses.color_pair(2))
  screen.addstr(14, center_x - x / 3 + 17, "  Toggle raid mode",
    curses.color_pair(3))

  screen.addstr(16, center_x - x / 3, "F1:             :",
   curses.color_pair(2))
  screen.addstr(16, center_x - x / 3 + 17, "  Events",
    curses.color_pair(3))

  screen.addstr(17, center_x - x / 3, "F2:             :",
    curses.color_pair(2))
  screen.addstr(17, center_x - x / 3 + 17, "  State",
   curses.color_pair(3))

  screen.addstr(18, center_x - x / 3, "F3:             :",
    curses.color_pair(2))
  screen.addstr(18, center_x - x / 3 + 17, "  Settings",
    curses.color_pair(3))

  screen.addstr(19, center_x - x / 3, "F4:             :",
    curses.color_pair(2))
  screen.addstr(19, center_x - x / 3 + 17, "  Help",
    curses.color_pair(3))


def draw_toosmall(screen):
    """Draws screen when too small"""
    screen.clear()
    screen.box()
    y, x = screen.getmaxyx()
    center_y = y / 2
    center_x = x / 2

    screen.addstr(center_y, center_x - 10, "Terminal too small.",
        curses.color_pair(1))


def draw_char_menu(screen, chars):
    """Draws char menu."""
    screen.clear()
    screen.box()
    y, x = screen.getmaxyx()
    center_y = y / 2
    center_x = x / 2

    screen.addstr(0, center_x - 6, "|           |",
        curses.color_pair(1))
    screen.addstr(0, center_x - 4, "Char Menu",
        curses.color_pair(2))

    screen.addstr(1, center_x - x / 2 + 1, "F1 :",
        curses.color_pair(2))
    screen.addstr(1, 5 + center_x - x / 2, "  Console",
        curses.color_pair(3))

    count = 0
    for toon in chars:
        screen.addstr(6 + count + 1, center_x - x / 3, str(count + 1) + ":",
            curses.color_pair(1))
        screen.addstr(6 + count + 1, center_x - x / 3 + 17, str(toon).title(),
            curses.color_pair(2))
        count = count + 1


def char_menu(screen, chars):
  """Controls char menu commands."""
  key = ''
  new_char = char

  draw_char_menu(screen, chars)

  selected = False
  while key != ord('q') and key != curses.KEY_F1 and key != 27 and not selected:
    key = screen.getch()
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


def redraw_all(screen, char, zone, events):
    """Redraw entire screen."""
    y, x = screen.getmaxyx()
    if x >= 80 and y >= 40:
        draw_events_frame(screen, char, zone)
        draw_events(screen, events)
        #draw_healparse(screen, healed)
        #draw_spelldps(screen, sdamaged, sdps)
    else:
        draw_toosmall(screen)



