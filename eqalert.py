#! /usr/bin/env python

"""
Parse, display, alert via eqlog
"""

import curses
import logging
import datetime
import time
import subprocess
import threading
import time
import os
from os import listdir
from os.path import isfile, join
import json
import eqaparser

__author__ = "Michael Geitz"
__version__ = "0.2.2"


##
##  CURSES
##


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

    with open('./eqa_logs/eqalert.log') as t:
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


##
##  CONFIG FILE
##


def add_type(line_type):
    """Adds default setting values for new line_type"""
    json_data = open('eqa_conf.json', 'r+')
    data = json.load(json_data)
    data["settings"]["sound_settings"].update({line_type:"0"})
    data["settings"]["check_line_type"].update({line_type:"true"})
    data["alert"].update({line_type:dict()})
    data["_HEADER"]["modified"] = str(datetime.datetime.now())
    json_data.seek(0)
    json.dump(data, json_data, indent = 4)
    json_data.close()


def add_zone(zone):
    """Adds default setting values for new zones"""
    json_data = open('eqa_conf.json', 'r+')
    data = json.load(json_data)
    data["zones"].update({zone:"false"})
    data["_HEADER"]["modified"] = str(datetime.datetime.now())
    json_data.seek(0)
    json.dump(data, json_data, indent = 4)
    json_data.close()


def read_config():
    """Returns JSON objects in config file"""
    json_data = open('eqa_conf.json', 'r')
    config = json.load(json_data)
    json_data.close()
    return config


def log_alert(line_type, check_line):
    """Logs an alert and refreshs display"""
    ## Seperated to maybe log line types differently
    log(line_type + ": " + check_line[0:65])


def init_config():
    """Updates _HEADER data in config file"""
    json_data = open('eqa_conf.json', 'r+')
    data = json.load(json_data)
    data["_HEADER"]["version"] = __version__
    data["_HEADER"]["parser_version"] = eqaparser.__version__
    data["_HEADER"]["modified"] = str(datetime.datetime.now())
    data["_HEADER"]["author"] = __author__
    json_data.seek(0)
    json.dump(data, json_data, indent = 4)
    json_data.close()


##
##  OTHER
##


def undetermined_line(line):
    """Temp function to log undetermined log lines"""
    f = open('./eqa_logs/undetermined.txt', 'a')
    f.write(line + '\n')
    f.close()


def log(message):
    """Effectively just for timestamping all log messages"""
    logging.info('[' + time_stamp() + ']: ' + str(message))


def time_stamp():
    """Returns a neat little timestamp for things"""
    unixstamp = int(time.time())
    timestamp = datetime.datetime.fromtimestamp(int(unixstamp))\
        .strftime('%Y-%m-%d %H:%M:%S')
    return str(timestamp)


def save_parse(healed, sdamaged, current_zone):
    """Save contents of healed and sdamaged to file"""
    eqa_log = "./eqa_logs/eqa_" + current_zone + "_" + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H:%M:%S') + ".log"
    with open(eqa_log, "a") as f:
        if healed:
            f.write("\n#\t#### HEALING ####\n#\n")
            for (key, value) in healed.iteritems():
                f.write("#\t")
                f.write(str(key))
                f.write("\t\t\t:\t")
                f.write(str(value))
                f.write("\n#\n")
        if sdamaged:
            f.write("\n#\t#### SPELL DAMAGE ####\n#\n")
            for (key, value) in sdamaged.iteritems():
                f.write("#\t")
                f.write(str(key))
                f.write("\t\t\t:\t")
                f.write(str(value))
                f.write("\n#\n")
        f.close()


def raid_alert(key, line):
    """Speak raid triggerable phrases"""
    if key == "assist" or key == "rampage":
        espeak(key + " on " + line[0])
    else:
        espeak(key)


def play_sound(sound):
    """Plays sound from path passed in"""
    command = ["aplay", sound]
    try:
        with open(os.devnull, "w") as fnull:
            subprocess.call(command, stdout=fnull, stderr = fnull)
    except KeyboardInterrupt:
        pass
    time.sleep(0.2)


def sound_alert(config, line_type):
    if not config["settings"]["sound_settings"][line_type] == "0":
        play_sound(config["settings"]["paths"]["sound"] + \
        config["settings"]["sounds"][config["settings"]["sound_settings"][line_type]])


def espeak(phrase):
    """Plays phrase using espeak"""
    command = ["espeak", "-v", "mb-en1", "-s", "140", phrase]
    try:
        with open(os.devnull, "w") as fnull:
            subprocess.call(command, stdout=fnull, stderr = fnull)
    except KeyboardInterrupt:
        pass
    time.sleep(0.2)


##
##  MAIN
##


def main():
    """Main method, does the good stuff"""

    ##
    ##  Variables / Initialization
    ##
    heal_parse = True
    spell_parse = True
    char_change = False
    on_raid = False
    healed = {}
    sdamaged = {}
    zones = {}
    start_time = 0
    total_damage = 0
    sdps = 0.0
    current_zone = "unavailable"

    # Logs
    logging.basicConfig(filename='./eqa_logs/eqalert.log', level=logging.DEBUG)
    log('Initializing... ' + str(datetime.datetime.now()))
    init_config()
    config = read_config()
    char = config["characters"]["default"]
    log_path = config["settings"]["paths"]["log"] + "eqlog_" + char.title() + "_project1999.txt"
    log_files = [ f for f in listdir(config["settings"]["paths"]["log"]) if isfile(join(config["settings"]["paths"]["log"],f)) ]
    chars = []
    for toon in config["characters"].keys():
        if toon != "default":
            chars.append(toon)
    for logs in log_files:
        if "eqlog_" in logs and "_project1999.txt" in logs:
            first, name, end = logs.split("_")
            if name.lower() not in config["characters"].keys():
                json_data = open('eqa_conf.json', 'r+')
                data = json.load(json_data)
                data["characters"].update({name.lower():"true"})
                chars.append(name.lower())
                data["_HEADER"]["modified"] = str(datetime.datetime.now())
                json_data.seek(0)
                json.dump(data, json_data, indent = 4)
                json_data.close()
    for toon in config["characters"].keys():
        if config["characters"][toon] == "false":
            chars.remove(toon)

    # Screen
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

    ##
    ##  Curses loop
    ##
    key = ''
    last_end = len(eqaparser.read(log_path))
    espeak('E Q alert initialized with ' + char)
    while key != ord('q') and key != 27:

        # F Keys / Resize
        if key == curses.KEY_RESIZE:
            redraw_all(main_screen, char, healed, sdamaged, sdps, current_zone)
        if key == curses.KEY_F1:
            help_menu(main_screen)
            redraw_all(main_screen, char, healed, sdamaged, sdps, current_zone)
        if key == curses.KEY_F2:
            new_char = char_menu(main_screen, char, chars)
            redraw_all(main_screen, char, healed, sdamaged, sdps, current_zone)
            if new_char == char:
                char_change = False
            else:
                char = new_char
                char_change = True
            redraw_all(main_screen, char, healed, sdamaged, sdps, current_zone)
        if key == curses.KEY_F3:
            if heal_parse or spell_parse:
                if healed or sdamaged:
                    save_parse(healed, sdamaged, current_zone)
                    healed = {}
                    sdamaged = {}
                    total_damage = 0
                    sdps = 0
                    log('Parse history saved and cleared')
                    espeak('Parse history saved and cleared')
                else:
                    log('No history to clear')
            redraw_all(main_screen, char, healed, sdamaged, sdps, current_zone)
        if key == curses.KEY_F4:
            healed = {}
            log("Heal parse cleared")
            espeak("Heal parse cleared")
            redraw_all(main_screen, char, healed, sdamaged, sdps, current_zone)
        if key == curses.KEY_F5:
            sdamaged = {}
            log("Spell parse cleared")
            espeak("Spell parse cleared")
            redraw_all(main_screen, char, healed, sdamaged, sdps, current_zone)
        if key == curses.KEY_F12:
            config = read_config()
            log("Configuration reloaded")
            espeak("Configuration reloaded")

        # Alphanumeric keys
        if key == ord('h'):
            if heal_parse:
                heal_parse = False
                log('Heal parse disbled')
                espeak('Heal parse disbled')
            elif not heal_parse:
                heal_parse = True
                log('Heal parse enabled')
                espeak('Heal parse enabled')
            redraw_all(main_screen, char, healed, sdamaged, sdps, current_zone)
        if key == ord('s'):
            if spell_parse:
                spell_parse = False
                log('Spell parse disabled')
                espeak('Spell parse disabled')
            elif not spell_parse:
                spell_parse = True
                log('Spell parse enabled')
                espeak('Spell parse enabled')
            redraw_all(main_screen, char, healed, sdamaged, sdps, current_zone)
        if key == ord('p'):
            if spell_parse:
                spell_parse = False
                log('Spell parse disabled')
                espeak('Spell parse disabled')
            elif not spell_parse:
                spell_parse = True
                log('Spell parse enabled')
                espeak('Spell parse enabled')
            if heal_parse:
                heal_parse = False
                log('Heal parse disbled')
                espeak('Heal parse disbled')
            elif not heal_parse:
                heal_parse = True
                log('Heal parse enabled')
                espeak('Heal parse enabled')
            redraw_all(main_screen, char, healed, sdamaged, sdps, current_zone)
        if key == ord('c'):
            log("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
            redraw_all(main_screen, char, healed, sdamaged, sdps, current_zone)
        if key == ord('r'):
            if not on_raid:
                on_raid = True
                log("Raid mode enabled")
                espeak("Raid mode enabled")
            elif on_raid:
                on_raid = False
                log("Raid mode disabled")
                espeak("Raid mode disabled")
            redraw_all(main_screen, char, healed, sdamaged, sdps, current_zone)


        ##
        ##  Read log
        ##
        if char_change:
            char_change = False
            log_path = config["settings"]["paths"]["log"] + "eqlog_" + char.title() + "_project1999.txt"
            eqlog = eqaparser.read(log_path)
            last_end = len(eqlog)
            end = last_end
            log("Character changed to " + char)
            espeak("Character changed to " + char)
            redraw_all(main_screen, char, healed, sdamaged, sdps, current_zone)
        else:
            eqlog = eqaparser.read(log_path)
            end = len(eqlog)
        count = 0
        while count < end - last_end:
            check_line = eqlog[last_end + count][27:].strip().lower()
            check_line_list = check_line.split(' ')
            line_type = eqaparser.determine(check_line, check_line_list)
            redraw_all(main_screen, char, healed, sdamaged, sdps, current_zone)

            # Line specific checks
            if line_type == "undetermined":
                undetermined_line(check_line)
            if line_type == "you_new_zone":
                nz_iter = 0
                current_zone = ""
                while check_line_list.index("entered") + nz_iter + 1 < len(check_line_list):
                    current_zone += check_line_list[check_line_list.index("entered") + nz_iter + 1] + " "
                    nz_iter += 1
                current_zone = current_zone[:-2]
                espeak(current_zone)
                if current_zone not in config["zones"].keys():
                    add_zone(current_zone)
                elif current_zone in config["zones"].keys() and not on_raid:
                    if config["zones"][current_zone] == "raid":
                        on_raid = True
                        log("Raid mode auto-enabled")
                        espeak("Raid mode enabled")
                elif current_zone in config["zones"].keys() and on_raid:
                    if config["zones"][current_zone] != "raid":
                        on_raid = False
                        log("Raid mode auto-disabled")
                        espeak("Raid mode disabled")

            # If line_type is a parsable type
            if line_type in config["settings"]["check_line_type"].keys():
                # If line_type is parsed for as true
                if config["settings"]["check_line_type"][line_type] == "true":
                    for keyphrase, value in config["alert"][line_type].iteritems():
                        if str(keyphrase).lower() in check_line and value == "true":
                            sound_alert(config, line_type)
                            log_alert(line_type, check_line)
                        elif str(keyphrase).lower() in check_line and value == "raid" and on_raid:
                            log_alert(line_type, check_line)
                            raid_alert(keyphrase, check_line_list)

                # Or if line_type is parsed for as all
                elif config["settings"]["check_line_type"][line_type] == "all":
                    # Heal parse
                    if heal_parse and line_type == "you_healed":
                        if check_line_list[3] not in healed:
                            healed[check_line_list[3]] = int(check_line_list[5])
                        else:
                            healed[check_line_list[3]] = int(healed[check_line_list[3]]) + int(check_line_list[5])

                    # Spell damage parse
                    elif spell_parse and line_type == "spell_damage":
                        length = check_line_list.index('was')
                        sp_iter = 0
                        name = ""
                        while sp_iter < length:
                           name = name + check_line_list[sp_iter] + " "
                           sp_iter += 1
                        if name not in sdamaged:
                            sdamaged[name] = int(check_line_list[-4])
                            log("New Target: " + name)
                            start_time = time.time()
                            time.clock()
                        else:
                            sdamaged[name] = int(sdamaged[name]) + int(check_line_list[-4])

                        if sdamaged:
                            elapsed = time.time() - start_time
                            if elapsed > 48:
                                start_time = time.time()
                                total_damage = 0
                            total_damage = total_damage + int(check_line_list[-4])
                            if elapsed < 1.0:
                                sdps = sdps + (total_damage / 48)
                            else:
                                sdps = (total_damage / elapsed)

                    # DoT damage parse
                    elif spell_parse and line_type == "dot_damage":
                        length = check_line_list.index('has')
                        dp_iter = 0
                        name = ""
                        damage = int(check_line_list[length + 2])
                        while dp_iter < length:
                           name = name + check_line_list[dp_iter] + " "
                           dp_iter += 1
                        if name not in sdamaged:
                            sdamaged[name] = damage
                            log("New Target: " + name)
                            start_time = time.time()
                            time.clock()
                        else:
                            sdamaged[name] = int(sdamaged[name]) + damage

                        if sdamaged:
                            elapsed = time.time() - start_time
                            if elapsed > 48:
                                start_time = time.time()
                                total_damage = 0
                            total_damage = total_damage + damage
                            if elapsed < 1.0:
                                sdps = sdps + (total_damage / 48)
                            else:
                                sdps = (total_damage / elapsed)

                    # Notify on all other all alerts
                    else:
                        sound_alert(config, line_type)
                        log_alert(line_type, check_line)
                # Or if line_type is parsed for as a spoken alert
                elif config["settings"]["check_line_type"][line_type] == "speak":
                    log("espeak: " + check_line)
                    espeak(check_line)
                # For triggers requiring all line_types
                if config["settings"]["check_line_type"]["all"] == "true":
                    for keyphrase, value in config["alert"]["all"].iteritems():
                        if keyphrase in check_line:
                            sound_alert(config, line_type)
                            log_alert(line_type, check_line)

            # If line_type is not a parsable type
            else:
                add_type(line_type)
                log('Added: ' + line_type)
                config = read_config()
                count -= 1
            count += 1
        last_end = end
        key = main_screen.getch()


    os.system('setterm -cursor on')
    curses.nocbreak()
    main_screen.keypad(0)
    curses.echo()
    curses.endwin()
    log('Exiting...\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
if __name__ == '__main__':
    main()
