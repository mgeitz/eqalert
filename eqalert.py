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

import lib.eqa_parser as eqa_parse
import lib.eqa_config as eqa_config
import lib.eqa_settings as eqa_settings
import lib.eqa_curses as eqa_curses
import lib.eqa_action as eqa_action
import lib.eqa_parser as eqa_parser

__author__ = "Michael Geitz"
__version__ = "0.2.2"


def log_alert(line_type, check_line):
    """Logs an alert and refreshs display"""
    ## Seperated to maybe log line types differently
    eqa_settings.log(line_type + ": " + check_line[0:65])


def undetermined_line(line):
    """Temp function to log undetermined log lines"""
    f = open('./logs/undetermined.txt', 'a')
    f.write(line + '\n')
    f.close()


def save_parse(healed, sdamaged, current_zone):
    """Save contents of healed and sdamaged to file"""
    eqa_log = "./logs/eqa_" + current_zone + "_" + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H:%M:%S') + ".log"
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
    logging.basicConfig(filename='./logs/eqalert.log', level=logging.DEBUG)
    eqa_settings.log('Initializing... ' + str(datetime.datetime.now()))
    eqa_config.init()
    config = eqa_config.read()
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
    main_screen = eqa_curses.init(char, healed, sdamaged, sdps, current_zone)

    ##
    ##  Curses loop
    ##
    key = ''
    last_end = len(eqa_parser.read(log_path))
    eqa_action.espeak('initialized')
    while key != ord('q') and key != 27:

        # F Keys / Resize
        if key == curses.KEY_RESIZE:
            eqa_curses.redraw_all(main_screen, char, healed, sdamaged, sdps, current_zone)
        if key == curses.KEY_F1:
            help_menu(main_screen)
            eqa_curses.redraw_all(main_screen, char, healed, sdamaged, sdps, current_zone)
        if key == curses.KEY_F2:
            new_char = char_menu(main_screen, char, chars)
            eqa_curses.redraw_all(main_screen, char, healed, sdamaged, sdps, current_zone)
            if new_char == char:
                char_change = False
            else:
                char = new_char
                char_change = True
            eqa_curses.redraw_all(main_screen, char, healed, sdamaged, sdps, current_zone)
        if key == curses.KEY_F3:
            if heal_parse or spell_parse:
                if healed or sdamaged:
                    save_parse(healed, sdamaged, current_zone)
                    healed = {}
                    sdamaged = {}
                    total_damage = 0
                    sdps = 0
                    eqa_settings.log('Parse history saved and cleared')
                    eqa_action.espeak('Parse history saved and cleared')
                else:
                    eqa_settings.log('No history to clear')
            eqa_curses.redraw_all(main_screen, char, healed, sdamaged, sdps, current_zone)
        if key == curses.KEY_F4:
            healed = {}
            eqa_settings.log("Heal parse cleared")
            eqa_action.espeak("Heal parse cleared")
            eqa_curses.redraw_all(main_screen, char, healed, sdamaged, sdps, current_zone)
        if key == curses.KEY_F5:
            sdamaged = {}
            eqa_settings.log("Spell parse cleared")
            eqa_action.espeak("Spell parse cleared")
            eqa_curses.redraw_all(main_screen, char, healed, sdamaged, sdps, current_zone)
        if key == curses.KEY_F12:
            config = eqa_config.read()
            eqa_settings.log("Configuration reloaded")
            eqa_action.espeak("Configuration reloaded")

        # Alphanumeric keys
        if key == ord('h'):
            if heal_parse:
                heal_parse = False
                eqa_settings.log('Heal parse disbled')
                eqa_action.espeak('Heal parse disbled')
            elif not heal_parse:
                heal_parse = True
                eqa_settings.log('Heal parse enabled')
                eqa_action.espeak('Heal parse enabled')
            eqa_curses.redraw_all(main_screen, char, healed, sdamaged, sdps, current_zone)
        if key == ord('s'):
            if spell_parse:
                spell_parse = False
                eqa_settings.log('Spell parse disabled')
                eqa_action.espeak('Spell parse disabled')
            elif not spell_parse:
                spell_parse = True
                eqa_settings.log('Spell parse enabled')
                eqa_action.espeak('Spell parse enabled')
            eqa_curses.redraw_all(main_screen, char, healed, sdamaged, sdps, current_zone)
        if key == ord('p'):
            if spell_parse:
                spell_parse = False
                eqa_settings.log('Spell parse disabled')
                eqa_action.espeak('Spell parse disabled')
            elif not spell_parse:
                spell_parse = True
                eqa_settings.log('Spell parse enabled')
                eqa_action.espeak('Spell parse enabled')
            if heal_parse:
                heal_parse = False
                eqa_settings.log('Heal parse disbled')
                eqa_action.espeak('Heal parse disbled')
            elif not heal_parse:
                heal_parse = True
                eqa_settings.log('Heal parse enabled')
                eqa_action.espeak('Heal parse enabled')
            eqa_curses.redraw_all(main_screen, char, healed, sdamaged, sdps, current_zone)
        if key == ord('c'):
            eqa_settings.log("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
            eqa_curses.redraw_all(main_screen, char, healed, sdamaged, sdps, current_zone)
        if key == ord('r'):
            if not on_raid:
                on_raid = True
                eqa_settings.log("Raid mode enabled")
                eqa_action.espeak("Raid mode enabled")
            elif on_raid:
                on_raid = False
                eqa_settings.log("Raid mode disabled")
                eqa_action.espeak("Raid mode disabled")
            eqa_curses.redraw_all(main_screen, char, healed, sdamaged, sdps, current_zone)


        ##
        ##  Read log
        ##
        if char_change:
            char_change = False
            log_path = config["settings"]["paths"]["log"] + "eqlog_" + char.title() + "_project1999.txt"
            eqlog = eqa_parser.read(log_path)
            last_end = len(eqlog)
            end = last_end
            eqa_settings.log("Character changed to " + char)
            eqa_action.espeak("Character changed to " + char)
            eqa_curses.redraw_all(main_screen, char, healed, sdamaged, sdps, current_zone)
        else:
            eqlog = eqa_parser.read(log_path)
            end = len(eqlog)
        count = 0
        while count < end - last_end:
            check_line = eqlog[last_end + count][27:].strip().lower()
            check_line_list = check_line.split(' ')
            line_type = eqa_parser.determine(check_line, check_line_list)
            eqa_curses.redraw_all(main_screen, char, healed, sdamaged, sdps, current_zone)

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
                eqa_action.espeak(current_zone)
                if current_zone not in config["zones"].keys():
                    eqa_config.add_zone(current_zone)
                elif current_zone in config["zones"].keys() and not on_raid:
                    if config["zones"][current_zone] == "raid":
                        on_raid = True
                        eqa_settings.log("Raid mode auto-enabled")
                        eqa_action.espeak("Raid mode enabled")
                elif current_zone in config["zones"].keys() and on_raid:
                    if config["zones"][current_zone] != "raid":
                        on_raid = False
                        eqa_settings.log("Raid mode auto-disabled")
                        eqa_action.espeak("Raid mode disabled")

            # If line_type is a parsable type
            if line_type in config["settings"]["check_line_type"].keys():
                # If line_type is parsed for as true
                if config["settings"]["check_line_type"][line_type] == "true":
                    for keyphrase, value in config["alert"][line_type].iteritems():
                        if str(keyphrase).lower() in check_line and value == "true":
                            eqa_action.sound_alert(config, line_type)
                            log_alert(line_type, check_line)
                        elif str(keyphrase).lower() in check_line and value == "raid" and on_raid:
                            log_alert(line_type, check_line)
                            eqa_action.raid_alert(keyphrase, check_line_list)

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
                            eqa_settings.log("New Target: " + name)
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
                            eqa_settings.log("New Target: " + name)
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
                        eqa_action.sound_alert(config, line_type)
                        log_alert(line_type, check_line)
                # Or if line_type is parsed for as a spoken alert
                elif config["settings"]["check_line_type"][line_type] == "speak":
                    eqa_settings.log("espeak: " + check_line)
                    eqa_action.espeak(check_line)
                # For triggers requiring all line_types
                if config["settings"]["check_line_type"]["all"] == "true":
                    for keyphrase, value in config["alert"]["all"].iteritems():
                        if keyphrase in check_line:
                            eqa_action.sound_alert(config, line_type)
                            log_alert(line_type, check_line)

            # If line_type is not a parsable type
            else:
                eqa_config.add_type(line_type)
                eqa_settings.log('Added: ' + line_type)
                config = eqa_config.read()
                count -= 1
            count += 1
        last_end = end
        key = main_screen.getch()


    eqa_curses.close_screens(main_screen)
    eqa_settings.log('Exiting...\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
if __name__ == '__main__':
    main()
