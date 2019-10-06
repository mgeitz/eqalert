#! /usr/bin/env python

"""
   Program:   EQ Alert
   File Name: eqa_action.py
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

import datetime
import time
import sys

import lib.eqa_sound as eqa_sound
import lib.eqa_struct as eqa_struct
import lib.eqa_settings as eqa_settings
import lib.eqa_config as eqa_config


def process(action_q, system_q, display_q, sound_q, heal_q, damage_q, exit_flag,
            heal_parse, spell_parse, raid, cfg_reload, config, base_path):
  """
    Process: action_q
    Produce: sound_q, display_q, system_q, heal_q, damage_q
  """

  try:
    while not exit_flag.is_set() and not cfg_reload.is_set():
      time.sleep(0.001)
      if not action_q.empty():
        new_message = action_q.get()
        action_q.task_done()
        line_type = new_message.type
        line_time = new_message.timestamp
        line_tx = new_message.tx
        line_rx = new_message.rx
        check_line = new_message.payload
        check_line_list = new_message.payload.split(' ')

        # Line specific checks
        if line_type == "undetermined":
          undetermined_line(check_line, base_path)
        if line_type.startswith("you_afk"):
          if line_type == "you_afk_on":
            display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'event', 'events', 'You are now AFK'))
            system_q.put(eqa_struct.message(eqa_settings.eqa_time(), 'system', 'afk', 'null', 'true'))
          elif line_type == "you_afk_off":
            display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'event', 'events', 'You are no longer AFK'))
            system_q.put(eqa_struct.message(eqa_settings.eqa_time(), 'system', 'afk', 'null', 'false'))
        if line_type == "you_new_zone":
          nz_iter = 0
          current_zone = ""
          while check_line_list.index("entered") + nz_iter + 1 < len(check_line_list):
            current_zone += check_line_list[check_line_list.index("entered") + nz_iter + 1] + " "
            nz_iter += 1
          current_zone = current_zone[:-2]
          current_zone = current_zone.rstrip('.')
          sound_q.put(eqa_struct.sound('espeak', current_zone))
          display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'update', 'zone', current_zone))
          system_q.put(eqa_struct.message(eqa_settings.eqa_time(), 'system', 'zone', 'null', current_zone))
          if current_zone not in config["zones"].keys():
            eqa_config.add_zone(current_zone, base_path)
          elif current_zone in config["zones"].keys() and not raid.is_set():
            if config["zones"][current_zone] == "raid":
              raid.set()
              display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'event', 'events', 'Raid mode auto-enabled'))
              sound_q.put(eqa_struct.sound('espeak', 'Raid mode enabled'))
          elif current_zone in config["zones"].keys() and raid.is_set():
            if config["zones"][current_zone] != "raid":
              raid.clear()
              display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'event', 'events', 'Raid mode auto-disabled'))
              sound_q.put(eqa_struct.sound('espeak', "Raid mode disabled"))

        # If line_type is a parsable type
        if line_type in config["settings"]["check_line_type"].keys():
          # If line_type is parsed for as true
          if config["settings"]["check_line_type"][line_type] == "true":
            for keyphrase, value in config["alert"][line_type].items():
              if str(keyphrase).lower() in check_line and value == "true":
                sound_q.put(eqa_struct.sound('alert', line_type))
                display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'event', 'events', line_type + ': ' + check_line[0:65]))
              elif str(keyphrase).lower() in check_line and value == "raid" and raid.is_set():
                if keyphrase == 'assist' or keyphrase == 'rampage':
                  payload = keyphrase + ' on ' + check_line_list[0]
                else:
                  payload = keyphrase
                sound_q.put(eqa_struct.sound('espeak', payload))
                display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'event', 'events', line_type + ': ' + check_line[0:65]))

          # Or if line_type is parsed for as all
          elif config["settings"]["check_line_type"][line_type] == "all":
            # Heal parse
            if heal_parse.is_set() and line_type == "you_healed":
              heal_q.put(eqa_struct.heal(datetime.datetime.now(), 'heal', 'you', check_line_list[3], check_line_list[5]))

            # Spell damage parse
            elif spell_parse.is_set() and line_type == "spell_damage":
              length = check_line_list.index('was')
              sp_iter = 0
              name = ""
              while sp_iter < length:
                name = name + check_line_list[sp_iter] + " "
                sp_iter += 1
              damaged_q.put(eqa_struct.heal(datetime.datetime.now(), 'spell', 'null', name, check_line_list[-4]))

            # DoT damage parse
            elif spell_parse.is_set() and line_type == "dot_damage":
              length = check_line_list.index('has')
              dp_iter = 0
              name = ""
              damage = int(check_line_list[length + 2])
              while dp_iter < length:
                name = name + check_line_list[dp_iter] + " "
                dp_iter += 1
              damaged_q.put(eqa_struct.heal(datetime.datetime.now(), 'dot', 'null', name, damage))

            # Notify on all other all alerts
            else:
              sound_q.put(eqa_struct.sound('alert', line_type))
              display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'event', 'events', line_type + ': ' + check_line[0:65]))

          # Or if line_type is parsed for as a spoken alert
          elif config["settings"]["check_line_type"][line_type] == "speak":
            display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'event', 'events', check_line))
            sound_q.put(eqa_struct.sound('espeak', check_line))

          # For triggers requiring all line_types
          if config["settings"]["check_line_type"]["all"] == "true":
            for keyphrase, value in config["alert"]["all"].items():
              if keyphrase in check_line:
                sound_q.put(eqa_struct.sound('alert', line_type))
                display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'event', 'events', line_type + ': ' + check_line[0:65]))

        # If line_type is not a parsable type
        else:
          eqa_config.add_type(line_type, base_path)
          display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'event', 'events', 'added: ' + line_type))
          config = eqa_config.read()

  except Exception as e:
    eqa_settings.log('process action: Error on line ' +
                      str(sys.exc_info()[-1].tb_lineno) + ': ' +  str(e))

  sys.exit()


def undetermined_line(line, base_path):
  """Temp function to log undetermined log lines"""
  f = open(base_path + 'log/undetermined.txt', 'a')
  f.write(line + '\n')
  f.close()


if __name__ == '__main__':
  main()
