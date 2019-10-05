#! /usr/bin/env python

"""
   Program:   EQ Alert
   File Name: eqalert.py
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

   Parse and react to eqemu logs
"""

import pyinotify
import curses
import logging
import datetime
import time
import threading
import queue
import os

import lib.eqa_parser as eqa_parse
import lib.eqa_config as eqa_config
import lib.eqa_settings as eqa_settings
import lib.eqa_curses as eqa_curses
import lib.eqa_sound as eqa_sound
import lib.eqa_parser as eqa_parser
import lib.eqa_struct as eqa_struct
import lib.eqa_action as eqa_action
import lib.eqa_keys as eqa_keys


def main():
  """Main method, does the good stuff"""

  # Queues
  keyboard_q = queue.Queue()
  action_q = queue.Queue()
  display_q = queue.Queue()
  sound_q = queue.Queue()
  system_q = queue.Queue()
  log_q = queue.Queue()
  heal_q = queue.Queue()
  damage_q = queue.Queue()

  # Build initial state
  logging.basicConfig(filename='./log/eqalert.log', level=logging.DEBUG)
  raid = threading.Event()
  cfg_reload = threading.Event()
  heal_parse = threading.Event()
  spell_parse = threading.Event()
  exit_flag = threading.Event()
  config = eqa_config.init()
  chars = eqa_config.get_chars(config)
  char = config["characters"]["default"]
  zone = "unavailable"
  char_log = config["settings"]["paths"]["char_log"] + "eqlog_" + char.title() + "_project1999.txt"

  screen = eqa_curses.init(char, zone)

  ## Consume keyboard events
  ## Produce keyoard_q
  read_keys       = threading.Thread(target=eqa_keys.read,
       args       = (exit_flag, keyboard_q, screen))
  read_keys.daemon = True
  read_keys.start()

  ## Process log_q
  ## Produce action_q
  process_log     = threading.Thread(target=eqa_parser.process,
            args  = (exit_flag, log_q, action_q))
  process_log.daemon = True
  process_log.start()

  ## Process keyboard_q
  ## Produce display_q, sound_q, system_q
  process_keys    = threading.Thread(target=eqa_keys.process,
            args  = (keyboard_q, system_q, display_q, sound_q,
                      exit_flag, heal_parse, spell_parse, raid, chars))
  process_keys.daemon = True
  process_keys.start()

  ## Consume action_q
  ## Produce display_q, sound_q, system_q, heal_q, damage_q
  process_action  = threading.Thread(target=eqa_action.process,
            args  = (action_q, system_q, display_q, sound_q, heal_q, damage_q,
                      exit_flag, heal_parse, spell_parse, raid, cfg_reload, config))
  process_action.daemon = True
  process_action.start()

  ## Consume sound_q
  process_sound   = threading.Thread(target=eqa_sound.process,
            args  = (config, sound_q, exit_flag, cfg_reload))
  process_sound.daemon = True
  process_sound.start()

  ## Consume display_q
  process_display = threading.Thread(target=eqa_curses.display,
            args  = (screen, display_q, zone, char, chars, exit_flag))
  process_display.daemon = True
  process_display.start()

  ## Consume char_log
  ## Produce log_q

  def callback(event):
    try:
      if event.mask == pyinotify.IN_CLOSE_WRITE:
        log_q.put(eqa_parser.last_line(char_log))
    except Exception as e:
      eqa_settings.log('watch callback: ' + str(e))

  log_watch = pyinotify.WatchManager()
  log_watch.add_watch(char_log, pyinotify.IN_CLOSE_WRITE, callback)
  log_notifier = pyinotify.ThreadedNotifier(log_watch)
  log_notifier.daemon = True
  log_notifier.start()

  # And we're on
  display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'draw', 'events', 'null'))
  display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'event', 'events', 'Initialized'))
  sound_q.put(eqa_struct.sound('espeak', 'initialized'))

  ## Consume system_q
  try:
    while not exit_flag.is_set():
      time.sleep(0.001)
      if not system_q.empty():
        new_message = system_q.get()
        system_q.task_done()

        if new_message.type == "system":
          # Update zone
          if new_message.tx == "zone":
            zone = new_message.payload
          # Update character
          elif new_message.tx == "new_character" and not new_message.payload == char:
            # Stop watch on previous character log
            log_watch.rm_watch(char_log, pyinotify.IN_CLOSE_WRITE, callback)
            # Set new character
            char = new_message.payload
            char_log = config["settings"]["paths"]["char_log"] + "eqlog_" + char.title() + "_project1999.txt"
            # Start new log watch
            log_watch.add_watch(char_log, pyinotify.IN_CLOSE_WRITE, callback)
            display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'event', 'events', "Character changed to " + char))
            sound_q.put(eqa_struct.sound('espeak', 'Character changed to ' + char))
          # Reload config
          elif new_message.tx == "reload_config":
            # Reload config
            config = eqa_config.init()
            # Reread characters
            chars = eqa_config.get_chars(config)
            # Stop process_action and process_sound
            cfg_reload.set()
            process_action.join()
            process_sound.join()
            cfg_reload.clear()
            # Start process_action and process_sound
            process_action = threading.Thread(target=eqa_action.process,
                      args = (action_q, system_q, display_q, sound_q, heal_q, damage_q,
                                exit_flag, heal_parse, spell_parse, raid, cfg_reload, config))
            process_action.daemon = True
            process_action.start()
            process_sound  = threading.Thread(target=eqa_sound.process,
                      args = (config, sound_q, exit_flag, cfg_reload))
            process_sound.daemon = True
            process_sound.start()
            display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'event', 'events', 'Configuration reloaded'))
            sound_q.put(eqa_struct.sound('espeak', 'Configuration reloaded'))
        else:
          display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'event', 'events', new_message.type + ': ' + new_message.payload))

  except Exception as e:
    eqa_settings.log('main: ' + str(e))
    pass

  # Exit
  display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'event', 'events', 'Exiting'))
  read_keys.join()
  process_log.join()
  process_keys.join()
  process_action.join()
  process_sound.join()
  process_display.join()
  log_watch.rm_watch(char_log, pyinotify.IN_CLOSE_WRITE, callback)
  log_notifier.stop()
  eqa_curses.close_screens(screen)

if __name__ == '__main__':
  main()
