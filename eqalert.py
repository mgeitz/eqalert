#! /usr/bin/env python

"""
Parse, display, alert via eqlog
"""

import curses
import logging
import datetime
import time
import threading
import Queue
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

__author__ = "Michael Geitz"
__version__ = "0.2.2"


def main():
  """Main method, does the good stuff"""

  # Queues
  keyboard_q = Queue.Queue()
  action_q = Queue.Queue()
  display_q = Queue.Queue()
  sound_q = Queue.Queue()
  system_q = Queue.Queue()
  log_q = Queue.Queue()
  heal_q = Queue.Queue()
  damage_q = Queue.Queue()

  # Build initial state
  logging.basicConfig(filename='./log/eqalert.log', level=logging.DEBUG)
  raid = threading.Event()
  stop_watcher = threading.Event()
  heal_parse = threading.Event()
  spell_parse = threading.Event()
  exit_flag = threading.Event()
  config, chars = eqa_config.init()
  char = config["characters"]["default"]
  zone = "unavailable"
  char_log = config["settings"]["paths"]["char_log"] + "eqlog_" + char.title() + "_project1999.txt"

  screen = eqa_curses.init(char, zone)

  ## Produce keyoard_q
  read_keys        = threading.Thread(target=eqa_keys.read,
            args   = (exit_flag, keyboard_q, screen))
  read_keys.daemon = True
  read_keys.start()

  ## Produce log_q
  read_log         = threading.Thread(target=eqa_parser.watch,
            args   = (stop_watcher, char_log, log_q))
  read_log.daemon = True
  read_log.start()

  ## Process log_q
  process_log      = threading.Thread(target=eqa_parser.process,
            args   = (exit_flag, log_q, action_q))
  process_log.daemon = True
  process_log.start()

  ## Process keyboard_q
  ## Produce system_q, display_q, keyboard_q
  process_keys     = threading.Thread(target=eqa_keys.process,
            args   = (display_q, sound_q, keyboard_q, heal_q, damage_q,
                      system_q, exit_flag, heal_parse, spell_parse, raid))
  process_keys.daemon = True
  process_keys.start()

  ## Consume action_q
  ## Produce display_q, sound_q, system_q, heal_q, damage_q
  process_action   = threading.Thread(target=eqa_action.process,
            args   = (config, display_q, sound_q, heal_q, damage_q, action_q,
                      system_q, exit_flag, heal_parse, spell_parse, raid))
  process_action.daemon = True
  process_action.start()

  ## Consume sound_q
  process_sound    = threading.Thread(target=eqa_sound.process,
            args   = (config, sound_q, exit_flag))
  process_sound.daemon = True
  process_sound.start()

  ## Consume display_q
  process_display  = threading.Thread(target=eqa_curses.display,
            args = (screen, display_q, zone, char, chars, exit_flag))
  process_display.daemon = True
  process_display.start()

  display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'draw', 'events', 'null'))
  display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'event', 'events', 'Initialized'))
  sound_q.put(eqa_struct.sound('espeak', 'initialized'))

  ## Consume system_q
  ## Produce action_q
  try:
    while not exit_flag.is_set():
      time.sleep(0.001)
      if not system_q.empty():
        new_message = system_q.get()
        system_q.task_done()

        if new_message.type == "system":
          if new_message.tx == "zone":
            zone = new_message.payload
          elif new_message.tx == "new_character" and not new_message.payload == char:
            char = new_message.payload
            char_log = config["settings"]["paths"]["char_log"] + "eqlog_" + char.title() + "_project1999.txt"
            stop_watcher.set()
            read_log.join()
            read_log = threading.Thread(target=eqa_parser.monitor,
                args = (stop_watcher, char_log, message))
            read_log.daemon = True
            read_log.start()
            display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'event', 'events', "Character changed to " + char))
            sound_q.put(eqa_struct.sound('espeak', 'Character changed to ' + char))
          elif new_message.tx == "reload_config":
            config = eqa_conifig.init()
            sound_q.put(eqa_struct.sound('espeak', 'Configuration reloaded'))
        else:
          display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'event', 'events', new_message.type + ': ' + new_message.payload))

  except Exception as e:
    eqa_settings.log('main: ' + str(e))
    pass

  display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'event', 'events', 'Exiting'))
  stop_watcher.set()

  process_keys.join()
  process_log.join()
  read_log.join()
  read_keys.join()
  process_action.join()
  process_sound.join()
  process_display.join()

  eqa_curses.close_screens(screen)

if __name__ == '__main__':
  main()
