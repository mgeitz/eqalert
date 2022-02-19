#! /usr/bin/env python

"""
   Program:   EQ Alert
   File Name: eqa/lib/config.py
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
import os
import sys

import eqa.lib.settings as eqa_settings
import eqa.lib.state as eqa_state


def init(base_path):
    """If there is no config, make a config"""
    try:
        if not os.path.isfile(base_path + "config.json"):
            build_config(base_path)

    except Exception as e:
        eqa_settings.log(
            "config init: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def read_config(base_path):
    """read the config"""
    try:
        json_data = open(base_path + "config.json", "r", encoding="utf-8")
        config = json.load(json_data)
        json_data.close()

        return config

    except Exception as e:
        eqa_settings.log(
            "config read: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def update_logs(base_path):
    """Add characters and servers of eqemu_ prefixed files in the log path"""
    try:
        json_data = open(base_path + "config.json", "r", encoding="utf-8")
        config = json.load(json_data)
        json_data.close()
        log_files = [
            f
            for f in os.listdir(config["settings"]["paths"]["char_log"])
            if os.path.isfile(os.path.join(config["settings"]["paths"]["char_log"], f))
        ]

        for logs in log_files:
            if "eqlog_" in logs:
                emu, middle, end = logs.split("_")
                server_name = end.split(".")[0]
                char_name = middle
                char_server = char_name + "_" + server_name
                if char_server not in config["char_logs"].keys():
                    add_char_log(char_name, server_name, base_path)

    except Exception as e:
        eqa_settings.log(
            "set config chars: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def add_char_log(char, server, base_path):
    """Adds a new character to the config"""
    try:
        char_server = char + "_" + server
        char_log = "eqlog_" + char.title() + "_" + server + ".txt"
        json_data = open(base_path + "config.json", "r", encoding="utf-8")
        data = json.load(json_data)
        json_data.close()
        if not data["char_logs"]:
            bootstrap_state(base_path, char, server)

        json_data = open(base_path + "config.json", "r", encoding="utf-8")
        data = json.load(json_data)
        json_data.close()
        data["char_logs"].update(
            {
                char_server: {
                    "char": char,
                    "server": server,
                    "file_name": char_log,
                    "disabled": "false",
                }
            }
        )
        json_data = open(base_path + "config.json", "w", encoding="utf-8")
        json.dump(data, json_data, sort_keys=True, indent=2)
        json_data.close()

    except Exception as e:
        eqa_settings.log(
            "add char: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def bootstrap_state(base_path, char, server):
    """Generate and save state to config"""

    try:
        json_data = open(base_path + "config.json", "r", encoding="utf-8")
        data = json.load(json_data)
        json_data.close()
        data["last_state"].update(
            {
                "server": server,
                "character": char,
                "zone": "unavailable",
                "location": {"x": "0.00", "y": "0.00", "z": "0.00"},
                "direction": "unavailable",
                "afk": "false",
            }
        )
        json_data = open(base_path + "config.json", "w", encoding="utf-8")
        json.dump(data, json_data, sort_keys=True, indent=2)
        json_data.close()

    except Exception as e:
        eqa_settings.log(
            "bootstrap state: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def get_config_chars(config):
    """Return each unique character log"""
    try:
        chars = []
        for char_server in config["char_logs"].keys():
            if config["char_logs"][char_server]["disabled"] == "false":
                chars.append(char_server)

        return chars

    except Exception as e:
        eqa_settings.log(
            "get config chars: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def set_last_state(state, base_path):
    """Save state to config"""

    try:
        json_data = open(base_path + "config.json", "r", encoding="utf-8")
        data = json.load(json_data)
        json_data.close()
        data["last_state"].update(
            {
                "server": state.server,
                "character": state.char,
                "zone": str(state.zone),
                "location": {
                    "x": str(state.loc[1]),
                    "y": str(state.loc[0]),
                    "z": str(state.loc[2]),
                },
                "direction": state.direction,
                "afk": state.afk,
            }
        )
        json_data = open(base_path + "config.json", "w", encoding="utf-8")
        json.dump(data, json_data, sort_keys=True, ensure_ascii=False, indent=2)
        json_data.close()

    except Exception as e:
        eqa_settings.log(
            "set last state: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def get_last_state(base_path):
    """Load state from config"""

    try:
        # Read config
        json_data = open(base_path + "config.json", "r", encoding="utf-8")
        data = json.load(json_data)
        json_data.close()

        # Populate State
        server = data["last_state"]["server"]
        char = data["last_state"]["character"]
        zone = data["last_state"]["zone"]
        location = [
            float(data["last_state"]["location"]["y"]),
            float(data["last_state"]["location"]["x"]),
            float(data["last_state"]["location"]["z"]),
        ]
        direction = data["last_state"]["direction"]
        afk = data["last_state"]["afk"]

        # Get chars
        chars = get_config_chars(data)

        # Populate and return a new state
        state = eqa_state.EQA_State(char, chars, zone, location, direction, afk, server)

        return state

    except Exception as e:
        eqa_settings.log(
            "get last state: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def add_type(line_type, base_path):
    """Adds default setting values for new line_type"""

    try:
        json_data = open(base_path + "config.json", "r", encoding="utf-8")
        data = json.load(json_data)
        json_data.close()
        data["line"].update(
            {line_type: {"sound": "0", "reaction": "false", "alert": {}}}
        )
        json_data = open(base_path + "config.json", "w", encoding="utf-8")
        json.dump(data, json_data, sort_keys=True, indent=2)
        json_data.close()

    except Exception as e:
        eqa_settings.log(
            "add type: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def add_zone(zone, base_path):
    """Adds default setting values for new zones"""

    try:
        json_data = open(base_path + "config.json", "r", encoding="utf-8")
        data = json.load(json_data)
        json_data.close()
        data["zones"].update({zone: "false"})
        json_data = open(base_path + "config.json", "w", encoding="utf-8")
        json.dump(data, json_data, sort_keys=True, indent=2)
        json_data.close()

    except Exception as e:
        eqa_settings.log(
            "add zone: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def build_config(base_path):
    """Build a default config"""

    home = os.path.expanduser("~")

    new_config = """
{
  "char_logs": {},
  "last_state": {},
  "line": {
    "all": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "auction": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "auction_wtb": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "auction_wts": {
      "alert": {
        "spiderling silk": "true"
      },
      "reaction": "true",
      "sound": "3"
    },
    "direction": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "direction_miss": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "dot_damage": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "emote_bonk": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "emote_bow": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "emote_cheer": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "emote_dance": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "emote_smile": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "emote_thank": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "emote_wave": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "engage": {
      "alert": {},
      "reaction": "speak",
      "sound": "0"
    },
    "faction_line": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "group": {
      "alert": {
        "help": "true",
        "inc": "true"
      },
      "reaction": "true",
      "sound": "4"
    },
    "group_invite": {
      "alert": {},
      "reaction": "speak",
      "sound": "0"
    },
    "guild": {
      "alert": {
        "assist": "raid",
        "fixated": "raid",
        "fixation": "raid",
        "malo": "raid",
        "malosini": "raid",
        "occlusion": "raid",
        "rampage": "raid",
        "slow": "raid",
        "sunder": "raid",
        "tash": "raid"
      },
      "reaction": "true",
      "sound": "3"
    },
    "location": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "melee_hit": {
      "alert": {},
      "reaction": "false",
      "sound": "2"
    },
    "melee_miss": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "mysterious_oner": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "ooc": {
      "alert": {},
      "reaction": "false",
      "sound": "1"
    },
    "random": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "say": {
      "alert": {
        "help": "true"
      },
      "reaction": "true",
      "sound": "0"
    },
    "shout": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "spell_begin_casting": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "spell_break": {
      "alert": {},
      "reaction": "false",
      "sound": "4"
    },
    "spell_break_charm": {
      "alert": {},
      "reaction": "speak",
      "sound": "0"
    },
    "spell_break_ensare": {
      "alert": {},
      "reaction": "speak",
      "sound": "0"
    },
    "spell_damage": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "spell_fizzle": {
      "alert": {},
      "reaction": "true",
      "sound": "5"
    },
    "spell_interrupted": {
      "alert": {},
      "reaction": "true",
      "sound": "2"
    },
    "spell_invis": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "spell_regen": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "spell_resist": {
      "alert": {},
      "reaction": "speak",
      "sound": "0"
    },
    "spell_something": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "target": {
      "alert": {},
      "reaction": "false",
      "sound": "3"
    },
    "target_cured": {
      "alert": {},
      "reaction": "speak",
      "sound": "0"
    },
    "tell": {
      "alert": {},
      "reaction": "speak",
      "sound": "0"
    },
    "undetermined": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "who_line": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "who_player": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "who_player_afk": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "who_top": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "who_total": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "you_afk_off": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "you_afk_on": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "you_auction": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "you_auction_wtb": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "you_auction_wts": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "you_group": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "you_guild": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "you_healed": {
      "alert": {},
      "reaction": "all",
      "sound": "0"
    },
    "you_hungry": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "you_lfg_off": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "you_lfg_on": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "you_new_zone": {
      "alert": {},
      "reaction": "all",
      "sound": "0"
    },
    "you_ooc": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "you_outdrink": {
      "alert": {},
      "reaction": "speak",
      "sound": "0"
    },
    "you_outdrinklowfood": {
      "alert": {},
      "reaction": "speak",
      "sound": "0"
    },
    "you_outfood": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "you_outfooddrink": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "you_outfoodlowdrink": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "you_say": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "you_shout": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "you_tell": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    },
    "you_thirsty": {
      "alert": {},
      "reaction": "speak",
      "sound": "0"
    },
    "zoning": {
      "alert": {},
      "reaction": "false",
      "sound": "0"
    }
  },
  "settings": {
    "paths": {
      "alert_log": "%slog/",
      "char_log": "%s/.wine/drive_c/Program Files/Sony/EverQuest/Logs/",
      "sound": "%ssound/"
    },
    "sounds": {
      "1": "hey.wav",
      "2": "listen.wav",
      "3": "look.wav",
      "4": "watch out.wav",
      "5": "hello.wav"
    },
    "version": "1.9.0"
  },
  "zones": {
    "an arena (pvp) area": "false",
    "befallen": "false",
    "blackburrow": "false",
    "butcherblock mountains": "false",
    "castle mistmoore": "false",
    "chardok": "false",
    "city of thurgadin": "false",
    "cobalt scar": "false",
    "crushbone": "false",
    "crystal caverns": "false",
    "dagnor's cauldron": "false",
    "dragon necropolis": "false",
    "dreadlands": "false",
    "east commonlands": "false",
    "east freeport": "false",
    "eastern plains of karana": "false",
    "eastern wastelands": "false",
    "erudin": "false",
    "erudin palace": "false",
    "estate of unrest": "false",
    "everfrost": "false",
    "field of bone": "false",
    "firiona vie": "false",
    "frontier mountains": "false",
    "great divide": "false",
    "greater faydark": "false",
    "guk": "false",
    "high keep": "false",
    "highpass hold": "false",
    "howling stones": "false",
    "iceclad ocean": "false",
    "icewell keep": "raid",
    "infected paw": "false",
    "innothule swamp": "false",
    "kael drakkel": "false",
    "karnor's castle": "false",
    "kedge keep": "false",
    "kithicor woods": "false",
    "kurn's tower": "false",
    "lake of ill omen": "false",
    "lake rathetear": "false",
    "lavastorm mountains": "false",
    "lesser faydark": "false",
    "lost temple of cazic-thule": "false",
    "mines of nurga": "false",
    "misty thicket": "false",
    "nagafen's lair": "false",
    "north freeport": "false",
    "northern desert of ro": "false",
    "northern felwithe": "false",
    "northern plains of karana": "false",
    "oasis of marr": "false",
    "ocean of tears": "false",
    "old sebilis": "false",
    "paineel": "false",
    "permafrost caverns": "false",
    "plane of air": "false",
    "plane of fear": "raid",
    "plane of growth": "false",
    "plane of hate": "raid",
    "plane of mischief": "false",
    "qeynos hills": "false",
    "rathe mountains": "false",
    "rivervale": "false",
    "ruins of old guk": "false",
    "sirens grotto": "false",
    "skyfire mountains": "false",
    "skyshrine": "false",
    "sleepers tomb": "false",
    "south kaladim": "false",
    "southern desert of ro": "false",
    "southern felwithe": "false",
    "southern plains of karana": "false",
    "steamfont mountains": "false",
    "surefall glade": "false",
    "temple of droga": "false",
    "temple of veeshan": "raid",
    "the arena": "false",
    "the burning wood": "false",
    "the city of mist": "false",
    "the emerald jungle": "false",
    "the feerrott": "false",
    "the hole": "false",
    "the nektulos forest": "false",
    "the overthere": "false",
    "the wakening lands": "false",
    "timorous deep": "false",
    "toxxulia forest": "false",
    "trakanon's teeth": "false",
    "veeshan's peak": "raid",
    "velketor's labyrinth": "false",
    "warrens": "false",
    "west commonlands": "false",
    "west freeport": "false",
    "western plains of karana": "false",
    "western wastelands": "false"
  }
}
"""

    try:
        f = open(base_path + "config.json", "w", encoding="utf-8")
        f.write(new_config % (base_path, home, base_path))
        f.close()

    except Exception as e:
        eqa_settings.log(
            "build config: Error on line"
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


if __name__ == "__main__":
    main()
