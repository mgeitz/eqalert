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


def init(base_path):
  """Read in config.json"""

  if not os.path.isfile(base_path + 'config.json'):
    build_config(base_path)
  json_data = open(base_path + 'config.json', 'r')
  config = json.load(json_data)

  json_data.close()
  return config


def get_chars(config, base_path):
  """Return known characters"""

  chars = []
  log_files = [ f for f in os.listdir(config["settings"]["paths"]["char_log"]) if os.path.isfile(os.path.join(config["settings"]["paths"]["char_log"],f)) ]
  for logs in log_files:
    if "eqlog_" in logs and "_project1999.txt" in logs:
      first, name, end = logs.split("_")
      if name.lower() not in config["characters"].keys():
        add_char(name.lower(), chars, base_path)

  for toon in config["characters"].keys():
    if toon != "default":
      chars.append(toon)
  for toon in config["characters"].keys():
    if config["characters"][toon] == "false":
      chars.remove(toon)

    return chars


def add_char(name, chars, base_path):
  """Adds a new character to the config"""

  json_data = open(base_path + 'config.json', 'r+')
  data = json.load(json_data)
  data["characters"].update({name.lower():"true"})
  chars.append(name.lower())
  json_data.seek(0)
  json.dump(data, json_data, indent = 4)
  json_data.close()


def add_type(line_type, base_path):
  """Adds default setting values for new line_type"""

  json_data = open(base_path + 'config.json', 'r+')
  data = json.load(json_data)
  data["settings"]["sound_settings"].update({line_type:"0"})
  data["settings"]["check_line_type"].update({line_type:"true"})
  data["alert"].update({line_type:dict()})
  json_data.seek(0)
  json.dump(data, json_data, indent = 4)
  json_data.close()


def add_zone(zone, base_path):
  """Adds default setting values for new zones"""

  json_data = open(base_path + 'config.json', 'r+')
  data = json.load(json_data)
  data["zones"].update({zone:"false"})
  json_data.seek(0)
  json.dump(data, json_data, indent = 4)
  json_data.close()


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
    "alert": {
        "mysterious_oner": {},
        "all": {},
        "you_new_zone": {},
        "group_invite": {},
        "emote_cheer": {},
        "you_ooc": {},
        "random": {},
        "auction_wtb": {},
        "melee_miss": {},
        "say": {},
        "spell_break_charm": {},
        "you_tell": {},
        "you_afk_on": {},
        "auction_wts": {
            "block of velium": "true"
        },
        "emote_bow": {},
        "loc": {},
        "group": {
            "invis": "true"
        },
        "you_thirsty": {},
        "emote_bonk": {},
        "emote_thank": {},
        "shout": {},
        "you_outdrinklowfood": {},
        "you_outdrink": {},
        "you_auction_wts": {},
        "you_healed": {},
        "you_say": {},
        "spell_fizzle": {},
        "tell": {},
        "emote_smile": {},
        "spell_something": {},
        "spell_interrupted": {},
        "ooc": {},
        "who_player": {},
        "you_outfoodlowdrink": {},
        "spell_begin_casting": {},
        "zoning": {},
        "you_outfooddrink": {},
        "who_player_afk": {},
        "who_line": {},
        "who_total": {},
        "target_cured": {},
        "you_auction_wtb": {},
        "emote_dance": {},
        "you_lfg_off": {},
        "spell_invis": {},
        "undetermined": {},
        "you_guild": {},
        "you_shout": {},
        "engage": {},
        "guild": {
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
        },
        "target": {},
        "spell_damage": {},
        "you_hungry": {},
        "dot_damage": {},
        "auction": {},
        "you_afk_off": {},
        "you_group": {},
        "you_auction": {},
        "spell_break_ensare": {},
        "who_top": {},
        "emote_wave": {},
        "you_outfood": {},
        "you_lfg_on": {},
        "spell_break": {},
        "melee_hit": {},
        "faction_line": {},
        "spell_resist": {},
        "spell_regen": {}
    },
    "characters": {
        "default": "change",
        "change": "true"
    },
    "settings": {
        "paths": {
            "sound": "%ssound/",
            "alert_log": "%slog/",
            "char_log": "%s/.wine/drive_c/Program Files/Sony/EverQuest/Logs/"
        },
        "sound_settings": {
            "mysterious_oner": "0",
            "all": "0",
            "you_new_zone": "0",
            "group_invite": "3",
            "emote_cheer": "0",
            "you_ooc": "0",
            "random": "0",
            "auction_wtb": "0",
            "melee_miss": "0",
            "say": "1",
            "spell_break_charm": "4",
            "you_tell": "0",
            "you_afk_on": "0",
            "auction_wts": "2",
            "emote_bow": "0",
            "loc": "0",
            "group": "3",
            "you_thirsty": "0",
            "emote_bonk": "0",
            "emote_thank": "0",
            "shout": "1",
            "you_outdrinklowfood": "0",
            "you_outdrink": "0",
            "you_auction_wts": "0",
            "you_healed": "0",
            "you_say": "0",
            "spell_fizzle": "0",
            "tell": "1",
            "emote_smile": "0",
            "spell_something": "0",
            "spell_interrupted": "2",
            "ooc": "1",
            "who_player": "0",
            "you_outfoodlowdrink": "0",
            "spell_begin_casting": "0",
            "zoning": "0",
            "you_outfooddrink": "0",
            "who_player_afk": "0",
            "who_line": "0",
            "who_total": "0",
            "target_cured": "5",
            "you_auction_wtb": "0",
            "emote_dance": "0",
            "you_lfg_off": "0",
            "spell_invis": "0",
            "undetermined": "0",
            "you_guild": "0",
            "you_shout": "0",
            "engage": "0",
            "guild": "3",
            "target": "3",
            "spell_damage": "0",
            "you_hungry": "0",
            "dot_damage": "0",
            "auction": "0",
            "you_afk_off": "0",
            "you_group": "0",
            "you_auction": "0",
            "spell_break_ensare": "3",
            "who_top": "0",
            "emote_wave": "0",
            "you_outfood": "0",
            "you_lfg_on": "0",
            "spell_break": "4",
            "melee_hit": "2",
            "faction_line": "0",
            "spell_resist": "0",
            "spell_regen": "0"
        },
        "sounds": {
            "1": "hey.wav",
            "3": "look.wav",
            "2": "listen.wav",
            "5": "hello.wav",
            "4": "watchout.wav"
        },
        "check_line_type": {
            "mysterious_oner": "false",
            "all": "false",
            "you_new_zone": "all",
            "group_invite": "speak",
            "emote_cheer": "false",
            "you_ooc": "false",
            "random": "false",
            "auction_wtb": "false",
            "melee_miss": "false",
            "say": "true",
            "spell_break_charm": "speak",
            "you_tell": "false",
            "you_afk_on": "false",
            "auction_wts": "true",
            "emote_bow": "false",
            "loc": "false",
            "group": "true",
            "you_thirsty": "false",
            "emote_bonk": "false",
            "emote_thank": "false",
            "shout": "false",
            "you_outdrinklowfood": "false",
            "you_outdrink": "false",
            "you_auction_wts": "false",
            "you_healed": "all",
            "you_say": "false",
            "spell_fizzle": "false",
            "tell": "speak",
            "emote_smile": "false",
            "spell_something": "false",
            "spell_interrupted": "false",
            "ooc": "false",
            "who_player": "false",
            "you_outfoodlowdrink": "false",
            "spell_begin_casting": "false",
            "zoning": "false",
            "you_outfooddrink": "false",
            "who_player_afk": "false",
            "who_line": "false",
            "who_total": "false",
            "target_cured": "all",
            "you_auction_wtb": "false",
            "emote_dance": "true",
            "you_lfg_off": "false",
            "spell_invis": "false",
            "undetermined": "false",
            "you_guild": "false",
            "you_shout": "false",
            "engage": "speak",
            "guild": "true",
            "target": "false",
            "spell_damage": "all",
            "you_hungry": "false",
            "dot_damage": "all",
            "auction": "false",
            "you_afk_off": "false",
            "you_group": "true",
            "you_auction": "false",
            "spell_break_ensare": "all",
            "who_top": "false",
            "emote_wave": "false",
            "you_outfood": "false",
            "you_lfg_on": "false",
            "spell_break": "false",
            "melee_hit": "false",
            "faction_line": "false",
            "spell_resist": "true",
            "spell_regen": "true"
        }
    }
}
"""

  print(new_config % (base_path, base_path, home), file=open(base_path + 'config.json', 'a'))

if __name__ == '__main__':
  main()
