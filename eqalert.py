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
import time
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
  message_q = Queue.Queue()
  heal_q = Queue.Queue()
  damage_q = Queue.Queue()

  # Flags
  raid = threading.Event()
  stop_watcher = threading.Event()
  heal_parse = threading.Event()
  spell_parse = threading.Event()
  exit_flag = threading.Event()

  # Logs
  logging.basicConfig(filename='./log/eqalert.log', level=logging.DEBUG)
  eqa_settings.log('Initializing... ' + str(datetime.datetime.now()))
  config = eqa_config.init()
  char = config["characters"]["default"]
  log_path = config["settings"]["paths"]["log"] + "eqlog_" + char.title() + "_project1999.txt"

  # build char menu req?
  chars = []
  for toon in config["characters"].keys():
    if toon != "default":
      chars.append(toon)

  # Remove toons I dont want in char menu
  for toon in config["characters"].keys():
    if config["characters"][toon] == "false":
      chars.remove(toon)

  screen = eqa_curses.init(char, "unavailable")

  ## Produce keyoard_q
  read_keys        = threading.Thread(target=eqa_keys.read,
            args   = (exit_flag, keyboard_q, screen))
  read_keys.daemon = True
  read_keys.start()

  ## Produce message_q
  read_log         = threading.Thread(target=eqa_parser.monitor,
            args   = (stop_watcher, log_path, message_q))
  read_log.daemon = True
  read_log.start()

  ## Consume keyboard_q
  ## Produce display_q, message_q, keyboard_q
  process_keys     = threading.Thread(target=eqa_keys.process,
            args   = (exit_flag, spell_parse, heal_parse, raid, display_q,
                    sound_q, keyboard_q, heal_q, damage_q, message_q))
  process_keys.daemon = True
  process_keys.start()

  ## Consume action_q
  ## Produce display_q, sound_q, message_q, heal_q, damage_q
  process_action   = threading.Thread(target=eqa_action.process,
            args   = (config, exit_flag, spell_parse, heal_parse, raid, display_q,
                    sound_q, heal_q, damage_q, action_q, message_q))
  process_action.daemon = True
  process_action.start()

  ## Consume sound_q
  process_sound    = threading.Thread(target=eqa_sound.process,
            args   = (config, sound_q, exit_flag))
  process_sound.daemon = True
  process_sound.start()

  ## Consume display_q
  process_display  = threading.Thread(target=eqa_curses.display,
            args = (screen, exit_flag, display_q, message_q))
  process_display.daemon = True
  process_display.start()

  display_q.put(eqa_struct.display('update', 'char', char))
  display_q.put(eqa_struct.display('draw', 'all', 'null'))
  sound_q.put(eqa_struct.sound('espeak', 'initialized'))

  ## Consume message_q
  ## Produce action_q
  try:
    while not exit_flag.is_set():
      time.sleep(0.1)
      if not message_q.empty():
        new_message = message_q.get()
        message_q.task_done()

        if new_message.type == "system":
          if new_message.tx == "new_character" and not new_message.payload == char:
            char = new_message.payload
            log_path = config["settings"]["paths"]["log"] + "eqlog_" + char.title() + "_project1999.txt"
            stop_watcher.set()
            read_log.join()
            read_log = threading.Thread(target=eqa_parser.monitor,
                args = (stop_watcher, log_path, message))
            read_log.daemon = True
            read_log.start()
            eqa_settings.log("Character changed to " + char)
            sound_q.put(eqa_struct.sound('espeak', 'Character changed to ' + char))
          elif new_message.tx == "reload_config":
            config = eqa_conifig.init()
            sound_q.put(eqa_struct.sound('espeak', 'Configuration reloaded'))
        else:
          eqa_settings.log(new_message.type + ': ' + new_message.payload)
          display_q.put(eqa_struct.display('draw', 'all', 'null'))
          action_q.put(new_message)

  except Exception as e:
    eqa_settings.log(e)

  stop_watcher.set()

  process_keys.join()
  read_log.join()
  read_keys.join()
  process_action.join()
  process_sound.join()
  process_display.join()

  eqa_curses.close_screens(screen)

if __name__ == '__main__':
  main()
