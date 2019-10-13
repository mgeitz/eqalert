#! /usr/bin/env python

"""
   Program:   EQ Alert
   File Name: eqa_config.py
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

import json
import datetime
import os
import sys

import eqa.lib.eqa_settings as eqa_settings
import eqa.lib.eqa_state as eqa_state

def init(base_path):
  """If there is no config, make a config"""
  try:
    if not os.path.isfile(base_path + 'config.json'):
      build_config(base_path)

  except Exception as e:
    eqa_settings.log('config init: Error on line ' +
                      str(sys.exc_info()[-1].tb_lineno) + ': ' + str(e))


def read_config(base_path):
  """read the config"""
  try:
    json_data = open(base_path + 'config.json', 'r')
    config = json.load(json_data)
    json_data.close()

    return config

  except Exception as e:
    eqa_settings.log('config read: Error on line ' +
                      str(sys.exc_info()[-1].tb_lineno) + ': ' + str(e))


def update_logs(base_path):
  """Add characters and servers of eqemu_ prefixed files in the log path"""
  try:
    json_data = open(base_path + 'config.json', 'r')
    config = json.load(json_data)
    json_data.close()
    log_files = [ f for f in os.listdir(config["settings"]["paths"]["char_log"]) if os.path.isfile(os.path.join(config["settings"]["paths"]["char_log"],f)) ]

    for logs in log_files:
      if "eqlog_" in logs:
        emu, middle, end = logs.split("_")
        server_name = end.lower().split('.')[0]
        char_name = middle.lower()
        char_server = char_name + '_' + server_name
        if char_server not in config["char_logs"].keys():
          add_char_log(char_name, server_name, base_path)


  except Exception as e:
    eqa_settings.log('set config chars: Error on line ' +
                      str(sys.exc_info()[-1].tb_lineno) + ': ' + str(e))


def add_char_log(char, server, base_path):
  """Adds a new character to the config"""
  try:
    json_data = open(base_path + 'config.json', 'r+')
    data = json.load(json_data)
    char_server = char + '_' + server
    char_log = 'eqlog_' + char.title() + '_' + server + '.txt'
    if not data["char_logs"]:
      json_data.close()
      bootstrap_state(base_path, char, server)
      json_data = open(base_path + 'config.json', 'r+')
      data = json.load(json_data)
    data["char_logs"].update({char_server:{'char': char, 'server': server, 'file_name': char_log, 'disabled': 'false'}})
    json_data.seek(0)
    json.dump(data, json_data, indent = 2)
    json_data.close()

  except Exception as e:
    eqa_settings.log('add char: Error on line ' +
                      str(sys.exc_info()[-1].tb_lineno) + ': ' + str(e))


def bootstrap_state(base_path, char, server):
  """Generate and save state to config"""

  try:
    json_data = open(base_path + 'config.json', 'r+')
    data = json.load(json_data)
    data["last_state"].update({'server': server, 'character': char, 'zone': 'unavailable', 'location': {'x': '0.00', 'y': '0.00', 'z': '0.00'}, 'direction': 'unavailable', 'afk': 'false'})
    json_data.seek(0)
    json.dump(data, json_data, indent = 2)
    json_data.close()

  except Exception as e:
    eqa_settings.log('bootstrap state: Error on line ' +
                      str(sys.exc_info()[-1].tb_lineno) + ': ' + str(e))


def get_config_chars(config, server):
  """Return characters in the config of given server"""
  try:
    chars = []
    for char_server in config["char_logs"].keys():
      if config["char_logs"][char_server]["server"] == server and config["char_logs"][char_server]["disabled"] == 'false':
        chars.append(config["char_logs"][char_server]["char"])

    return chars

  except Exception as e:
    eqa_settings.log('get config chars: Error on line ' +
                      str(sys.exc_info()[-1].tb_lineno) + ': ' + str(e))


def get_config_servers(config):
  """Return all servers from the config"""

  try:
    servers = []
    for char_server in config["char_logs"].keys():
      if config["char_logs"][char_server]["server"] not in servers and config["char_log"][char_server]["disabled"] == 'false':
        servers.append(server)

    return servers

  except Exception as e:
    eqa_settings.log('get config servers: Error on line ' +
                      str(sys.exc_info()[-1].tb_lineno) + ': ' + str(e))


def set_last_state(state, base_path):
  """Save state to config"""

  try:
    json_data = open(base_path + 'config.json', 'r+')
    data = json.load(json_data)
    data["last_state"].update({"server":state.server})
    data["last_state"].update({"character":state.char})
    data["last_state"].update({"zone":state.zone})
    data["last_state"].update({"location":{'y': str(state.loc[0]), 'x': str(state.loc[1]), 'z': str(state.loc[2])}})
    data["last_state"].update({"direction":state.direction})
    data["last_state"].update({"afk":state.afk})
    json_data.seek(0)
    json.dump(data, json_data, indent = 2)
    json_data.close()

  except Exception as e:
    eqa_settings.log('set last state: Error on line ' +
                      str(sys.exc_info()[-1].tb_lineno) + ': ' + str(e))


def get_last_state(base_path):
  """Load state from config"""

  try:
    # Read config
    json_data = open(base_path + 'config.json', 'r')
    data = json.load(json_data)
    json_data.close()

    # Populate State
    server = data["last_state"]["server"]
    chars = get_config_chars(data, server)
    char = data["last_state"]["character"]
    zone = data["last_state"]["zone"]
    location = [float(data["last_state"]["location"]["y"]), float(data["last_state"]["location"]["x"]), float(data["last_state"]["location"]["z"])]
    direction = data["last_state"]["direction"]
    afk = data["last_state"]["afk"]

    state = eqa_state.EQA_State(char, chars, zone, location, direction, afk, server)

    return state

  except Exception as e:
    eqa_settings.log('get last state: Error on line ' +
                      str(sys.exc_info()[-1].tb_lineno) + ': ' + str(e))


def add_type(line_type, base_path):
  """Adds default setting values for new line_type"""

  try:
    json_data = open(base_path + 'config.json', 'r+')
    data = json.load(json_data)
    data["line"].update({line_type:{'sound': '0', 'reaction': 'false', 'alert': {}}})
    json_data.seek(0)
    json.dump(data, json_data, indent = 2)
    json_data.close()

  except Exception as e:
    eqa_settings.log('add type: Error on line ' +
                      str(sys.exc_info()[-1].tb_lineno) + ': ' + str(e))


def add_zone(zone, base_path):
  """Adds default setting values for new zones"""

  try:
    json_data = open(base_path + 'config.json', 'r+')
    data = json.load(json_data)
    data["zones"].update({zone:"false"})
    json_data.seek(0)
    json.dump(data, json_data, indent = 2)
    json_data.close()

  except Exception as e:
    eqa_settings.log('add zone: Error on line ' +
                      str(sys.exc_info()[-1].tb_lineno) + ': ' + str(e))


def build_config(base_path):
  """Build a default config"""

  home = os.path.expanduser("~")

  new_config = """
{
  "zones": {
    "rivervale": "false",
    "the feerrott": "false",
    "mines of nurga": "false",
    "crushbone": "false",
    "lake of ill omen": "false",
    "befallen": "false",
    "everfrost": "false",
    "infected paw": "false",
    "dragon necropolis": "false",
    "high keep": "false",
    "east freeport": "false",
    "lavastorm mountains": "false",
    "east commonlands": "false",
    "great divide": "false",
    "the city of mist": "false",
    "surefall glade": "false",
    "guk": "false",
    "kedge keep": "false",
    "field of bone": "false",
    "west freeport": "false",
    "butcherblock mountains": "false",
    "rathe mountains": "false",
    "the hole": "false",
    "karnor's castle": "false",
    "plane of hate": "raid",
    "kithicor woods": "false",
    "southern felwithe": "false",
    "steamfont mountains": "false",
    "eastern plains of karana": "false",
    "temple of droga": "false",
    "permafrost caverns": "false",
    "paineel": "false",
    "firiona vie": "false",
    "ocean of tears": "false",
    "trakanon's teeth": "false",
    "sleepers tomb": "false",
    "city of thurgadin": "false",
    "oasis of marr": "false",
    "iceclad ocean": "false",
    "north freeport": "false",
    "nagafen's lair": "false",
    "the burning wood": "false",
    "estate of unrest": "false",
    "velketor's labyrinth": "false",
    "warrens": "false",
    "dagnor's cauldron": "false",
    "howling stones": "false",
    "the wakening lands": "false",
    "lesser faydark": "false",
    "the arena": "false",
    "ruins of old guk": "false",
    "the overthere": "false",
    "toxxulia forest": "false",
    "chardok": "false",
    "skyshrine": "false",
    "lost temple of cazic-thule": "false",
    "northern plains of karana": "false",
    "innothule swamp": "false",
    "sirens grotto": "false",
    "plane of fear": "raid",
    "northern felwithe": "false",
    "plane of growth": "false",
    "kael drakkel": "false",
    "western wastelands": "false",
    "skyfire mountains": "false",
    "the nektulos forest": "false",
    "southern desert of ro": "false",
    "crystal caverns": "false",
    "an arena (pvp) area": "false",
    "qeynos hills": "false",
    "south kaladim": "false",
    "the emerald jungle": "false",
    "greater faydark": "false",
    "timorous deep": "false",
    "kurn's tower": "false",
    "icewell keep": "raid",
    "west commonlands": "false",
    "eastern wastelands": "false",
    "cobalt scar": "false",
    "misty thicket": "false",
    "blackburrow": "false",
    "southern plains of karana": "false",
    "erudin": "false",
    "western plains of karana": "false",
    "erudin palace": "false",
    "plane of air": "false",
    "dreadlands": "false",
    "highpass hold": "false",
    "temple of veeshan": "raid",
    "veeshan's peak": "raid",
    "old sebilis": "false",
    "plane of mischief": "false",
    "frontier mountains": "false",
    "castle mistmoore": "false",
    "northern desert of ro": "false",
    "lake rathetear": "false"
  },
  "line": {
    "mysterious_oner": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "all": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "you_new_zone": {
      "sound": "0",
      "reaction": "all",
      "alert": {}
    },
    "group_invite": {
      "sound": "0",
      "reaction": "speak",
      "alert": {}
    },
    "emote_cheer": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "you_ooc": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "random": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "auction_wtb": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "melee_miss": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "say": {
      "sound": "0",
      "reaction": "true",
      "alert": {
        "help": "true"
      }
    },
    "spell_break_charm": {
      "sound": "0",
      "reaction": "speak",
      "alert": {}
    },
    "you_tell": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "you_afk_on": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "auction_wts": {
      "sound": "3",
      "reaction": "true",
      "alert": {
        "spiderling silk": "true"
      }
    },
    "emote_bow": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "group": {
      "sound": "4",
      "reaction": "true",
      "alert": {
        "help": "true",
        "inc": "true",
        "incoming": "true"
      }
    },
    "you_thirsty": {
      "sound": "0",
      "reaction": "speak",
      "alert": {}
    },
    "emote_bonk": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "emote_thank": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "shout": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "you_outdrinklowfood": {
      "sound": "0",
      "reaction": "speak",
      "alert": {}
    },
    "you_outdrink": {
      "sound": "0",
      "reaction": "speak",
      "alert": {}
    },
    "you_auction_wts": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "you_healed": {
      "sound": "0",
      "reaction": "all",
      "alert": {}
    },
    "you_say": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "spell_fizzle": {
      "sound": "5",
      "reaction": "true",
      "alert": {}
    },
    "tell": {
      "sound": "0",
      "reaction": "speak",
      "alert": {}
    },
    "emote_smile": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "spell_something": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "spell_interrupted": {
      "sound": "2",
      "reaction": "true",
      "alert": {}
    },
    "ooc": {
      "sound": "1",
      "reaction": "false",
      "alert": {}
    },
    "who_player": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "you_outfoodlowdrink": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "spell_begin_casting": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "zoning": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "you_outfooddrink": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "who_player_afk": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "who_line": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "who_total": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "target_cured": {
      "sound": "0",
      "reaction": "speak",
      "alert": {}
    },
    "you_auction_wtb": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "emote_dance": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "you_lfg_off": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "spell_invis": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "undetermined": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "you_guild": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "you_shout": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "engage": {
      "sound": "0",
      "reaction": "speak",
      "alert": {}
    },
    "guild": {
      "sound": "3",
      "reaction": "true",
      "alert": {
        "tash": "raid",
        "fixated": "raid",
        "slow": "raid",
        "rampage": "raid",
        "malo": "raid",
        "fixation": "raid",
        "occlusion": "raid",
        "assist": "raid",
        "sunder": "raid",
        "malosini": "raid"
      }
    },
    "target": {
      "sound": "3",
      "reaction": "false",
      "alert": {}
    },
    "spell_damage": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "you_hungry": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "dot_damage": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "auction": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "you_afk_off": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "you_group": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "you_auction": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "spell_break_ensare": {
      "sound": "0",
      "reaction": "speak",
      "alert": {}
    },
    "who_top": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "emote_wave": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "you_outfood": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "you_lfg_on": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "spell_break": {
      "sound": "4",
      "reaction": "false",
      "alert": {}
    },
    "melee_hit": {
      "sound": "2",
      "reaction": "false",
      "alert": {}
    },
    "faction_line": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "spell_resist": {
      "sound": "0",
      "reaction": "speak",
      "alert": {}
    },
    "spell_regen": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "location": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "direction": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    },
    "direction_miss": {
      "sound": "0",
      "reaction": "false",
      "alert": {}
    }
  },
  "last_state": {},
  "char_logs": {},
  "settings": {
    "paths": {
      "sound": "%ssound/",
      "alert_log": "%slog/",
      "char_log": "%s/.wine/drive_c/Program Files/Sony/EverQuest/Logs/"
    },
    "sounds": {
      "1": "hey.wav",
      "3": "look.wav",
      "2": "listen.wav",
      "5": "hello.wav",
      "4": "watch out.wav"
    }
  }
}
"""

  try:
    f = open(base_path + 'config.json', 'w')
    f.write(new_config % (base_path, base_path, home))
    f.close()

  except Exception as e:
    eqa_settings.log('build config: Error on line' +
                      str(sys.exc_info()[-1].tb_lineno) + ': ' + str(e))

if __name__ == '__main__':
  main()
