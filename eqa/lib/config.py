#! /usr/bin/env python

"""
   Program:   EQ Alert
   File Name: eqa/lib/config.py
   Copyright (C) 2022 Michael Geitz
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
import pkg_resources

import eqa.lib.settings as eqa_settings
import eqa.lib.state as eqa_state
import eqa.lib.struct as eqa_struct


def init(base_path):
    """Create any missing config files"""
    try:
        generated = build_config(base_path)

        if generated:
            print("One or more new versioned configuration files have been generated.")
            print("Older files have been archived under config/archive/\n")
            print("Please validate your config/settings.json and relaunch eqalert.")
            exit(1)

    except Exception as e:
        eqa_settings.log(
            "config init: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def read_config(base_path):
    """All the config"""
    try:

        line_alerts = {}

        # Characters
        config_path_char = base_path + "config/characters.json"
        json_data = open(config_path_char, "r", encoding="utf-8")
        config_file_characters = json.load(json_data)
        json_data.close()
        config_characters = eqa_struct.config_file(
            "characters", config_path_char, config_file_characters
        )

        # Settings
        config_path_settings = base_path + "config/settings.json"
        json_data = open(config_path_settings, "r", encoding="utf-8")
        config_file_settings = json.load(json_data)
        json_data.close()
        config_settings = eqa_struct.config_file(
            "settings", config_path_settings, config_file_settings
        )

        # Zones
        config_path_zones = base_path + "config/zones.json"
        json_data = open(config_path_zones, "r", encoding="utf-8")
        config_file_zones = json.load(json_data)
        json_data.close()
        config_zones = eqa_struct.config_file(
            "zones", config_path_zones, config_file_zones
        )

        ## Combat
        config_path_line_combat = base_path + "config/line-alerts/combat.json"
        json_data = open(config_path_line_combat, "r", encoding="utf-8")
        config_file_line_alerts = json.load(json_data)
        json_data.close()
        line_alerts.update(config_file_line_alerts)

        ## Spell General
        config_path_line_spell_general = (
            base_path + "config/line-alerts/spell-general.json"
        )
        json_data = open(config_path_line_spell_general, "r", encoding="utf-8")
        config_file_line_alerts = json.load(json_data)
        json_data.close()
        line_alerts["line"].update(config_file_line_alerts["line"])

        ## Spell Specific
        config_path_line_spell_specific = (
            base_path + "config/line-alerts/spell-specific.json"
        )
        json_data = open(config_path_line_spell_specific, "r", encoding="utf-8")
        config_file_line_alerts = json.load(json_data)
        json_data.close()
        line_alerts["line"].update(config_file_line_alerts["line"])

        ## Pets
        config_path_line_pets = base_path + "config/line-alerts/pets.json"
        json_data = open(config_path_line_pets, "r", encoding="utf-8")
        config_file_line_alerts = json.load(json_data)
        json_data.close()
        line_alerts["line"].update(config_file_line_alerts["line"])

        ## Chat Recieved NPC
        config_path_line_chat_recieved_npc = (
            base_path + "config/line-alerts/chat-recieved-npc.json"
        )
        json_data = open(config_path_line_chat_recieved_npc, "r", encoding="utf-8")
        config_file_line_alerts = json.load(json_data)
        json_data.close()
        line_alerts["line"].update(config_file_line_alerts["line"])

        ## Chat Recieved
        config_path_line_chat_recieved = (
            base_path + "config/line-alerts/chat-recieved.json"
        )
        json_data = open(config_path_line_chat_recieved, "r", encoding="utf-8")
        config_file_line_alerts = json.load(json_data)
        json_data.close()
        line_alerts["line"].update(config_file_line_alerts["line"])

        ## Chat Sent
        config_path_line_chat_sent = base_path + "config/line-alerts/chat-sent.json"
        json_data = open(config_path_line_chat_sent, "r", encoding="utf-8")
        config_file_line_alerts = json.load(json_data)
        json_data.close()
        line_alerts["line"].update(config_file_line_alerts["line"])

        ## Command Output
        config_path_line_command_output = (
            base_path + "config/line-alerts/command-output.json"
        )
        json_data = open(config_path_line_command_output, "r", encoding="utf-8")
        config_file_line_alerts = json.load(json_data)
        json_data.close()
        line_alerts["line"].update(config_file_line_alerts["line"])

        ## System Messages
        config_path_line_system_messages = (
            base_path + "config/line-alerts/system-messages.json"
        )
        json_data = open(config_path_line_system_messages, "r", encoding="utf-8")
        config_file_line_alerts = json.load(json_data)
        json_data.close()
        line_alerts["line"].update(config_file_line_alerts["line"])

        ## Group System Messages
        config_path_line_group_system_messages = (
            base_path + "config/line-alerts/group-system-messages.json"
        )
        json_data = open(config_path_line_group_system_messages, "r", encoding="utf-8")
        config_file_line_alerts = json.load(json_data)
        json_data.close()
        line_alerts["line"].update(config_file_line_alerts["line"])

        ## Loot Trade Messages
        config_path_line_loot_trade = base_path + "config/line-alerts/loot-trade.json"
        json_data = open(config_path_line_loot_trade, "r", encoding="utf-8")
        config_file_line_alerts = json.load(json_data)
        json_data.close()
        line_alerts["line"].update(config_file_line_alerts["line"])

        ## Emotes
        config_path_line_emotes = base_path + "config/line-alerts/emotes.json"
        json_data = open(config_path_line_emotes, "r", encoding="utf-8")
        config_file_line_alerts = json.load(json_data)
        json_data.close()
        line_alerts["line"].update(config_file_line_alerts["line"])

        ## Who
        config_path_line_who = base_path + "config/line-alerts/who.json"
        json_data = open(config_path_line_who, "r", encoding="utf-8")
        config_file_line_alerts = json.load(json_data)
        json_data.close()
        line_alerts["line"].update(config_file_line_alerts["line"])

        ## Other
        config_path_line_other = base_path + "config/line-alerts/other.json"
        json_data = open(config_path_line_other, "r", encoding="utf-8")
        config_file_line_alerts = json.load(json_data)
        json_data.close()
        line_alerts["line"].update(config_file_line_alerts["line"])

        config_line_alerts = eqa_struct.config_file("line-alerts", None, line_alerts)

        configs = eqa_struct.configs(
            config_characters, config_settings, config_zones, config_line_alerts
        )

        return configs

    except Exception as e:
        print(
            "config read: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )
        eqa_settings.log(
            "config read: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def update_logs(configs):
    """Add characters and servers of eqemu_ prefixed files in the log path"""

    try:
        log_files = [
            f
            for f in os.listdir(
                configs.settings.config["settings"]["paths"]["char_log"]
            )
            if os.path.isfile(
                os.path.join(
                    configs.settings.config["settings"]["paths"]["char_log"], f
                )
            )
        ]

        for logs in log_files:
            if "eqlog_" in logs:
                emu, middle, end = logs.split("_")
                server_name = end.split(".")[0]
                char_name = middle
                char_server = char_name + "_" + server_name
                if char_server not in configs.characters.config["char_logs"].keys():
                    add_char_log(char_name, server_name, configs)
                if len(configs.settings.config["last_state"].keys()) == 0:
                    bootstrap_state(configs, char_name, server_name)

    except Exception as e:
        print(
            "set config chars: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )
        eqa_settings.log(
            "set config chars: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def add_char_log(char, server, configs):
    """Adds a new character to the config"""
    try:
        char_server = char + "_" + server
        char_log = "eqlog_" + char.title() + "_" + server + ".txt"

        configs.characters.config["char_logs"].update(
            {
                char_server: {
                    "character": char,
                    "server": server,
                    "file_name": char_log,
                    "disabled": "false",
                    "char_state": {
                        "location": {"x": "0.00", "y": "0.00", "z": "0.00"},
                        "direction": "unavailable",
                        "zone": "unavailable",
                        "encumbered": "false",
                        "bind": "unavailable",
                        "level": "unavailable",
                        "class": "unavailable",
                        "guild": "unavailable",
                    },
                }
            }
        )
        json_data = open(configs.characters.path, "w", encoding="utf-8")
        json.dump(configs.characters.config, json_data, sort_keys=True, indent=2)
        json_data.close()

    except Exception as e:
        print(
            "add char: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )
        eqa_settings.log(
            "add char: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def bootstrap_state(configs, char, server):
    """Generate and save state to config"""

    try:
        data = configs.settings.config
        data["last_state"].update(
            {
                "server": server,
                "character": char,
                "afk": "false",
                "group": "false",
                "leader": "false",
                "raid": "false",
            }
        )
        json_data = open(configs.settings.path, "w", encoding="utf-8")
        json.dump(data, json_data, sort_keys=True, indent=2)
        json_data.close()

    except Exception as e:
        eqa_settings.log(
            "bootstrap state: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def get_config_chars(configs):
    """Return each unique character log"""
    try:
        chars = []
        for char_server in configs.characters.config["char_logs"].keys():
            if (
                configs.characters.config["char_logs"][char_server]["disabled"]
                == "false"
            ):
                chars.append(char_server)

        return chars

    except Exception as e:
        eqa_settings.log(
            "get config chars: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def set_last_state(state, configs):
    """Save state to config"""

    try:
        configs.settings.config["last_state"].update(
            {
                "server": str(state.server),
                "character": str(state.char),
                "afk": str(state.afk),
                "group": str(state.group),
                "leader": str(state.leader),
                "raid": str(state.raid),
            }
        )
        configs.settings.config["settings"]["encounter_parsing"].update(
            {"auto_save": str(state.save_parse), "enabled": str(state.encounter_parse)}
        )
        configs.settings.config["settings"]["raid_mode"].update(
            {
                "auto_set": str(state.auto_raid),
            }
        )
        configs.settings.config["settings"]["timers"].update(
            {
                "auto_mob_timer": str(state.auto_mob_timer),
            }
        )
        configs.settings.config["settings"]["debug_mode"].update(
            {"enabled": str(state.debug)}
        )
        configs.settings.config["settings"]["mute"].update({"enabled": str(state.mute)})
        configs.characters.config["char_logs"][state.char + "_" + state.server].update(
            {
                "char": str(state.char),
                "disabled": "false",
                "file_name": "eqlog_"
                + str(state.char)
                + "_"
                + str(state.server)
                + ".txt",
                "server": str(state.server),
                "char_state": {
                    "direction": str(state.direction),
                    "location": {
                        "x": str(state.loc[1]),
                        "y": str(state.loc[0]),
                        "z": str(state.loc[2]),
                    },
                    "zone": str(state.zone),
                    "encumbered": str(state.encumbered),
                    "bind": str(state.bind),
                    "level": str(state.char_level),
                    "class": str(state.char_class),
                    "guild": str(state.char_guild),
                },
            }
        )
        json_data = open(configs.settings.path, "w", encoding="utf-8")
        json.dump(
            configs.settings.config,
            json_data,
            sort_keys=True,
            ensure_ascii=False,
            indent=2,
        )
        json_data.close()
        json_data = open(configs.characters.path, "w", encoding="utf-8")
        json.dump(
            configs.characters.config,
            json_data,
            sort_keys=True,
            ensure_ascii=False,
            indent=2,
        )
        json_data.close()

    except Exception as e:
        eqa_settings.log(
            "set last state: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def get_last_state(configs, char_name, char_server):
    """Load state from config"""

    try:
        # Populate State
        server = configs.settings.config["last_state"]["server"]
        char = configs.settings.config["last_state"]["character"]
        zone = configs.characters.config["char_logs"][char_name + "_" + char_server][
            "char_state"
        ]["zone"]
        location = [
            float(
                configs.characters.config["char_logs"][char_name + "_" + char_server][
                    "char_state"
                ]["location"]["y"]
            ),
            float(
                configs.characters.config["char_logs"][char_name + "_" + char_server][
                    "char_state"
                ]["location"]["x"]
            ),
            float(
                configs.characters.config["char_logs"][char_name + "_" + char_server][
                    "char_state"
                ]["location"]["z"]
            ),
        ]
        direction = configs.characters.config["char_logs"][
            char_name + "_" + char_server
        ]["char_state"]["direction"]
        encumbered = configs.characters.config["char_logs"][
            char_name + "_" + char_server
        ]["char_state"]["encumbered"]
        bind = configs.characters.config["char_logs"][char_name + "_" + char_server][
            "char_state"
        ]["bind"]
        char_level = configs.characters.config["char_logs"][
            char_name + "_" + char_server
        ]["char_state"]["level"]
        char_class = configs.characters.config["char_logs"][
            char_name + "_" + char_server
        ]["char_state"]["class"]
        char_guild = configs.characters.config["char_logs"][
            char_name + "_" + char_server
        ]["char_state"]["guild"]
        afk = configs.settings.config["last_state"]["afk"]
        group = configs.settings.config["last_state"]["group"]
        leader = configs.settings.config["last_state"]["leader"]
        raid = configs.settings.config["last_state"]["raid"]

        encounter_parse = configs.settings.config["settings"]["encounter_parsing"][
            "enabled"
        ]
        debug = configs.settings.config["settings"]["debug_mode"]["enabled"]
        mute = configs.settings.config["settings"]["mute"]["enabled"]
        save_parse = configs.settings.config["settings"]["encounter_parsing"][
            "auto_save"
        ]
        auto_raid = configs.settings.config["settings"]["raid_mode"]["auto_set"]
        auto_mob_timer = configs.settings.config["settings"]["timers"]["auto_mob_timer"]
        mute = configs.settings.config["settings"]["mute"]["enabled"]

        # Get chars
        chars = get_config_chars(configs)

        # Populate and return a new state
        state = eqa_state.EQA_State(
            char,
            chars,
            zone,
            location,
            direction,
            afk,
            server,
            raid,
            debug,
            mute,
            group,
            leader,
            encumbered,
            bind,
            char_level,
            char_class,
            char_guild,
            encounter_parse,
            save_parse,
            auto_raid,
            auto_mob_timer,
        )

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
        json_data = open(
            base_path + "config/line-alerts/other.json", "r", encoding="utf-8"
        )
        data = json.load(json_data)
        data["line"].update(
            {line_type: {"sound": "false", "reaction": "false", "alert": {}}}
        )
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
        json_data = open(base_path + "config/zones.json", "r", encoding="utf-8")
        data = json.load(json_data)
        json_data.close()
        data["zones"].update({str(zone): {"raid_mode": "false", "timer": "0"}})
        json_data = open(base_path + "config/zones.json", "w", encoding="utf-8")
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

    new_char_config = """
{
  "char_logs": {}
}
"""

    new_settings_config = """
{
  "last_state": {},
  "settings": {
    "debug_mode": {
      "enabled": "false"
    },
    "encounter_parsing": {
      "auto_save": "false",
      "enabled": "true"
    },
    "mute": {
      "enabled": "false"
    },
    "paths": {
      "alert_log": "%slog/",
      "data": "%sdata/",
      "encounter": "%sencounters/",
      "char_log": "%s/.wine/drive_c/Program Files/Sony/EverQuest/Logs/",
      "sound": "%ssound/",
      "tmp_sound": "/tmp/eqa/sound/"
    },
    "raid_mode": {
      "auto_set": "true"
    },
    "timers": {
      "auto_mob_timer": "false"
    }
  },
  "version": "%s"
}
"""

    new_zones_config = """
{
  "zones": {
    "An Arena (PVP) Area": {
      "raid_mode": "false",
      "timer": "0"
    },
    "Befallen": {
      "raid_mode": "false",
      "timer": "1140"
    },
    "Blackburrow": {
      "raid_mode": "false",
      "timer": "1320"
    },
    "Butcherblock Mountains": {
      "raid_mode": "false",
      "timer": "600"
    },
    "Castle Mistmoore": {
      "raid_mode": "false",
      "timer": "1320"
    },
    "Chardok": {
      "raid_mode": "false",
      "timer": "1200"
    },
    "City of Thurgadin": {
      "raid_mode": "false",
      "timer": "420"
    },
    "Cobalt Scar": {
      "raid_mode": "false",
      "timer": "1200"
    },
    "Crushbone": {
      "raid_mode": "false",
      "timer": "540"
    },
    "Crystal Caverns": {
      "raid_mode": "false",
      "timer": "885"
    },
    "Dagnor's Cauldron": {
      "raid_mode": "false",
      "timer": "0"
    },
    "Dalnir": {
      "raid_mode": "false",
      "timer": "720"
    },
    "Dragon Necropolis": {
      "raid_mode": "false",
      "timer": "1620"
    },
    "Dreadlands": {
      "raid_mode": "false",
      "timer": "400"
    },
    "East Commonlands": {
      "raid_mode": "false",
      "timer": "400"
    },
    "East Freeport": {
      "raid_mode": "false",
      "timer": "1440"
    },
    "Eastern Plains of Karana": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Eastern Wastelands": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Erudin": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Erudin Palace": {
      "raid_mode": "false",
      "timer": "1500"
    },
    "Estate of Unrest": {
      "raid_mode": "false",
      "timer": "1320"
    },
    "Everfrost": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Field of Bone": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Firiona Vie": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Frontier Mountains": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Gorge of King Xorbb": {
      "raid_mode": "false",
      "timer": "360"
    },
    "Great Divide": {
      "raid_mode": "false",
      "timer": "640"
    },
    "Greater Faydark": {
      "raid_mode": "false",
      "timer": "425"
    },
    "Guk": {
      "raid_mode": "false",
      "timer": "990"
    },
    "High Keep": {
      "raid_mode": "false",
      "timer": "600"
    },
    "Highpass Hold": {
      "raid_mode": "false",
      "timer": "300"
    },
    "Howling Stones": {
      "raid_mode": "false",
      "timer": "1230"
    },
    "Iceclad Ocean": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Icewell Keep": {
      "raid_mode": "true",
      "timer": "1260"
    },
    "Infected Paw": {
      "raid_mode": "false",
      "timer": "1320"
    },
    "Innothule Swamp": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Kael Drakkel": {
      "raid_mode": "true",
      "timer": "1680"
    },
    "Kaesora": {
      "raid_mode": "false",
      "timer": "1080"
    },
    "Karnor's Castle": {
      "raid_mode": "false",
      "timer": "1620"
    },
    "Kedge Keep": {
      "raid_mode": "false",
      "timer": "1320"
    },
    "Kithicor Woods": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Kurn's Tower": {
      "raid_mode": "false",
      "timer": "1100"
    },
    "Lake Rathetear": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Lake of Ill Omen": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Lavastorm Mountains": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Lesser Faydark": {
      "raid_mode": "false",
      "timer": "390"
    },
    "Lost Temple of Cazic-Thule": {
      "raid_mode": "false",
      "timer": "1320"
    },
    "Mines of Nurga": {
      "raid_mode": "false",
      "timer": "1230"
    },
    "Misty Thicket": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Nagafen's Lair": {
      "raid_mode": "false",
      "timer": "1320"
    },
    "Najena": {
      "raid_mode": "false",
      "timer": "1110"
    },
    "North Freeport": {
      "raid_mode": "false",
      "timer": "1440"
    },
    "Northern Desert of Ro": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Northern Felwithe": {
      "raid_mode": "false",
      "timer": "1440"
    },
    "Northern Plains of Karana": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Oasis of Marr": {
      "raid_mode": "false",
      "timer": "990"
    },
    "Ocean of Tears": {
      "raid_mode": "false",
      "timer": "360"
    },
    "Old Sebilis": {
      "raid_mode": "false",
      "timer": "1620"
    },
    "Paineel": {
      "raid_mode": "false",
      "timer": "630"
    },
    "Permafrost Caverns": {
      "raid_mode": "false",
      "timer": "1320"
    },
    "Plane of Air": {
      "raid_mode": "true",
      "timer": "28800"
    },
    "Plane of Fear": {
      "raid_mode": "true",
      "timer": "28800"
    },
    "Plane of Growth": {
      "raid_mode": "true",
      "timer": "43200"
    },
    "Plane of Hate": {
      "raid_mode": "true",
      "timer": "28800"
    },
    "Plane of Mischief": {
      "raid_mode": "false",
      "timer": "4210"
    },
    "Qeynos Hills": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Rathe Mountains": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Rivervale": {
      "raid_mode": "false",
      "timer": "1320"
    },
    "Ruins of Old Guk": {
      "raid_mode": "false",
      "timer": "1680"
    },
    "Sirens Grotto": {
      "raid_mode": "false",
      "timer": "1680"
    },
    "Skyfire Mountains": {
      "raid_mode": "false",
      "timer": "780"
    },
    "Skyshrine": {
      "raid_mode": "true",
      "timer": "1800"
    },
    "Sleepers Tomb": {
      "raid_mode": "true",
      "timer": "28800"
    },
    "South Kaladim": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Southern Desert of Ro": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Southern Felwithe": {
      "raid_mode": "false",
      "timer": "1440"
    },
    "Southern Plains of Karana": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Steamfont Mountains": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Surefall Glade": {
      "raid_mode": "false",
      "timer": "0"
    },
    "Temple of Droga": {
      "raid_mode": "false",
      "timer": "1230"
    },
    "Temple of Solusek Ro": {
      "raid_mode": "false",
      "timer": "0"
    },
    "Temple of Veeshan": {
      "raid_mode": "true",
      "timer": "4398"
    },
    "The Arena": {
      "raid_mode": "false",
      "timer": "0"
    },
    "The Burning Wood": {
      "raid_mode": "false",
      "timer": "400"
    },
    "The City of Mist": {
      "raid_mode": "false",
      "timer": "1320"
    },
    "The Emerald Jungle": {
      "raid_mode": "false",
      "timer": "0"
    },
    "The Feerrott": {
      "raid_mode": "false",
      "timer": "400"
    },
    "The Hole": {
      "raid_mode": "false",
      "timer": "1290"
    },
    "The Nektulos Forest": {
      "raid_mode": "false",
      "timer": "400"
    },
    "The Overthere": {
      "raid_mode": "false",
      "timer": "400"
    },
    "The Wakening Lands": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Tower of Frozen Shadow": {
      "raid_mode": "false",
      "timer": "1200"
    },
    "Timorous Deep": {
      "raid_mode": "false",
      "timer": "720"
    },
    "Toxxulia Forest": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Trakanon's Teeth": {
      "raid_mode": "false",
      "timer": "400"
    },
    "Veeshan's Peak": {
      "raid_mode": "true",
      "timer": "0"
    },
    "Velketor's Labyrinth": {
      "raid_mode": "false",
      "timer": "1972"
    },
    "Warrens": {
      "raid_mode": "false",
      "timer": "400"
    },
    "West Commonlands": {
      "raid_mode": "false",
      "timer": "400"
    },
    "West Freeport": {
      "raid_mode": "false",
      "timer": "1440"
    },
    "Western Plains of Karana": {
      "raid_mode": "false",
      "timer": "1320"
    },
    "Western Wastes": {
      "raid_mode": "true",
      "timer": "0"
    }
  },
  "version": "%s"
}
"""

    new_line_combat_config = """
{
  "line": {
    "combat_other_melee": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_other_melee_block": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_other_melee_crip_blow": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_other_melee_crit": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_other_melee_crit_kick": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_other_melee_dodge": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_other_melee_invulnerable": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_other_melee_miss": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_other_melee_parry": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_other_melee_reposte": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_other_rune_damage": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_you_melee": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_you_melee_miss": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_you_receive_melee": {
      "alert": {},
      "reaction": "afk",
      "sound": "danger will robinson"
    },
    "experience_group": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "experience_lost": {
      "alert": {},
      "reaction": "all",
      "sound": "oh no!"
    },
    "experience_solo": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "experience_solo_resurrection": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "mob_enrage_off": {
      "alert": {},
      "reaction": "group",
      "sound": "true"
    },
    "mob_enrage_on": {
      "alert": {},
      "reaction": "group",
      "sound": "enrage"
    },
    "mob_out_of_range": {
      "alert": {},
      "reaction": "group",
      "sound": "range"
    },
    "mob_rampage_on": {
      "alert": {},
      "reaction": "group",
      "sound": "rampage"
    },
    "mob_slain_other": {
      "alert": {},
      "reaction": "solo_group_only",
      "sound": "true"
    },
    "mob_slain_you": {
      "alert": {},
      "reaction": "solo_group_only",
      "sound": "true"
    }
  },
  "version": "%s"
}
"""

    new_line_spell_general_config = """
{
  "line": {
    "spell_cast_item_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_cast_oom": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_cast_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_cast_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_cooldown_active": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_damage": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_fizzle_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_fizzle_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_forget": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_interrupt_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_interrupt_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_memorize_already": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_memorize_begin": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_memorize_finish": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_no_target": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_not_hold": {
      "alert": {},
      "reaction": "raid",
      "sound": "did not hold"
    },
    "spell_protected": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_recover_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_recover_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_resist_you": {
      "alert": {},
      "reaction": "solo",
      "sound": "resist"
    },
    "spell_sitting": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_worn_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "true"
    }
  },
  "version": "%s"
}
"""

    new_line_spell_specific_config = """
{
  "line": {
    "spell_bind_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_cured_other": {
      "alert": {},
      "reaction": "all",
      "sound": "cured"
    },
    "spell_gate_collapse": {
      "alert": {},
      "reaction": "all",
      "sound": "gate collapse"
    },
    "spell_heal_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_invis_dropping_you": {
      "alert": {},
      "reaction": "solo",
      "sound": "invis is dropping"
    },
    "spell_invis_off_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_invis_on_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_levitate_dropping_you": {
      "alert": {},
      "reaction": "solo",
      "sound": "levitate is dropping"
    },
    "spell_levitate_off_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_levitate_on_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_regen_on_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_regen_on_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_slow_on": {
      "alert": {},
      "reaction": "solo_group_only",
      "sound": "slowed"
    },
    "spell_sow_off_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_sow_on_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_summoned_you": {
      "alert": {},
      "reaction": "group",
      "sound": "you have been summoned"
    }
  },
  "version": "%s"
}
"""

    new_line_pets_config = """
{
  "line": {
    "pet_attack": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "pet_back": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "pet_dead": {
      "alert": {},
      "reaction": "solo",
      "sound": "pet dead"
    },
    "pet_follow": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "pet_guard": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "pet_illegal_target": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "pet_sit_stand": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "pet_spawn": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "pet_taunt_off": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    }
  },
  "version": "%s"
}
"""

    new_line_chat_recieved_npc_config = """
{
  "line": {
    "say_npc": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "shout_npc": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "tell_npc": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    }
  },
  "version": "%s"
}
"""

    new_line_chat_recieved_config = """
{
  "line": {
    "auction": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "auction_wtb": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "auction_wts": {
      "alert": {
        "shiny brass idol": "true"
      },
      "reaction": "alert",
      "sound": "look at auction"
    },
    "group": {
      "alert": {
        "drop": "raid",
        "help": "raid",
        "inc": "true",
        "invis": "raid",
        "invite": "raid",
        "oom": "true"
      },
      "reaction": "alert",
      "sound": "look at group"
    },
    "guild": {
      "alert": {
        "assist": "raid",
        "crippled": "raid",
        "dispelled": "raid",
        "feared": "raid",
        "fixated": "raid",
        "fixation": "raid",
        "harmony": "raid",
        "help": "true",
        "incoming": "raid",
        "logs": "raid",
        "malo": "raid",
        "malosini": "raid",
        "occlusion": "raid",
        "off-tanking": "raid",
        "pop": "raid",
        "rampage": "raid",
        "rune": "raid",
        "sieve": "raid",
        "slow": "raid",
        "snare": "raid",
        "stand": "raid",
        "sunder": "raid",
        "tash": "raid"
      },
      "reaction": "alert",
      "sound": "look at guild"
    },
    "ooc": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "say": {
      "alert": {
        "help": "true",
        "spot": "raid"
      },
      "reaction": "alert",
      "sound": "look at say"
    },
    "shout": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "tell": {
      "alert": {},
      "reaction": "solo",
      "sound": "true"
    }
  },
  "version": "%s"
}
"""

    new_line_chat_sent_config = """
{
  "line": {
    "auction_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "group_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "guild_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "ooc_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "say_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "shout_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "tell_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    }
  },
  "version": "%s"
}
"""

    new_line_command_output_config = """
{
  "line": {
    "command_block": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "command_block_casting": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "command_invalid": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "direction": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "direction_miss": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "drink_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "location": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "motd_game": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "motd_guild": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "player_linkdead": {
      "alert": {},
      "reaction": "group",
      "sound": "true"
    },
    "random": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "server_message": {
      "alert": {},
      "reaction": "all",
      "sound": "true"
    },
    "skill_up": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "song_interrupted_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "summon_corpse": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "target": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "time_earth": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "time_game": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_afk_off": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_afk_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_camping": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_camping_abandoned": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_lfg_off": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_lfg_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    }
  },
  "version": "%s"
}
"""

    new_line_system_messages_config = """
{
  "line": {
    "autofollow_advice": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "command_error": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "consider_no_target": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "ding_down": {
      "alert": {},
      "reaction": "all",
      "sound": "true"
    },
    "ding_up": {
      "alert": {},
      "reaction": "all",
      "sound": "congratulations"
    },
    "earthquake": {
      "alert": {},
      "reaction": "solo",
      "sound": "earthquake!"
    },
    "encumbered_off": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "encumbered_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "engage": {
      "alert": {},
      "reaction": "all",
      "sound": "true"
    },
    "faction_line": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "motd_welcome": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "tell_offline": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "tracking": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "tracking_player_off": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "tracking_player_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "weather_start_rain": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "weather_start_snow": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "wrong_key": {
      "alert": {},
      "reaction": "all",
      "sound": "wrong key or place"
    },
    "you_auto_attack_off": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_auto_attack_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_cannot_reach": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_char_bound": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_hungry": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_new_zone": {
      "alert": {},
      "reaction": "all",
      "sound": "true"
    },
    "you_outdrink": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_outdrinklowfood": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_outfood": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_outfooddrink": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_outfoodlowdrink": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_stun_off": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_stun_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_thirsty": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "zone_message": {
      "alert": {},
      "reaction": "all",
      "sound": "true"
    },
    "zoning": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    }
  },
  "version": "%s"
}
"""

    new_line_group_system_messages_config = """
{
  "line": {
    "group_created": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "group_disbanded": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "group_invite_instruction": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "group_invite_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "group_invite_you": {
      "alert": {},
      "reaction": "solo",
      "sound": "true"
    },
    "group_join_notify": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "group_joined": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "group_joined_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "group_leader_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "group_leader_you": {
      "alert": {},
      "reaction": "group",
      "sound": "true"
    },
    "group_leave_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "group_removed": {
      "alert": {},
      "reaction": "solo",
      "sound": "true"
    }
  },
  "version": "%s"
}
"""

    new_line_loot_trade_config = """
{
  "line": {
    "looted_item_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "looted_item_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "looted_money_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "looted_money_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "trade_item": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "trade_money": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "trade_npc_payment": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    }
  },
  "version": "%s"
}
"""

    new_line_emotes_config = """
{
  "line": {
    "emote_agree_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_amaze_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_apologize_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_bird_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_bite_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_bleed_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_blink_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_blush_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_boggle_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_bonk_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_bonk_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_bored_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_bounce_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_bow_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_bow_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_brb_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_burp_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_bye_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_cackle_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_calm_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_cheer_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_cheer_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_chuckle_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_clap_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_comfort_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_congratulate_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_cough_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_cringe_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_cry_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_curious_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_dance_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_dance_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_drool_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_duck_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_eye_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_fidget_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_flex_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_frown_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_gasp_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_giggle_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_glare_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_grin_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_groan_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_grovel_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_happy_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_hug_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_hungry_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_introduce_you": {
      "alert": {},
      "reaction": "all",
      "sound": "why, hello there"
    },
    "emote_jk_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_kiss_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_kneel_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_laugh_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_lost_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_massage_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_moan_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_mourn_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_nod_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_nudge_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_panic_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_pat_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_peer_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_plead_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_point_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_poke_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_ponder_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_purr_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_puzzle_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_raise_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_ready_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_roar_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_rofl_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_salute_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_shiver_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_shrug_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_sigh_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_smack_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_smile_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_smile_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_smirk_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_snarl_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_snicker_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_stare_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_tap_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_tease_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_thank_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_thank_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_thirsty_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_veto_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_wave_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_wave_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_whine_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_whistle_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_yawn_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    }
  },
  "version": "%s"
}
"""

    new_line_who_config = """
{
  "line": {
    "who_line": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "who_line_friends": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "who_player": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "who_top": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "who_top_friends": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "who_top_lfg": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "who_total": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "who_total_empty": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "who_total_local_empty": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    }
  },
  "version": "%s"
}
"""

    new_line_other_config = """
{
  "line": {
    "all": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "undetermined": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    }
  },
  "version": "%s"
}
"""

    try:
        home = os.path.expanduser("~")
        version = str(pkg_resources.get_distribution("eqalert").version)
        generated = False

        # Check for old config.yml
        legacy_config_json_path = base_path + "config.json"
        if os.path.isfile(legacy_config_json_path):
            json_data = open(legacy_config_json_path, "r", encoding="utf-8")
            legacy_config_json = json.load(json_data)
            json_data.close()
            old_version = str(legacy_config_json["settings"]["version"]).replace(
                ".", "-"
            )
            if not os.path.exists(base_path + "config/archive/"):
                os.makedirs(base_path + "config/archive/")
            if not os.path.exists(base_path + "config/archive/" + old_version + "/"):
                os.makedirs(base_path + "config/archive/" + old_version + "/")
            archive_config = (
                base_path + "config/archive/" + old_version + "/config.json"
            )
            os.rename(legacy_config_json_path, archive_config)

        # Generate Default Files if Needed
        ## Characters File
        characters_json_path = base_path + "config/characters.json"
        if not os.path.isfile(characters_json_path):
            f = open(characters_json_path, "w", encoding="utf-8")
            f.write(new_char_config)
            f.close()
            generated = True

        ## Settings
        settings_json_path = base_path + "config/settings.json"
        if not os.path.isfile(settings_json_path):
            f = open(settings_json_path, "w", encoding="utf-8")
            f.write(
                new_settings_config
                % (base_path, base_path, base_path, home, base_path, version)
            )
            f.close()
            generated = True
        elif os.path.isfile(settings_json_path):
            json_data = open(settings_json_path, "r", encoding="utf-8")
            settings_json = json.load(json_data)
            json_data.close()
            # Archive old settings.json and re-generate one
            if not settings_json["version"] == version:
                old_version = str(settings_json["version"]).replace(".", "-")
                if not os.path.exists(base_path + "config/archive/"):
                    os.makedirs(base_path + "config/archive/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/"
                ):
                    os.makedirs(base_path + "config/archive/" + old_version + "/")
                archive_config = (
                    base_path + "config/archive/" + old_version + "/settings.json"
                )
                os.rename(settings_json_path, archive_config)
                f = open(settings_json_path, "w", encoding="utf-8")
                f.write(
                    new_settings_config
                    % (base_path, base_path, base_path, home, base_path, version)
                )
                f.close()
                generated = True

        ## Zones
        zones_json_path = base_path + "config/zones.json"
        if not os.path.isfile(zones_json_path):
            f = open(zones_json_path, "w", encoding="utf-8")
            f.write(new_zones_config % (version))
            f.close()
            generated = True
        elif os.path.isfile(zones_json_path):
            json_data = open(zones_json_path, "r", encoding="utf-8")
            zones_json = json.load(json_data)
            json_data.close()
            # Archive old zones.json and re-generate one
            if not zones_json["version"] == version:
                old_version = str(zones_json["version"]).replace(".", "-")
                if not os.path.exists(base_path + "config/archive/"):
                    os.makedirs(base_path + "config/archive/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/"
                ):
                    os.makedirs(base_path + "config/archive/" + old_version + "/")
                archive_config = (
                    base_path + "config/archive/" + old_version + "/zones.json"
                )
                os.rename(zones_json_path, archive_config)
                f = open(zones_json_path, "w", encoding="utf-8")
                f.write(new_zones_config % (version))
                f.close()
                generated = True

        ## Line Alerts
        ### Combat
        line_combat_json_path = base_path + "config/line-alerts/combat.json"
        if not os.path.isfile(line_combat_json_path):
            f = open(line_combat_json_path, "w", encoding="utf-8")
            f.write(new_line_combat_config % (version))
            f.close()
            generated = True
        elif os.path.isfile(line_combat_json_path):
            json_data = open(line_combat_json_path, "r", encoding="utf-8")
            line_combat_json = json.load(json_data)
            json_data.close()
            # Archive old line-alerts/combat.json and re-generate one
            if not line_combat_json["version"] == version:
                old_version = str(line_combat_json["version"]).replace(".", "-")
                if not os.path.exists(base_path + "config/archive/"):
                    os.makedirs(base_path + "config/archive/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/"
                ):
                    os.makedirs(base_path + "config/archive/" + old_version + "/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/line-alerts/"
                ):
                    os.makedirs(
                        base_path + "config/archive/" + old_version + "/line-alerts/"
                    )
                archive_config = (
                    base_path
                    + "config/archive/"
                    + old_version
                    + "/line-alerts/combat.json"
                )
                os.rename(line_combat_json_path, archive_config)
                f = open(line_combat_json_path, "w", encoding="utf-8")
                f.write(new_line_combat_config % (version))
                f.close()
                generated = True

        ### Spell General
        line_spell_general_json_path = (
            base_path + "config/line-alerts/spell-general.json"
        )
        if not os.path.isfile(line_spell_general_json_path):
            f = open(
                line_spell_general_json_path,
                "w",
                encoding="utf-8",
            )
            f.write(new_line_spell_general_config % (version))
            f.close()
            generated = True
        elif os.path.isfile(line_spell_general_json_path):
            json_data = open(line_spell_general_json_path, "r", encoding="utf-8")
            line_spell_general_json = json.load(json_data)
            json_data.close()
            # Archive old line-alerts/spell-general.json and re-generate one
            if not line_spell_general_json["version"] == version:
                old_version = str(line_spell_general_json["version"]).replace(".", "-")
                if not os.path.exists(base_path + "config/archive/"):
                    os.makedirs(base_path + "config/archive/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/"
                ):
                    os.makedirs(base_path + "config/archive/" + old_version + "/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/line-alerts/"
                ):
                    os.makedirs(
                        base_path + "config/archive/" + old_version + "/line-alerts/"
                    )
                archive_config = (
                    base_path
                    + "config/archive/"
                    + old_version
                    + "/line-alerts/spell-general.json"
                )
                os.rename(line_spell_general_json_path, archive_config)
                f = open(
                    line_spell_general_json_path,
                    "w",
                    encoding="utf-8",
                )
                f.write(new_line_spell_general_config % (version))
                f.close()
                generated = True

        ### Spell Specific
        line_spell_specific_json_path = (
            base_path + "config/line-alerts/spell-specific.json"
        )
        if not os.path.isfile(line_spell_specific_json_path):
            f = open(
                line_spell_specific_json_path,
                "w",
                encoding="utf-8",
            )
            f.write(new_line_spell_specific_config % (version))
            f.close()
            generated = True
        elif os.path.isfile(line_spell_specific_json_path):
            json_data = open(line_spell_specific_json_path, "r", encoding="utf-8")
            line_spell_specific_json = json.load(json_data)
            json_data.close()
            # Archive old line-alerts/spell-specific.json and re-generate one
            if not line_spell_specific_json["version"] == version:
                old_version = str(line_spell_specific_json["version"]).replace(".", "-")
                if not os.path.exists(base_path + "config/archive/"):
                    os.makedirs(base_path + "config/archive/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/"
                ):
                    os.makedirs(base_path + "config/archive/" + old_version + "/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/line-alerts/"
                ):
                    os.makedirs(
                        base_path + "config/archive/" + old_version + "/line-alerts/"
                    )
                archive_config = (
                    base_path
                    + "config/archive/"
                    + old_version
                    + "/line-alerts/spell-specific.json"
                )
                os.rename(line_spell_specific_json_path, archive_config)
                f = open(
                    line_spell_specific_json_path,
                    "w",
                    encoding="utf-8",
                )
                f.write(new_line_spell_specific_config % (version))
                f.close()
                generated = True

        ### Pets
        line_pets_json_path = base_path + "config/line-alerts/pets.json"
        if not os.path.isfile(line_pets_json_path):
            f = open(line_pets_json_path, "w", encoding="utf-8")
            f.write(new_line_pets_config % (version))
            f.close()
            generated = True
        elif os.path.isfile(line_pets_json_path):
            json_data = open(line_pets_json_path, "r", encoding="utf-8")
            line_pets_json = json.load(json_data)
            json_data.close()
            # Archive old line-alerts/pets.json and re-generate one
            if not line_pets_json["version"] == version:
                old_version = str(line_pets_json["version"]).replace(".", "-")
                if not os.path.exists(base_path + "config/archive/"):
                    os.makedirs(base_path + "config/archive/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/"
                ):
                    os.makedirs(base_path + "config/archive/" + old_version + "/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/line-alerts/"
                ):
                    os.makedirs(
                        base_path + "config/archive/" + old_version + "/line-alerts/"
                    )
                archive_config = (
                    base_path
                    + "config/archive/"
                    + old_version
                    + "/line-alerts/pets.json"
                )
                os.rename(line_pets_json_path, archive_config)
                f = open(line_pets_json_path, "w", encoding="utf-8")
                f.write(new_line_pets_config % (version))
                f.close()
                generated = True

        ### Chat Recieved NPC
        line_chat_recieved_npc_json_path = (
            base_path + "config/line-alerts/chat-recieved-npc.json"
        )
        if not os.path.isfile(line_chat_recieved_npc_json_path):
            f = open(
                line_chat_recieved_npc_json_path,
                "w",
                encoding="utf-8",
            )
            f.write(new_line_chat_recieved_npc_config % (version))
            f.close()
            generated = True
        elif os.path.isfile(line_chat_recieved_npc_json_path):
            json_data = open(line_chat_recieved_npc_json_path, "r", encoding="utf-8")
            line_chat_recieved_npc_json = json.load(json_data)
            json_data.close()
            # Archive old line-alerts/chat-recieved-npc.json and re-generate one
            if not line_chat_recieved_npc_json["version"] == version:
                old_version = str(line_chat_recieved_npc_json["version"]).replace(
                    ".", "-"
                )
                if not os.path.exists(base_path + "config/archive/"):
                    os.makedirs(base_path + "config/archive/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/"
                ):
                    os.makedirs(base_path + "config/archive/" + old_version + "/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/line-alerts/"
                ):
                    os.makedirs(
                        base_path + "config/archive/" + old_version + "/line-alerts/"
                    )
                archive_config = (
                    base_path
                    + "config/archive/"
                    + old_version
                    + "/line-alerts/chat-recieved-npc.json"
                )
                os.rename(line_chat_recieved_npc_json_path, archive_config)
                f = open(
                    line_chat_recieved_npc_json_path,
                    "w",
                    encoding="utf-8",
                )
                f.write(new_line_chat_recieved_npc_config % (version))
                f.close()
                generated = True

        ### Chat Recieved
        line_chat_recieved_json_path = (
            base_path + "config/line-alerts/chat-recieved.json"
        )
        if not os.path.isfile(line_chat_recieved_json_path):
            f = open(
                line_chat_recieved_json_path,
                "w",
                encoding="utf-8",
            )
            f.write(new_line_chat_recieved_config % (version))
            f.close()
            generated = True
        elif os.path.isfile(line_chat_recieved_json_path):
            json_data = open(line_chat_recieved_json_path, "r", encoding="utf-8")
            line_chat_recieved_json = json.load(json_data)
            json_data.close()
            # Archive old line-alerts/chat-recieved.json and re-generate one
            if not line_chat_recieved_json["version"] == version:
                old_version = str(line_chat_recieved_json["version"]).replace(".", "-")
                if not os.path.exists(base_path + "config/archive/"):
                    os.makedirs(base_path + "config/archive/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/"
                ):
                    os.makedirs(base_path + "config/archive/" + old_version + "/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/line-alerts/"
                ):
                    os.makedirs(
                        base_path + "config/archive/" + old_version + "/line-alerts/"
                    )
                archive_config = (
                    base_path
                    + "config/archive/"
                    + old_version
                    + "/line-alerts/chat-recieved.json"
                )
                os.rename(line_chat_recieved_json_path, archive_config)
                f = open(
                    line_chat_recieved_json_path,
                    "w",
                    encoding="utf-8",
                )
                f.write(new_line_chat_recieved_config % (version))
                f.close()
                generated = True

        ### Chat Sent
        line_chat_sent_json_path = base_path + "config/line-alerts/chat-sent.json"
        if not os.path.isfile(line_chat_sent_json_path):
            f = open(line_chat_sent_json_path, "w", encoding="utf-8")
            f.write(new_line_chat_sent_config % (version))
            f.close()
            generated = True
        elif os.path.isfile(line_chat_sent_json_path):
            json_data = open(line_chat_sent_json_path, "r", encoding="utf-8")
            line_chat_sent_json = json.load(json_data)
            json_data.close()
            # Archive old line-alerts/chat-sent.json and re-generate one
            if not line_chat_sent_json["version"] == version:
                old_version = str(line_chat_sent_json["version"]).replace(".", "-")
                if not os.path.exists(base_path + "config/archive/"):
                    os.makedirs(base_path + "config/archive/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/"
                ):
                    os.makedirs(base_path + "config/archive/" + old_version + "/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/line-alerts/"
                ):
                    os.makedirs(
                        base_path + "config/archive/" + old_version + "/line-alerts/"
                    )
                archive_config = (
                    base_path
                    + "config/archive/"
                    + old_version
                    + "/line-alerts/chat-sent.json"
                )
                os.rename(line_chat_sent_json_path, archive_config)
                f = open(
                    line_chat_sent_json_path,
                    "w",
                    encoding="utf-8",
                )
                f.write(new_line_chat_sent_config % (version))
                f.close()
                generated = True

        ### Command Output
        line_command_output_json_path = (
            base_path + "config/line-alerts/command-output.json"
        )
        if not os.path.isfile(line_command_output_json_path):
            f = open(
                line_command_output_json_path,
                "w",
                encoding="utf-8",
            )
            f.write(new_line_command_output_config % (version))
            f.close()
            generated = True
        elif os.path.isfile(line_command_output_json_path):
            json_data = open(line_command_output_json_path, "r", encoding="utf-8")
            line_command_output_json = json.load(json_data)
            json_data.close()
            # Archive old line-alerts/command-output.json and re-generate one
            if not line_command_output_json["version"] == version:
                old_version = str(line_chat_sent_json["version"]).replace(".", "-")
                if not os.path.exists(base_path + "config/archive/"):
                    os.makedirs(base_path + "config/archive/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/"
                ):
                    os.makedirs(base_path + "config/archive/" + old_version + "/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/line-alerts/"
                ):
                    os.makedirs(
                        base_path + "config/archive/" + old_version + "/line-alerts/"
                    )
                archive_config = (
                    base_path
                    + "config/archive/"
                    + old_version
                    + "/line-alerts/command-output.json"
                )
                os.rename(line_command_output_json_path, archive_config)
                f = open(
                    line_command_output_json_path,
                    "w",
                    encoding="utf-8",
                )
                f.write(new_line_command_output_config % (version))
                f.close()
                generated = True

        ### System Messages
        line_system_messages_json_path = (
            base_path + "config/line-alerts/system-messages.json"
        )
        if not os.path.isfile(line_system_messages_json_path):
            f = open(
                line_system_messages_json_path,
                "w",
                encoding="utf-8",
            )
            f.write(new_line_system_messages_config % (version))
            f.close()
            generated = True
        elif os.path.isfile(line_system_messages_json_path):
            json_data = open(line_system_messages_json_path, "r", encoding="utf-8")
            line_system_messages_json = json.load(json_data)
            json_data.close()
            # Archive old line-alerts/system-messages.json and re-generate one
            if not line_system_messages_json["version"] == version:
                old_version = str(line_system_messages_json["version"]).replace(
                    ".", "-"
                )
                if not os.path.exists(base_path + "config/archive/"):
                    os.makedirs(base_path + "config/archive/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/"
                ):
                    os.makedirs(base_path + "config/archive/" + old_version + "/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/line-alerts/"
                ):
                    os.makedirs(
                        base_path + "config/archive/" + old_version + "/line-alerts/"
                    )
                archive_config = (
                    base_path
                    + "config/archive/"
                    + old_version
                    + "/line-alerts/system-messages.json"
                )
                os.rename(line_system_messages_json_path, archive_config)
                f = open(
                    line_system_messages_json_path,
                    "w",
                    encoding="utf-8",
                )
                f.write(new_line_system_messages_config % (version))
                f.close()
                generated = True

        ### Group System Messages
        line_group_system_messages_json_path = (
            base_path + "config/line-alerts/group-system-messages.json"
        )
        if not os.path.isfile(line_group_system_messages_json_path):
            f = open(
                line_group_system_messages_json_path,
                "w",
                encoding="utf-8",
            )
            f.write(new_line_group_system_messages_config % (version))
            f.close()
            generated = True
        elif os.path.isfile(line_group_system_messages_json_path):
            json_data = open(
                line_group_system_messages_json_path, "r", encoding="utf-8"
            )
            line_group_system_messages_json = json.load(json_data)
            json_data.close()
            # Archive old line-alerts/group-system-messages.json and re-generate one
            if not line_group_system_messages_json["version"] == version:
                old_version = str(line_group_system_messages_json["version"]).replace(
                    ".", "-"
                )
                if not os.path.exists(base_path + "config/archive/"):
                    os.makedirs(base_path + "config/archive/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/"
                ):
                    os.makedirs(base_path + "config/archive/" + old_version + "/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/line-alerts/"
                ):
                    os.makedirs(
                        base_path + "config/archive/" + old_version + "/line-alerts/"
                    )
                archive_config = (
                    base_path
                    + "config/archive/"
                    + old_version
                    + "/line-alerts/group-system-messages.json"
                )
                os.rename(line_group_system_messages_json_path, archive_config)
                f = open(
                    line_group_system_messages_json_path,
                    "w",
                    encoding="utf-8",
                )
                f.write(new_line_group_system_messages_config % (version))
                f.close()
                generated = True

        ### Loot Trade Messages
        line_loot_trade_json_path = base_path + "config/line-alerts/loot-trade.json"
        if not os.path.isfile(line_loot_trade_json_path):
            f = open(line_loot_trade_json_path, "w", encoding="utf-8")
            f.write(new_line_loot_trade_config % (version))
            f.close()
            generated = True
        elif os.path.isfile(line_loot_trade_json_path):
            json_data = open(line_loot_trade_json_path, "r", encoding="utf-8")
            line_loot_trade_json = json.load(json_data)
            json_data.close()
            # Archive old line-alerts/loot-trade.json and re-generate one
            if not line_loot_trade_json["version"] == version:
                old_version = str(line_loot_trade_json["version"]).replace(".", "-")
                if not os.path.exists(base_path + "config/archive/"):
                    os.makedirs(base_path + "config/archive/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/"
                ):
                    os.makedirs(base_path + "config/archive/" + old_version + "/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/line-alerts/"
                ):
                    os.makedirs(
                        base_path + "config/archive/" + old_version + "/line-alerts/"
                    )
                archive_config = (
                    base_path
                    + "config/archive/"
                    + old_version
                    + "/line-alerts/loot-trade.json"
                )
                os.rename(line_loot_trade_json_path, archive_config)
                f = open(
                    line_loot_trade_json_path,
                    "w",
                    encoding="utf-8",
                )
                f.write(new_line_loot_trade_messages_config % (version))
                f.close()
                generated = True

        ### Emotes
        line_emotes_json_path = base_path + "config/line-alerts/emotes.json"
        if not os.path.isfile(line_emotes_json_path):
            f = open(line_emotes_json_path, "w", encoding="utf-8")
            f.write(new_line_emotes_config % (version))
            f.close()
            generated = True
        elif os.path.isfile(line_emotes_json_path):
            json_data = open(line_emotes_json_path, "r", encoding="utf-8")
            line_emotes_json = json.load(json_data)
            json_data.close()
            # Archive old line-alerts/emotes.json and re-generate one
            if not line_emotes_json["version"] == version:
                old_version = str(line_emotes_json["version"]).replace(".", "-")
                if not os.path.exists(base_path + "config/archive/"):
                    os.makedirs(base_path + "config/archive/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/"
                ):
                    os.makedirs(base_path + "config/archive/" + old_version + "/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/line-alerts/"
                ):
                    os.makedirs(
                        base_path + "config/archive/" + old_version + "/line-alerts/"
                    )
                archive_config = (
                    base_path
                    + "config/archive/"
                    + old_version
                    + "/line-alerts/emotes.json"
                )
                os.rename(line_emotes_json_path, archive_config)
                f = open(line_emotes_json_path, "w", encoding="utf-8")
                f.write(new_line_emotes_config % (version))
                f.close()
                generated = True

        ### Who
        line_who_json_path = base_path + "config/line-alerts/who.json"
        if not os.path.isfile(line_who_json_path):
            f = open(line_who_json_path, "w", encoding="utf-8")
            f.write(new_line_who_config % (version))
            f.close()
            generated = True
        elif os.path.isfile(line_who_json_path):
            json_data = open(line_who_json_path, "r", encoding="utf-8")
            line_who_json = json.load(json_data)
            json_data.close()
            # Archive old line-alerts/who.json and re-generate one
            if not line_who_json["version"] == version:
                old_version = str(line_who_json["version"]).replace(".", "-")
                if not os.path.exists(base_path + "config/archive/"):
                    os.makedirs(base_path + "config/archive/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/"
                ):
                    os.makedirs(base_path + "config/archive/" + old_version + "/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/line-alerts/"
                ):
                    os.makedirs(
                        base_path + "config/archive/" + old_version + "/line-alerts/"
                    )
                archive_config = (
                    base_path
                    + "config/archive/"
                    + old_version
                    + "/line-alerts/who.json"
                )
                os.rename(line_who_json_path, archive_config)
                f = open(line_who_json_path, "w", encoding="utf-8")
                f.write(new_line_who_config % (version))
                f.close()
                generated = True

        ### Other
        line_other_json_path = base_path + "config/line-alerts/other.json"
        if not os.path.isfile(line_other_json_path):
            f = open(line_other_json_path, "w", encoding="utf-8")
            f.write(new_line_other_config % (version))
            f.close()
            generated = True
        elif os.path.isfile(line_other_json_path):
            json_data = open(line_other_json_path, "r", encoding="utf-8")
            line_other_json = json.load(json_data)
            json_data.close()
            # Archive old line-alerts/other.json and re-generate one
            if not line_other_json["version"] == version:
                old_version = str(line_other_json["version"]).replace(".", "-")
                if not os.path.exists(base_path + "config/archive/"):
                    os.makedirs(base_path + "config/archive/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/"
                ):
                    os.makedirs(base_path + "config/archive/" + old_version + "/")
                if not os.path.exists(
                    base_path + "config/archive/" + old_version + "/line-alerts/"
                ):
                    os.makedirs(
                        base_path + "config/archive/" + old_version + "/line-alerts/"
                    )
                archive_config = (
                    base_path
                    + "config/archive/"
                    + old_version
                    + "/line-alerts/other.json"
                )
                os.rename(line_other_json_path, archive_config)
                f = open(line_other_json_path, "w", encoding="utf-8")
                f.write(new_line_other_config % (version))
                f.close()
                generated = True

        return generated

    except Exception as e:
        print(
            "build config: Error on line"
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


if __name__ == "__main__":
    main()
