#! /usr/bin/env python

"""
   Program:   EQ Alert
   File Name: eqa/lib/config.py
   Copyright (C) 2024 M Geitz

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

from dataclasses import asdict, dataclass, field
import json
import os
from typing import Dict
import re
import hashlib

import eqa.lib.state as eqa_state
import eqa.lib.struct as eqa_struct

from eqa.const.config_ability import NEW_LINE_ABILITY_CONFIG
from eqa.const.config_char import NEW_CHAR_CONFIG
from eqa.const.config_chat_sent import NEW_LINE_CHAT_SENT_CONFIG
from eqa.const.config_chat_received import NEW_LINE_CHAT_RECEIVED_CONFIG
from eqa.const.config_chat_npc import NEW_LINE_CHAT_NPC_CONFIG
from eqa.const.config_combat import NEW_LINE_COMBAT_CONFIG
from eqa.const.config_command import NEW_LINE_COMMAND_OUTPUT_CONFIG
from eqa.const.config_emote import NEW_LINE_EMOTES_CONFIG
from eqa.const.config_group import NEW_LINE_GROUP_SYSTEM_MESSAGES_CONFIG
from eqa.const.config_loot import NEW_LINE_LOOT_TRADE_CONFIG
from eqa.const.config_other import NEW_LINE_OTHER_CONFIG
from eqa.const.config_pets import NEW_LINE_PETS_CONFIG
from eqa.const.config_settings import NEW_SETTINGS_CONFIG
from eqa.const.config_spell_general import NEW_LINE_SPELL_GENERAL_CONFIG
from eqa.const.config_spell_specific import NEW_LINE_SPELL_SPECIFIC_CONFIG
from eqa.const.config_system import NEW_LINE_SYSTEM_MESSAGES_CONFIG
from eqa.const.config_who import NEW_LINE_WHO_CONFIG
from eqa.const.config_zones import NEW_ZONES_CONFIG
from eqa.const.data_spell_casters import NEW_SPELL_CASTER_DATA
from eqa.const.data_spell_items import NEW_SPELL_ITEMS_DATA
from eqa.const.data_spell_lines import NEW_SPELL_LINES_DATA
from eqa.const.validspells import VALID_SPELLS
from eqa.lib.util import handleException


@dataclass
class SpellTimer:
    cast_time: str
    duration: str
    formula: str


@dataclass
class SpellTimerJSON:
    hash: str
    version: str
    spells: Dict[str, SpellTimer] = field(default_factory=lambda: {}, compare=False)


def init(base_path, version):
    """Create any missing config files"""
    try:
        generated = build_config(base_path, version)

        if generated:
            print("One or more new versioned configuration files have been generated.")
            print("Older files have been archived under config/archive/\n")
            print("Please validate your config/settings.json and relaunch eqalert.")
            exit(0)

    except Exception as e:
        handleException(e, "config init", e_print=False, e_log=True)


def read_config(base_path):
    """All the config"""
    try:
        # Read "config" files
        # like {base_path}/{config_dir}/{config_file}.json
        config_dir = os.path.join(base_path, "config")
        config_files = ["characters", "settings", "zones"]
        config_filetype_ext = ".json"

        configs = {}

        for config_file in config_files:
            config_full_filepath = os.path.join(
                config_dir, f"{config_file}{config_filetype_ext}"
            )

            with open(config_full_filepath, "r", encoding="utf-8") as json_data:
                config_file_data = json.load(json_data)

            configs[config_file] = eqa_struct.config_file(
                config_file, config_full_filepath, config_file_data
            )

        # Read "line_alert" files
        # like {base_path}/{config_dir}/{line-alerts}/{config_file}.json
        line_alert_dir = os.path.join(config_dir, "line-alerts")
        line_alert_files = [
            "combat",
            "spell-general",
            "spell-specific",
            "pets",
            "chat-received-npc",
            "chat-received",
            "chat-sent",
            "ability-output",
            "command-output",
            "system-messages",
            "group-system-messages",
            "loot-trade",
            "emotes",
            "who",
            "other",
        ]

        line_alerts = {"line": {}, "version": ""}

        for line_alert in line_alert_files:
            line_alert_full_filepath = os.path.join(
                line_alert_dir, f"{line_alert}{config_filetype_ext}"
            )

            with open(line_alert_full_filepath, "r", encoding="utf-8") as json_data:
                line_alert_data = json.load(json_data)

            line_alerts["line"].update(line_alert_data["line"])
            line_alerts["version"] = line_alert_data.get("version")

        config_line_alerts = eqa_struct.config_file("line-alerts", None, line_alerts)

        configs = eqa_struct.configs(
            configs["characters"],
            configs["settings"],
            configs["zones"],
            config_line_alerts,
        )

        return configs

    except Exception as e:
        handleException(e, "config read", e_print=True, e_log=True)


def update_logs(configs, version):
    """Add characters and servers of eqemu_ prefixed files in the log path"""

    try:
        log_files = [
            f
            for f in os.listdir(
                configs.settings.config["settings"]["paths"]["everquest_logs"]
            )
            if os.path.isfile(
                os.path.join(
                    configs.settings.config["settings"]["paths"]["everquest_logs"], f
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

        validate_char_log(configs, version)

    except Exception as e:
        handleException(e, "config chars", e_print=True, e_log=True)


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
                    "disabled": False,
                    "char_state": {
                        "location": {"x": "0.00", "y": "0.00", "z": "0.00"},
                        "direction": None,
                        "zone": None,
                        "encumbered": False,
                        "bind": None,
                        "level": None,
                        "class": None,
                        "guild": None,
                    },
                }
            }
        )
        with open(configs.characters.path, "w", encoding="utf-8") as json_data:
            json.dump(configs.characters.config, json_data, sort_keys=True, indent=2)

    except Exception as e:
        handleException(e, "add char", e_print=True, e_log=True)


def validate_char_log(configs, version):
    """Validate characters.json"""

    try:
        with open(configs.characters.path, "r", encoding="utf-8") as json_data:
            characters_json_data = json.load(json_data)

        if "version" in characters_json_data.keys():
            # For any future needed changes
            pass
        else:
            # no version
            for char_log in characters_json_data["char_logs"].keys():
                if (
                    characters_json_data["char_logs"][char_log]["char_state"]["bind"]
                    == "unavailable"
                ):
                    characters_json_data["char_logs"][char_log]["char_state"][
                        "bind"
                    ] = None
                if (
                    characters_json_data["char_logs"][char_log]["char_state"]["class"]
                    == "unavailable"
                ):
                    characters_json_data["char_logs"][char_log]["char_state"][
                        "class"
                    ] = None
                if (
                    characters_json_data["char_logs"][char_log]["char_state"][
                        "direction"
                    ]
                    == "unavailable"
                ):
                    characters_json_data["char_logs"][char_log]["char_state"][
                        "direction"
                    ] = None
                if (
                    characters_json_data["char_logs"][char_log]["char_state"][
                        "encumbered"
                    ]
                    == "false"
                ):
                    characters_json_data["char_logs"][char_log]["char_state"][
                        "encumbered"
                    ] = False
                if (
                    characters_json_data["char_logs"][char_log]["char_state"][
                        "encumbered"
                    ]
                    == "true"
                ):
                    characters_json_data["char_logs"][char_log]["char_state"][
                        "encumbered"
                    ] = True
                if (
                    characters_json_data["char_logs"][char_log]["char_state"]["guild"]
                    == "unavailable"
                ):
                    characters_json_data["char_logs"][char_log]["char_state"][
                        "guild"
                    ] = None
                if (
                    characters_json_data["char_logs"][char_log]["char_state"]["level"]
                    == "unavailable"
                ):
                    characters_json_data["char_logs"][char_log]["char_state"][
                        "level"
                    ] = None
                else:
                    characters_json_data["char_logs"][char_log]["char_state"][
                        "level"
                    ] = int(
                        characters_json_data["char_logs"][char_log]["char_state"][
                            "level"
                        ]
                    )
                if (
                    characters_json_data["char_logs"][char_log]["char_state"]["zone"]
                    == "unavailable"
                ):
                    characters_json_data["char_logs"][char_log]["char_state"][
                        "zone"
                    ] = None
                if characters_json_data["char_logs"][char_log]["disabled"] == "false":
                    characters_json_data["char_logs"][char_log]["disabled"] = False
                if characters_json_data["char_logs"][char_log]["disabled"] == "true":
                    characters_json_data["char_logs"][char_log]["disabled"] = True

            characters_json_data["version"] = version

            with open(configs.characters.path, "w", encoding="utf-8") as json_data:
                json.dump(characters_json_data, json_data, sort_keys=True, indent=2)

    except Exception as e:
        handleException(e, "validate char log", e_print=False, e_log=True)


def bootstrap_state(configs, char, server):
    """Generate and save state to config"""

    try:
        data = configs.settings.config
        data["last_state"].update(
            {
                "server": server,
                "character": char,
                "afk": False,
                "group": False,
                "leader": False,
                "raid": False,
            }
        )
        with open(configs.settings.path, "w", encoding="utf-8") as json_data:
            json.dump(data, json_data, sort_keys=True, indent=2)

    except Exception as e:
        handleException(e, "bootstrap state", e_print=False, e_log=True)


def get_config_chars(configs):
    """Return each unique character log"""
    try:
        chars = []
        for char_server in configs.characters.config["char_logs"].keys():
            if not configs.characters.config["char_logs"][char_server]["disabled"]:
                chars.append(char_server)

        return chars

    except Exception as e:
        handleException(e, "get config chars", e_print=False, e_log=True)


def get_spell_timers(data_path):
    """Return spell timers file"""

    try:
        spell_timers_file = data_path + "spell-timers.json"
        with open(spell_timers_file, "r", encoding="utf-8") as json_data:
            spell_timers = json.load(json_data)

        return spell_timers

    except Exception as e:
        handleException(e, "cget spell timers", e_print=False, e_log=True)


def get_spell_casters(data_path):
    """Return spell casters file"""

    try:
        spell_casters_file = data_path + "spell-casters.json"
        with open(spell_casters_file, "r", encoding="utf-8") as json_data:
            spell_casters = json.load(json_data)

        return spell_casters

    except Exception as e:
        handleException(e, "get spell casters", e_print=False, e_log=True)


def get_spell_items(data_path):
    """Return spell items file"""

    try:
        spell_items_file = data_path + "spell-items.json"
        with open(spell_items_file, "r", encoding="utf-8") as json_data:
            spell_items = json.load(json_data)

        return spell_items

    except Exception as e:
        handleException(e, "get spell items", e_print=False, e_log=True)


def update_spell_casters(data_path, version):
    """Update data/spell-casters.json"""

    try:
        spell_casters_path = data_path + "spell-casters.json"
        generate = True

        if os.path.isfile(spell_casters_path):
            with open(spell_casters_path, "r", encoding="utf-8") as json_data:
                spell_casters = json.load(json_data)

            if spell_casters["version"] == version:
                generate = False

        if generate:
            print("    - generating spell-casters.json")
            with open(spell_casters_path, "w", encoding="utf-8") as f:
                f.write(NEW_SPELL_CASTER_DATA % (version))

    except Exception as e:
        handleException(e, "update spell casters", e_print=False, e_log=True)


def update_spell_items(data_path, version):
    """Update data/spell-items.json"""

    try:
        spell_items_path = data_path + "spell-items.json"
        generate = True

        if os.path.isfile(spell_items_path):
            with open(spell_items_path, "r", encoding="utf-8") as json_data:
                spell_items = json.load(json_data)

            if spell_items["version"] == version:
                generate = False

        if generate:
            print("    - generating spell-items.json")
            with open(spell_items_path, "w", encoding="utf-8") as f:
                f.write(NEW_SPELL_ITEMS_DATA % (version))

    except Exception as e:
        handleException(e, "update spell items", e_print=False, e_log=True)


def update_spell_lines(data_path, version):
    """Update data/spell-lines.json"""

    try:
        spell_lines_path = data_path + "spell-lines.json"
        generate = True

        if os.path.isfile(spell_lines_path):
            with open(spell_lines_path, "r", encoding="utf-8") as json_data:
                spell_lines = json.load(json_data)

            if spell_lines["version"] == version:
                generate = False

        if generate:
            print("    - generating spell-lines.json")
            with open(spell_lines_path, "w", encoding="utf-8") as f:
                f.write(NEW_SPELL_LINES_DATA % (version))

    except Exception as e:
        handleException(e, "update spell lines", e_print=False, e_log=True)


def get_spell_lines(data_path):
    """Return spell-lines.json"""

    try:
        spell_lines_path = data_path + "spell-lines.json"
        with open(spell_lines_path, "r", encoding="utf-8") as json_data:
            spell_lines = json.load(json_data)

        return spell_lines

    except Exception as e:
        handleException(e, "get spell lines", e_print=False, e_log=True)


def update_spell_timers(data_path, eq_spells_file_path, version):
    """Parse spells_us.txt to data/spell-timers.json"""

    try:
        spell_timers_file_name = "spell-timers.json"
        spell_timer_file = data_path + spell_timers_file_name

        # Read spells_us.txt
        with open(eq_spells_file_path, "r") as eq_spells_file:
            eq_spells_file_lines = eq_spells_file.readlines()

        # Calculate file hash
        BLOCKSIZE = 65536
        file_hash = hashlib.md5()
        with open(eq_spells_file_path, "r") as spells_file:
            buf = spells_file.read(BLOCKSIZE)
            while len(buf) > 0:
                file_hash.update(buf.encode("utf-8"))
                buf = spells_file.read(BLOCKSIZE)
        spells_hash = file_hash.hexdigest()

        # Parse EQ spells file into Spell Timer JSON
        spell_timer_json = generate_spell_timer_json(
            spells_hash, eq_spells_file_lines, VALID_SPELLS, version
        )

        # Write to disk
        spell_timer_json_dump = asdict(spell_timer_json)

        with open(spell_timer_file, "w") as json_data:
            json.dump(spell_timer_json_dump, json_data, sort_keys=True, indent=2)

    except Exception as e:
        handleException(e, "update spell timers", e_print=False, e_log=True)


def generate_spell_timer_json(
    spells_hash, eq_spells_file_lines, VALID_SPELLS, version
) -> SpellTimerJSON:
    spell_timer_json = SpellTimerJSON(spells_hash, version)

    # Read spells_us.txt line
    for line in eq_spells_file_lines:
        modified_line = line.split("^")

        ## Relevant values
        spell_name = modified_line[1]
        spell_cast_time = str(int(modified_line[13]) / 1000)
        spell_buff_duration = modified_line[17]
        spell_buffdurationformula = modified_line[16]

        # Spell timers only pertain to spells that have an effect with a duration, like DoT's or Buffs
        if spell_buffdurationformula == "0":
            continue

        ## Clean spell name
        line_type_spell_name = re.sub(r"[^a-z\s]", "", spell_name.lower()).replace(
            " ", "_"
        )

        if line_type_spell_name in VALID_SPELLS:
            spell_timer_data = SpellTimer(
                spell_cast_time, spell_buff_duration, spell_buffdurationformula
            )
            spell_timer_json.spells[line_type_spell_name] = spell_timer_data

    return spell_timer_json


def set_last_state(state, configs):
    """Save state to config"""

    try:
        configs.settings.config["last_state"].update(
            {
                "server": str(state.server),
                "character": str(state.char),
                "afk": state.afk,
                "group": state.group,
                "leader": state.leader,
                "raid": state.raid,
            }
        )
        configs.settings.config["settings"]["encounter_parsing"].update(
            {"auto_save": state.save_parse, "enabled": state.encounter_parse}
        )
        configs.settings.config["settings"]["raid_mode"].update(
            {
                "auto_set": state.auto_raid,
            }
        )
        configs.settings.config["settings"]["timers"]["mob"].update(
            {
                "auto": state.auto_mob_timer,
            }
        )
        configs.settings.config["settings"]["timers"]["mob"].update(
            {
                "auto_delay": state.auto_mob_timer_delay,
            }
        )
        configs.settings.config["settings"]["timers"]["spell"].update(
            {
                "delay": state.spell_timer_delay,
            }
        )
        configs.settings.config["settings"]["timers"]["spell"].update(
            {
                "guess": state.spell_timer_guess,
            }
        )
        configs.settings.config["settings"]["timers"]["spell"]["filter"].update(
            {
                "guild_only": state.spell_timer_guild_only,
            }
        )
        configs.settings.config["settings"]["timers"]["spell"]["filter"].update(
            {
                "yours_only": state.spell_timer_yours_only,
            }
        )
        configs.settings.config["settings"]["timers"]["spell"].update(
            {
                "other": state.spell_timer_other,
            }
        )
        configs.settings.config["settings"]["timers"]["spell"].update(
            {
                "self": state.spell_timer_self,
            }
        )
        configs.settings.config["settings"]["consider_eval"].update(
            {"enabled": state.consider_eval}
        )
        configs.settings.config["settings"]["debug_mode"].update(
            {"enabled": state.debug}
        )
        configs.settings.config["settings"]["detect_character"].update(
            {"enabled": state.detect_char}
        )
        configs.settings.config["settings"]["mute"].update({"enabled": state.mute})
        configs.characters.config["char_logs"][state.char + "_" + state.server].update(
            {
                "char": str(state.char),
                "disabled": False,
                "file_name": "eqlog_"
                + str(state.char)
                + "_"
                + str(state.server)
                + ".txt",
                "server": str(state.server),
                "char_state": {
                    "direction": state.direction,
                    "location": {
                        "x": state.loc[1],
                        "y": state.loc[0],
                        "z": state.loc[2],
                    },
                    "zone": state.zone,
                    "encumbered": state.encumbered,
                    "bind": state.bind,
                    "level": state.char_level,
                    "class": state.char_class,
                    "guild": state.char_guild,
                },
            }
        )
        with open(configs.settings.path, "w", encoding="utf-8") as json_data:
            json.dump(
                configs.settings.config,
                json_data,
                sort_keys=True,
                ensure_ascii=False,
                indent=2,
            )

        with open(configs.characters.path, "w", encoding="utf-8") as json_data:
            json.dump(
                configs.characters.config,
                json_data,
                sort_keys=True,
                ensure_ascii=False,
                indent=2,
            )

    except Exception as e:
        handleException(e, "set last state", e_print=False, e_log=True)


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
        consider_eval = configs.settings.config["settings"]["consider_eval"]["enabled"]
        debug = configs.settings.config["settings"]["debug_mode"]["enabled"]
        detect_char = configs.settings.config["settings"]["detect_character"]["enabled"]
        mute = configs.settings.config["settings"]["mute"]["enabled"]
        save_parse = configs.settings.config["settings"]["encounter_parsing"][
            "auto_save"
        ]
        auto_raid = configs.settings.config["settings"]["raid_mode"]["auto_set"]
        auto_mob_timer = configs.settings.config["settings"]["timers"]["mob"]["auto"]
        auto_mob_timer_delay = configs.settings.config["settings"]["timers"]["mob"][
            "auto_delay"
        ]
        spell_timer_delay = configs.settings.config["settings"]["timers"]["spell"][
            "delay"
        ]
        spell_timer_guess = configs.settings.config["settings"]["timers"]["spell"][
            "guess"
        ]
        spell_timer_other = configs.settings.config["settings"]["timers"]["spell"][
            "other"
        ]
        spell_timer_guild_only = configs.settings.config["settings"]["timers"]["spell"][
            "filter"
        ]["guild_only"]
        spell_timer_yours_only = configs.settings.config["settings"]["timers"]["spell"][
            "filter"
        ]["yours_only"]
        spell_timer_self = configs.settings.config["settings"]["timers"]["spell"][
            "self"
        ]
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
            auto_mob_timer_delay,
            consider_eval,
            detect_char,
            spell_timer_delay,
            spell_timer_guess,
            spell_timer_other,
            spell_timer_guild_only,
            spell_timer_self,
            spell_timer_yours_only,
        )

        return state

    except Exception as e:
        handleException(e, "get last state", e_print=False, e_log=True)


def add_type(line_type, base_path):
    """Adds default setting values for new line_type"""

    try:
        with open(
            base_path + "config/line-alerts/other.json", "r", encoding="utf-8"
        ) as json_data:
            data = json.load(json_data)

        data["line"].update(
            {line_type: {"sound": False, "reaction": False, "alert": {}}}
        )

        with open(
            base_path + "config/line-alerts/other.json", "w", encoding="utf-8"
        ) as json_data:
            json.dump(data, json_data, sort_keys=True, indent=2)

    except Exception as e:
        handleException(e, "add type", e_print=False, e_log=True)


def add_zone(zone, base_path):
    """Adds default setting values for new zones"""

    try:
        with open(base_path + "config/zones.json", "r", encoding="utf-8") as json_data:
            data = json.load(json_data)

        data["zones"].update(
            {str(zone): {"indoors": False, "raid_mode": False, "timer": 0}}
        )
        with open(base_path + "config/zones.json", "w", encoding="utf-8") as json_data:
            json.dump(data, json_data, sort_keys=True, indent=2)

    except Exception as e:
        handleException(e, "add zone", e_print=False, e_log=True)


def get_players_file(player_data_path, server):
    """Update Player Data File"""

    try:
        player_data_file = player_data_path + "players.json"
        with open(player_data_file, "r", encoding="utf-8") as json_data:
            player_json_data = json.load(json_data)

        player_list = player_json_data["server"][server]["players"]

        return player_list

    except Exception as e:
        handleException(e, "get players file", e_print=False, e_log=True)


def update_players_file(player_data_path, server, player_list):
    """Update Player Data File"""

    try:
        player_data_file = player_data_path + "players.json"
        with open(player_data_file, "r", encoding="utf-8") as json_data:
            player_json_data = json.load(json_data)

        if server not in player_json_data["server"].keys():
            player_json_data["servers"][server] = {"players": {}}

        player_json_data["server"][server]["players"].update(player_list)

        with open(player_data_file, "w", encoding="utf-8") as json_data:
            json.dump(player_json_data, json_data, sort_keys=True, indent=2)

    except Exception as e:
        handleException(e, "update players file", e_print=False, e_log=True)


def generate_players_file(player_data_file, version):
    """Bootstrap Player Data File"""

    new_players_data = """
{
  "server": {
    "P1999Green": {
      "players": {}
    },
    "project1999": {
      "players": {}
    }
  },
  "version": "%s"
}
"""

    try:
        print("    - generating players.json")
        with open(player_data_file, "w", encoding="utf-8") as f:
            f.write(new_players_data % (version))

    except Exception as e:
        handleException(e, "generate players file", e_print=False, e_log=True)


def validate_players_file(player_data_file, version):
    """Validate Player Data File"""

    try:
        with open(player_data_file, "r", encoding="utf-8") as json_data:
            player_json_data = json.load(json_data)

        if "version" in player_json_data.keys():
            # For any future needed changes
            pass
        else:
            # no version
            updated_player_list = {"server": {}, "version": version}
            for server in player_json_data["server"].keys():
                updated_player_list["server"][server] = {"players": {}}
                for player in player_json_data["server"][server]["players"].keys():
                    if (
                        player_json_data["server"][server]["players"][player]["guild"]
                        != "none"
                    ):
                        char_guild = player_json_data["server"][server]["players"][
                            player
                        ]["guild"]
                    else:
                        char_guild = None
                    if (
                        player_json_data["server"][server]["players"][player]["class"]
                        != "unknown"
                    ):
                        char_class = player_json_data["server"][server]["players"][
                            player
                        ]["class"]
                    else:
                        char_class = None
                    char_level = int(
                        player_json_data["server"][server]["players"][player]["level"]
                    )

                    updated_player_list["server"][server]["players"][player] = {
                        "class": char_class,
                        "guild": char_guild,
                        "level": char_level,
                    }

            with open(player_data_file, "w", encoding="utf-8") as json_data:
                json.dump(updated_player_list, json_data, sort_keys=True, indent=2)

    except Exception as e:
        handleException(e, "validate players file", e_print=False, e_log=True)


def build_config(base_path, version):
    """Build a default config"""

    try:
        home = os.path.expanduser("~")
        generated = False

        # Check for old config.yml
        legacy_config_json_path = base_path + "config.json"
        if os.path.isfile(legacy_config_json_path):
            with open(legacy_config_json_path, "r", encoding="utf-8") as json_data:
                legacy_config_json = json.load(json_data)

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
            with open(characters_json_path, "w", encoding="utf-8") as f:
                f.write(NEW_CHAR_CONFIG % (version))

            generated = True

        ## Settings

        # fmt: off
        configs = [
            ("settings", NEW_SETTINGS_CONFIG),
            ("zones", NEW_ZONES_CONFIG),
            ("line-alerts/combat", NEW_LINE_COMBAT_CONFIG),
            ("line-alerts/spell-general", NEW_LINE_SPELL_GENERAL_CONFIG),
            ("line-alerts/spell-specific", NEW_LINE_SPELL_SPECIFIC_CONFIG),
            ("line-alerts/pets", NEW_LINE_PETS_CONFIG),
            ("line-alerts/chat-received-npc", NEW_LINE_CHAT_NPC_CONFIG),
            ("line-alerts/chat-received", NEW_LINE_CHAT_RECEIVED_CONFIG),
            ("line-alerts/chat-sent", NEW_LINE_CHAT_SENT_CONFIG),
            ("line-alerts/ability-output", NEW_LINE_ABILITY_CONFIG),
            ("line-alerts/command-output", NEW_LINE_COMMAND_OUTPUT_CONFIG),
            ("line-alerts/system-messages", NEW_LINE_SYSTEM_MESSAGES_CONFIG),
            ("line-alerts/group-system-messages",NEW_LINE_GROUP_SYSTEM_MESSAGES_CONFIG),
            ("line-alerts/loot-trade", NEW_LINE_LOOT_TRADE_CONFIG),
            ("line-alerts/emotes", NEW_LINE_EMOTES_CONFIG),
            ("line-alerts/who", NEW_LINE_WHO_CONFIG),
            ("line-alerts/other", NEW_LINE_OTHER_CONFIG),
        ]
        # fmt: on

        for config in configs:
            generated = write_config(base_path, version, *config) or generated

        return generated

    except Exception as e:
        handleException(e, "build config")


def write_config(base_path, version, config_name, new_config) -> bool:
    """Create any missing config files"""
    try:
        # Determine Config Path
        generated = False

        line_json_path = base_path + "config/" + config_name + ".json"
        home = os.path.expanduser("~")

        ## If the config does not exist
        if not os.path.isfile(line_json_path):
            with open(line_json_path, "w", encoding="utf-8") as f:
                if config_name == "settings":
                    f.write(
                        new_config
                        % (base_path, base_path, home, home, base_path, version)
                    )
                else:
                    f.write(new_config % (version))

            generated = True
        ## If the config exists
        elif os.path.isfile(line_json_path):
            ### Validate file is readable

            old_version = "unknown"
            # do we still need to generate a new config?
            # we'll determine that by checking the version in the existing config
            generate_config = False
            try:
                with open(line_json_path, "r", encoding="utf-8") as json_data:
                    line_json = json.load(json_data)
                old_version = str(line_json["version"]).replace(".", "-")

                if not line_json["version"] == version:
                    generate_config = True
            except:
                generate_config = True
            ### Archive the old and regenerate a new config
            if generate_config:
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
                    + "/"
                    + config_name
                    + ".json"
                )
                os.rename(line_json_path, archive_config)

                with open(line_json_path, "w", encoding="utf-8") as f:
                    if config_name == "settings":
                        f.write(
                            new_config
                            % (
                                base_path,
                                base_path,
                                home,
                                home,
                                base_path,
                                version,
                            )
                        )
                    else:
                        f.write(new_config % (version))
                generated = True

        return generated

    except Exception as e:
        handleException(e, "write config line alert", e_print=True, e_log=False)
        return generated
