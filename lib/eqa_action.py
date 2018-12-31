"""
eqalert action
"""

import datetime
import time

import eqa_sound
import eqa_struct
import eqa_settings


def process(config, exit_flag, spell_parse, heal_parse, raid, display_q, sound_q, heal_q, damage_q, action_q, message_q):

  try:
    while not exit_flag.is_set():
      time.sleep(0.1)
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
          undetermined_line(check_line)
        if line_type == "you_new_zone":
          nz_iter = 0
          current_zone = ""
          while check_line_list.index("entered") + nz_iter + 1 < len(check_line_list):
            current_zone += check_line_list[check_line_list.index("entered") + nz_iter + 1] + " "
            nz_iter += 1
          current_zone = current_zone[:-2]
          sound_q.put(eqa_struct.sound('espeak', current_zone))
          if current_zone not in config["zones"].keys():
            eqa_config.add_zone(current_zone)
          elif current_zone in config["zones"].keys() and not raid.is_set():
            if config["zones"][current_zone] == "raid":
              raid.set()
              eqa_settings.log("Raid mode auto-enabled")
              sound_q.put(eqa_struct.sound('espeak', "Raid mode enabled"))
          elif current_zone in config["zones"].keys() and raid.is_set():
            if config["zones"][current_zone] != "raid":
              raid.clear()
              eqa_settings.log("Raid mode auto-disabled")
              sound_q.put(eqa_struct.sound('espeak', "Raid mode disabled"))
          display_q.put(eqa_struct.display('update', 'current_zone', current_zone))

        # If line_type is a parsable type
        if line_type in config["settings"]["check_line_type"].keys():
          # If line_type is parsed for as true
          if config["settings"]["check_line_type"][line_type] == "true":
            for keyphrase, value in config["alert"][line_type].iteritems():
              if str(keyphrase).lower() in check_line and value == "true":
                sound_q.put(eqa_struct.sound('alert', line_type))
                log_alert(line_type, check_line)
              elif str(keyphrase).lower() in check_line and value == "raid" and raid.is_set():
                if keyphrase == 'assist' or keyphrase == 'rampage':
                  payload = keyphrase + ' on ' + check_line_list[0]
                else:
                  payload = keyphrase
                sound_q.put(eqa_struct.sound('espeak', payload))
                log_alert(line_type, check_line)

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
              log_alert(line_type, check_line)

          # Or if line_type is parsed for as a spoken alert
          elif config["settings"]["check_line_type"][line_type] == "speak":
            eqa_settings.log("espeak: " + check_line)
            sound_q.put(eqa_struct.sound('espeak', check_line))

          # For triggers requiring all line_types
          if config["settings"]["check_line_type"]["all"] == "true":
            for keyphrase, value in config["alert"]["all"].iteritems():
              if keyphrase in check_line:
                sound_q.put(eqa_struct.sound('alert', line_type))
                log_alert(line_type, check_line)

        # If line_type is not a parsable type
        else:
          eqa_config.add_type(line_type)
          eqa_settings.log('Added: ' + line_type)
          config = eqa_config.read()

  except Exception as e:
    eqa_settings.log(e)


def log_alert(line_type, check_line):
  """Logs an alert and refreshs display"""
  ## Seperated to maybe log line types differently
  eqa_settings.log(line_type + ": " + check_line[0:65])


def undetermined_line(line):
  """Temp function to log undetermined log lines"""
  f = open('./log/undetermined.txt', 'a')
  f.write(line + '\n')
  f.close()


def save_parse(healed, sdamaged, current_zone):
  """Save contents of healed and sdamaged to file"""
  eqa_log = "./log/eqa_" + current_zone + "_" + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H:%M:%S') + ".log"
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
