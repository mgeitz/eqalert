#! /usr/bin/env python

"""
   Program:   EQ Alert
   File Name: eqa/eqalert.py
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

import logging
import os
import pkg_resources
import pyinotify
import sys
import threading
import time
import queue

import eqa.lib.action as eqa_action
import eqa.lib.config as eqa_config
import eqa.lib.curses as eqa_curses
import eqa.lib.keys as eqa_keys
import eqa.lib.parser as eqa_parser
import eqa.lib.settings as eqa_settings
import eqa.lib.sound as eqa_sound
import eqa.lib.state as eqa_state
import eqa.lib.struct as eqa_struct


def bootstrap(base_path):
  """Bootstrap first run"""

  try:
    print("Bootstrapping for first run . . .")

    # Make the main folder
    if not os.path.exists(base_path):
      print("    - putting this stuff in " + base_path)
      os.makedirs(base_path)

    # Make the log folder
    if not os.path.exists(base_path + 'log/'):
      print("    - making a place for logs")
      os.makedirs(base_path + 'log/')

    # Make some sounds
    sound_directory = base_path + 'sound/'
    if not os.path.exists(sound_directory):
      print("    - making some sounds")
      os.makedirs(base_path + 'sound/')
      eqa_sound.speak('hello', 'false', sound_directory)
      eqa_sound.speak('hey', 'false', sound_directory)
      eqa_sound.speak('listen', 'false', sound_directory)
      eqa_sound.speak('look', 'false', sound_directory)
      eqa_sound.speak('watch out', 'false', sound_directory)

    # Generating a config file
    print("    - generating json config")
    eqa_config.init(base_path)
    eqa_config.update_logs(base_path)

  except Exception as e:
    print('Unfortunately, the bootstrap step failed with: ' +
          str(sys.exc_info()[-1].tb_lineno) + ': ' + str(e))
    exit(1)


def main():
  """Main method, does the good stuff"""

  # Paths
  home = os.path.expanduser("~")
  base_path = home + '/.eqa/'

  # Queues
  keyboard_q = queue.Queue()
  action_q = queue.Queue()
  display_q = queue.Queue()
  sound_q = queue.Queue()
  system_q = queue.Queue()
  log_q = queue.Queue()
  heal_q = queue.Queue()
  damage_q = queue.Queue()

  # Bootstraps bootstraps
  if not os.path.exists(base_path + 'config.json'):
    bootstrap(base_path)

  # Thread Events
  raid = threading.Event()
  cfg_reload = threading.Event()
  heal_parse = threading.Event()
  spell_parse = threading.Event()
  exit_flag = threading.Event()

  # Build initial state
  logging.basicConfig(filename=base_path + 'log/eqalert.log', level=logging.INFO)
  eqa_config.update_logs(base_path)
  config = eqa_config.read_config(base_path)
  server = config["last_state"]["server"]
  char = config["last_state"]["character"]
  char_log = config["settings"]["paths"]["char_log"] + config["char_logs"][char + '_' + server]["file_name"]
  state = eqa_config.get_last_state(base_path)

  # Ensure the character log file exists
  if not os.path.exists(char_log):
    print('Please review `settings > paths` in config.json, a log with that default server and character cannot be found.')
    exit(1)

  # Ensure the configuration is up-to-date
  if 'version' not in config["settings"]:
    print('Please move or delete your current configuration. A new config.json file must be generated.')
    exit(1)
  elif not config["settings"]["version"] == str(pkg_resources.get_distribution('eqalert').version):
    print('Please move or delete your current configuration. A new config.json file must be generated.')
    exit(1)

  # Initialize curses
  screen = eqa_curses.init(state)

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
                      exit_flag, heal_parse, spell_parse, raid, state.chars))
  process_keys.daemon = True
  process_keys.start()

  ## Consume action_q
  ## Produce display_q, sound_q, system_q, heal_q, damage_q
  process_action  = threading.Thread(target=eqa_action.process,
            args  = (action_q, system_q, display_q, sound_q, heal_q, damage_q,
                      exit_flag, heal_parse, spell_parse, raid, cfg_reload,
                      config, base_path))
  process_action.daemon = True
  process_action.start()

  ## Consume sound_q
  process_sound   = threading.Thread(target=eqa_sound.process,
            args  = (config, sound_q, exit_flag, cfg_reload))
  process_sound.daemon = True
  process_sound.start()

  ## Consume display_q
  process_display = threading.Thread(target=eqa_curses.display,
            args  = (screen, display_q, state, raid, exit_flag))
  process_display.daemon = True
  process_display.start()

  ## Consume char_log
  ## Produce log_q

  def callback(event):
    try:
      if event.mask == pyinotify.IN_CLOSE_WRITE:
        log_q.put(eqa_parser.last_line(char_log))
    except Exception as e:
      eqa_settings.log('log watch callback: Error on line ' +
                        str(sys.exc_info()[-1].tb_lineno) + ': ' + str(e))

  try:
    log_watch = pyinotify.WatchManager()
    log_watch.add_watch(char_log, pyinotify.IN_CLOSE_WRITE, callback)
    log_notifier = pyinotify.ThreadedNotifier(log_watch)
    log_notifier.daemon = True
    log_notifier.start()
  except Exception as e:
    eqa_settings.log('log watch callback: Error on line ' +
                      str(sys.exc_info()[-1].tb_lineno) + ': ' + str(e))

  # And we're on
  display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'draw', 'events', 'null'))
  display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'event', 'events', 'Initialized'))
  sound_q.put(eqa_struct.sound('speak', 'initialized'))

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
            state.set_zone(new_message.payload)
            eqa_config.set_last_state(state, base_path)
          # Update afk status
          elif new_message.tx == "afk":
            state.set_afk(new_message.payload)
            eqa_config.set_last_state(state, base_path)
          # Update location
          elif new_message.tx == "loc":
            state.set_loc(new_message.payload)
            eqa_config.set_last_state(state, base_path)
          # Update direction
          elif new_message.tx == "direction":
            state.set_direction(new_message.payload)
            eqa_config.set_last_state(state, base_path)
          # Update character
          elif new_message.tx == "new_character":
            new_char_log = config["settings"]["paths"]["char_log"] + config["char_logs"][new_message.payload]["file_name"]
            # Ensure char/server combo exists as file
            if os.path.exists(new_char_log):
              # Stop watch on current log
              log_watch.rm_watch(char_log, pyinotify.IN_CLOSE_WRITE, callback)
              # Set new character
              char_name, char_server = new_message.payload.split('_')
              state.set_char(char_name)
              state.set_server(char_server)
              eqa_config.set_last_state(state, base_path)
              char_log = new_char_log
              # Start new log watch
              log_watch.add_watch(char_log, pyinotify.IN_CLOSE_WRITE, callback)
              display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'event', 'events', "Character changed to " + state.char + ' on ' + state.server))
              sound_q.put(eqa_struct.sound('speak', 'Character changed to ' + state.char + ' on ' + state.server))
            else:
              display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'event', 'events', "Unable to change characters, please review logs"))
              eqa_settings.log('Could not find file: ' + new_char_log)
          # Reload config
          elif new_message.tx == "reload_config":
            # Reload config
            eqa_config.update_logs(base_path)
            config = eqa_config.read_config(base_path)
            # Reread characters
            state.set_chars(eqa_config.get_config_chars(config))
            # Stop process_action and process_sound
            cfg_reload.set()
            process_action.join()
            process_sound.join()
            cfg_reload.clear()
            # Start process_action and process_sound
            process_action  = threading.Thread(target=eqa_action.process,
                      args  = (action_q, system_q, display_q, sound_q, heal_q, damage_q,
                                exit_flag, heal_parse, spell_parse, raid, cfg_reload,
                                config, base_path))
            process_action.daemon = True
            process_action.start()
            process_sound  = threading.Thread(target=eqa_sound.process,
                      args = (config, sound_q, exit_flag, cfg_reload))
            process_sound.daemon = True
            process_sound.start()
            display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'event', 'events', 'Configuration reloaded'))
            sound_q.put(eqa_struct.sound('speak', 'Configuration reloaded'))
        else:
          display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'event', 'events', new_message.type + ': ' + new_message.payload))

  except Exception as e:
    eqa_settings.log('main: Error on line ' +
                      str(sys.exc_info()[-1].tb_lineno) + ': ' + str(e))
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
