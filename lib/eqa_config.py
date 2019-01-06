"""
eqalert config
"""

import json
import datetime
import os


def init():
  """Read in config.json"""

  json_data = open('config.json', 'r')
  config = json.load(json_data)

  json_data.close()
  return config


def get_chars(config):
  """Return known characters"""

  log_files = [ f for f in os.listdir(config["settings"]["paths"]["char_log"]) if os.path.isfile(os.path.join(config["settings"]["paths"]["char_log"],f)) ]
  for logs in log_files:
    if "eqlog_" in logs and "_project1999.txt" in logs:
      first, name, end = logs.split("_")
      if name.lower() not in config["characters"].keys():
        add_char(name.lower())

  chars = []
  for toon in config["characters"].keys():
    if toon != "default":
      chars.append(toon)
  for toon in config["characters"].keys():
    if config["characters"][toon] == "false":
      chars.remove(toon)

    return chars


def add_char(name):
  """Adds a new character to the config"""

  json_data = open('config.json', 'r+')
  data = json.load(json_data)
  data["characters"].update({name.lower():"true"})
  chars.append(name.lower())
  json_data.seek(0)
  json.dump(data, json_data, indent = 4)
  json_data.close()


def add_type(line_type):
  """Adds default setting values for new line_type"""

  json_data = open('config.json', 'r+')
  data = json.load(json_data)
  data["settings"]["sound_settings"].update({line_type:"0"})
  data["settings"]["check_line_type"].update({line_type:"true"})
  data["alert"].update({line_type:dict()})
  json_data.seek(0)
  json.dump(data, json_data, indent = 4)
  json_data.close()


def add_zone(zone):
  """Adds default setting values for new zones"""

  json_data = open('config.json', 'r+')
  data = json.load(json_data)
  data["zones"].update({zone:"false"})
  json_data.seek(0)
  json.dump(data, json_data, indent = 4)
  json_data.close()
