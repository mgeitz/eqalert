"""
eqalert curses
"""

import curses
import os

import eqa_struct

#def display(stop, screen, event):
#    while not stop.is_set():
#        if not event.empty():
#            process event


def init(char, healed, sdamaged, sdps, current_zone):
    """Create new screen in terminal"""
    main_screen = curses.initscr()
    os.system('setterm -cursor off')
    curses.start_color()
    curses.use_default_colors()
    curses.noecho()
    curses.cbreak()
    main_screen.keypad(1)
    main_screen.timeout(100)
    curses.init_pair(1, curses.COLOR_WHITE, -1)  # Title
    curses.init_pair(2, curses.COLOR_YELLOW, -1) # Header
    curses.init_pair(3, curses.COLOR_CYAN, -1)   # Subtext
    redraw_all(main_screen, char, healed, sdamaged, sdps, current_zone)
    return main_screen


def keys(key_queue, screen_obj):
  """Check dem keys"""
  key = ''
  while key != ord('q') and key != 27:
    key = screen_obj.getch()
    key_queue.put(key)


def close_screens(screen_obj):
  """Terminate screen_obj"""
  os.system('setterm -cursor on')
  curses.nocbreak()
  screen_obj.keypad(0)
  curses.echo()
  curses.endwin()


def draw_screen(screen_obj, char, current_zone):
    """Draws the main windows using curses"""
    screen_obj.clear()
    screen_obj.box()
    y, x = screen_obj.getmaxyx()
    center_y = y / 2
    center_x = x / 2

    screen_obj.addstr(0, center_x - 5, "|          |",
        curses.color_pair(1))
    screen_obj.addstr(0, center_x - 3, "EQ ALERT",
        curses.color_pair(2))

    screen_obj.addstr(1, center_x - x / 2 + 1, "F1 :",
        curses.color_pair(2))
    screen_obj.addstr(1, center_x - x / 2 + 7, "Help Menu",
        curses.color_pair(3))

    screen_obj.addstr(1, x - (center_x - x / 2 + 1) - len(char) - 1, char,
        curses.color_pair(3))

    screen_obj.addstr(2, center_x - x / 2 + 1, "F2 :",
        curses.color_pair(2))
    screen_obj.addstr(2, center_x - x / 2 + 7, "Char Menu",
        curses.color_pair(3))

    screen_obj.addstr(2, x - (center_x - x / 2 + 1) - len(current_zone) - 1, current_zone,
        curses.color_pair(3))


def draw_textbox(screen_obj):
    """Draws the captured text box"""
    by, bx = screen_obj.getmaxyx()
    offset_y = 5
    offset_x = bx / 12
    textbox = screen_obj.derwin(offset_y + 14, offset_x * 10, offset_y, offset_x)
    textbox.clear()
    textbox.box()

    screen_obj.addstr(offset_y, offset_x * 6 - 5, "|        |",
        curses.color_pair(1))
    screen_obj.addstr(offset_y, offset_x * 6 - 3, "Events",
        curses.color_pair(2))

    with open('./logs/eqalert.log') as t:
        content = t.readlines()
        end = len(content)
        count = 1
        while count < end and count < 18:
            screen_obj.addstr(offset_y - count + 18, offset_x + 1,
                content[end - count][33:].strip(), curses.color_pair(2))
            count = count + 1
        t.close()


def draw_healparse(screen_obj, healed):
    """Draws the heal parse box"""
    by, bx = screen_obj.getmaxyx()
    offset_y = 14
    offset_x = bx / 12
    textbox = screen_obj.derwin(offset_y - 5, (bx / 3) + 3, offset_y + 10, offset_x)
    textbox.clear()
    textbox.box()

    screen_obj.addstr(offset_y + 10, offset_x * 3 - 4, "|       |",
        curses.color_pair(1))
    screen_obj.addstr(offset_y + 10, offset_x * 3 - 2, "Heals",
        curses.color_pair(2))

    count = 1
    for (key, value) in healed.iteritems():
        screen_obj.addstr(offset_y + count + 10, offset_x + 1,
            key, curses.color_pair(2))
        screen_obj.addstr(offset_y + count + 10, offset_x + 2 - len(str(value)) + offset_x * 4,
            str(value), curses.color_pair(2))
        count = count + 1


def draw_spelldps(screen_obj, sdamaged, sdps):
    """Draws the spell parse box"""
    by, bx = screen_obj.getmaxyx()
    offset_y = 14
    offset_x = (bx / 2)
    textbox = screen_obj.derwin(offset_y - 5, (bx / 3), offset_y + 10, offset_x)
    textbox.clear()
    textbox.box()

    screen_obj.addstr(offset_y + 10, (bx / 2) + (bx / 6) - 7, "|            |",
        curses.color_pair(1))
    screen_obj.addstr(offset_y + 10, (bx / 2) + (bx / 6) - 4, "Damage",
        curses.color_pair(2))

    screen_obj.addstr(offset_y + 11, (bx / 2) + 1,
        "DPS:", curses.color_pair(2))
    screen_obj.addstr(offset_y + 11, (bx / 2) + (bx / 3) - 1 - len(str(sdps)),
        str(sdps), curses.color_pair(2))

    count = 2
    for (key, value) in sdamaged.iteritems():
        screen_obj.addstr(offset_y + count + 10, (bx / 2) + 1,
            key, curses.color_pair(2))
        screen_obj.addstr(offset_y + count + 10, (bx / 2) + (bx / 3) - 1 - len(str(value)),
            str(value), curses.color_pair(2))
        count = count + 1


def draw_help_menu(screen_obj):
    """Draws help menu."""
    screen_obj.clear()
    screen_obj.box()
    y, x = screen_obj.getmaxyx()
    center_y = y / 2
    center_x = x / 2

    screen_obj.addstr(0, center_x - 6, "|           |",
        curses.color_pair(1))
    screen_obj.addstr(0, center_x - 4, "EQA Help",
        curses.color_pair(2))

    screen_obj.addstr(1, center_x - x / 2 + 1, "F1 :",
        curses.color_pair(2))
    screen_obj.addstr(1, 5 + center_x - x / 2, "  Console",
        curses.color_pair(3))

    screen_obj.addstr(5, center_x - x / 3, "Commands:",
        curses.color_pair(1))
    screen_obj.addstr(7, center_x - x / 3, "Key             :",
        curses.color_pair(1))
    screen_obj.addstr(7, center_x - x / 3 + 17, "  Command",
        curses.color_pair(1))

    screen_obj.addstr(9, center_x - x / 3, "q:              :",
        curses.color_pair(2))
    screen_obj.addstr(9, center_x - x / 3 + 17, "  Quit/Back",
        curses.color_pair(3))

    screen_obj.addstr(10, center_x - x / 3, "h:              :",
        curses.color_pair(2))
    screen_obj.addstr(10, center_x - x / 3 + 17, "  Toggle heal parse",
        curses.color_pair(3))

    screen_obj.addstr(11, center_x - x / 3, "s:              :",
        curses.color_pair(2))
    screen_obj.addstr(11, center_x - x / 3 + 17, "  Toggle spell parse",
        curses.color_pair(3))

    screen_obj.addstr(12, center_x - x / 3, "p:              :",
        curses.color_pair(2))
    screen_obj.addstr(12, center_x - x / 3 + 17, "  Toggle all parses",
        curses.color_pair(3))

    screen_obj.addstr(13, center_x - x / 3, "c:              :",
        curses.color_pair(2))
    screen_obj.addstr(13, center_x - x / 3 + 17, "  Clear event box",
        curses.color_pair(3))

    screen_obj.addstr(14, center_x - x / 3, "r:              :",
        curses.color_pair(2))
    screen_obj.addstr(14, center_x - x / 3 + 17, "  Toggle raid mode",
        curses.color_pair(3))


    screen_obj.addstr(16, center_x - x / 3, "F1:             :",
        curses.color_pair(2))
    screen_obj.addstr(16, center_x - x / 3 + 17, "  Display help menu",
        curses.color_pair(3))

    screen_obj.addstr(17, center_x - x / 3, "F2:             :",
        curses.color_pair(2))
    screen_obj.addstr(17, center_x - x / 3 + 17, "  Open char menu",
        curses.color_pair(3))

    screen_obj.addstr(18, center_x - x / 3, "F3:             :",
        curses.color_pair(2))
    screen_obj.addstr(18, center_x - x / 3 + 17, "  Save and reset parses",
        curses.color_pair(3))

    screen_obj.addstr(19, center_x - x / 3, "F4:             :",
        curses.color_pair(2))
    screen_obj.addstr(19, center_x - x / 3 + 17, "  Clear heal parse history",
        curses.color_pair(3))

    screen_obj.addstr(20, center_x - x / 3, "F5:             :",
        curses.color_pair(2))
    screen_obj.addstr(20, center_x - x / 3 + 17, "  Clear spell parse history",
        curses.color_pair(3))

    screen_obj.addstr(21, center_x - x / 3, "F12:            :",
        curses.color_pair(2))
    screen_obj.addstr(21, center_x - x / 3 + 17, "  Reload config file",
        curses.color_pair(3))


def draw_toosmall(screen_obj):
    """Draws screen when too small"""
    screen_obj.clear()
    screen_obj.box()
    y, x = screen_obj.getmaxyx()
    center_y = y / 2
    center_x = x / 2

    screen_obj.addstr(center_y, center_x - 10, "Terminal too small.",
        curses.color_pair(1))


def draw_char_menu(screen_obj, chars):
    """Draws char menu."""
    screen_obj.clear()
    screen_obj.box()
    y, x = screen_obj.getmaxyx()
    center_y = y / 2
    center_x = x / 2

    screen_obj.addstr(0, center_x - 6, "|           |",
        curses.color_pair(1))
    screen_obj.addstr(0, center_x - 4, "Char Menu",
        curses.color_pair(2))

    screen_obj.addstr(1, center_x - x / 2 + 1, "F1 :",
        curses.color_pair(2))
    screen_obj.addstr(1, 5 + center_x - x / 2, "  Console",
        curses.color_pair(3))

    count = 0
    for toon in chars:
        screen_obj.addstr(6 + count + 1, center_x - x / 3, str(count + 1) + ":",
            curses.color_pair(1))
        screen_obj.addstr(6 + count + 1, center_x - x / 3 + 17, str(toon).title(),
            curses.color_pair(2))
        count = count + 1


def help_menu(screen_obj):
    """Controls help menu commands."""
    key = ''
    draw_help_menu(screen_obj)
    while key != ord('q') and key != curses.KEY_F1 and key != 27:
        key = screen_obj.getch()
        if key == curses.KEY_RESIZE:
            return


def char_menu(screen_obj, char, chars):
    """Controls char menu commands."""
    key = ''
    new_char = char
    draw_char_menu(screen_obj, chars)
    selected = False
    while key != ord('q') and key != curses.KEY_F1 and key != 27 and not selected:
        key = screen_obj.getch()
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


def redraw_all(screen_obj, char, healed, sdamaged, sdps, current_zone):
    """Redraw entire screen."""
    y, x = screen_obj.getmaxyx()
    if x >= 80 and y >= 40:
        draw_screen(screen_obj, char, current_zone)
        draw_textbox(screen_obj)
        draw_healparse(screen_obj, healed)
        draw_spelldps(screen_obj, sdamaged, sdps)
    else:
        draw_toosmall(screen_obj)



