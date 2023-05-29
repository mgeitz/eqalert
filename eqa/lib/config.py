#! /usr/bin/env python

"""
   Program:   EQ Alert
   File Name: eqa/lib/config.py
   Copyright (C) 2023 M Geitz

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
import re
import hashlib

import eqa.lib.settings as eqa_settings
import eqa.lib.state as eqa_state
import eqa.lib.struct as eqa_struct


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
            base_path + "config/line-alerts/chat-received-npc.json"
        )
        json_data = open(config_path_line_chat_recieved_npc, "r", encoding="utf-8")
        config_file_line_alerts = json.load(json_data)
        json_data.close()
        line_alerts["line"].update(config_file_line_alerts["line"])

        ## Chat Recieved
        config_path_line_chat_recieved = (
            base_path + "config/line-alerts/chat-received.json"
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


def get_spell_timers(data_path):
    """Return spell timers file"""

    try:
        spell_timers_file = data_path + "spell-timers.json"
        json_data = open(spell_timers_file, "r", encoding="utf-8")
        spell_timers = json.load(json_data)
        json_data.close()

        return spell_timers

    except Exception as e:
        eqa_settings.log(
            "get spell timers: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def get_spell_casters(data_path):
    """Return spell casters file"""

    try:
        spell_casters_file = data_path + "spell-casters.json"
        json_data = open(spell_casters_file, "r", encoding="utf-8")
        spell_casters = json.load(json_data)
        json_data.close()

        return spell_casters

    except Exception as e:
        eqa_settings.log(
            "get spell casters: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def update_spell_casters(data_path, version):
    """Update data/spell-casters.json"""

    new_spell_caster_data = """
{
  "spells": {
    "aanyas_quickening": {
      "classes": {
        "enchanter": "53"
      },
      "npc": "false",
      "item": "false"
    },
    "accuracy": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "acid_jet": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "acumen": {
      "classes": {
        "shaman": 56
      },
      "npc": "false",
      "item": "false"
    },
    "adorning_grace": {
      "classes": {
        "enchanter": "49"
      },
      "npc": "false",
      "item": "false"
    },
    "adroitness": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "aegis": {
      "classes": {
        "cleric": 57
      },
      "npc": "false",
      "item": "false"
    },
    "aegis_of_bathezid": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "aegis_of_ro": {
      "classes": {
        "magician": 60
      },
      "npc": "false",
      "item": "false"
    },
    "aegolism": {
      "classes": {
        "cleric": 60
      },
      "npc": "false",
      "item": "false"
    },
    "affliction": {
      "classes": {
        "shaman": 19
      },
      "npc": "true",
      "item": "false"
    },
    "agility": {
      "classes": {
        "shaman": 44
      },
      "npc": "false",
      "item": "false"
    },
    "agilmentes_aria_of_eagles": {
      "classes": {
        "bard": 31
      },
      "npc": "false",
      "item": "true"
    },
    "alacrity": {
      "classes": {
        "enchanter": "24",
        "shaman": 44
      },
      "npc": "false",
      "item": "true"
    },
    "allure": {
      "classes": {
        "enchanter": "49"
      },
      "npc": "false",
      "item": "true"
    },
    "allure_of_death": {
      "classes": {
        "necromancer": 20
      },
      "npc": "false",
      "item": "true"
    },
    "allure_of_the_wild": {
      "classes": {
        "druid": 44
      },
      "npc": "false",
      "item": "false"
    },
    "alluring_aura": {
      "classes": {
        "shaman": 29
      },
      "npc": "false",
      "item": "false"
    },
    "alluring_whispers": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "aloe_sweat": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "ancient_breath": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "anthem_de_arms": {
      "classes": {
        "bard": 10
      },
      "npc": "false",
      "item": "false"
    },
    "arch_lich": {
      "classes": {
        "necromancer": 60
      },
      "npc": "false",
      "item": "false"
    },
    "arch_shielding": {
      "classes": {
        "enchanter": "44",
        "magician": 44,
        "necromancer": 44,
        "wizard": 44
      },
      "npc": "false",
      "item": "true"
    },
    "armor_of_faith": {
      "classes": {
        "cleric": 39,
        "paladin": 49
      },
      "npc": "false",
      "item": "true"
    },
    "armor_of_protection": {
      "classes": {
        "cleric": 34
      },
      "npc": "false",
      "item": "false"
    },
    "asphyxiate": {
      "classes": {
        "enchanter": "59"
      },
      "npc": "false",
      "item": "false"
    },
    "assiduous_vision": {
      "classes": {
        "shaman": 39
      },
      "npc": "false",
      "item": "false"
    },
    "asystole": {
      "classes": {
        "necromancer": 44,
        "shadow knight": 60
      },
      "npc": "false",
      "item": "false"
    },
    "atols_spectral_shackles": {
      "classes": {
        "wizard": 51
      },
      "npc": "false",
      "item": "false"
    },
    "augment": {
      "classes": {
        "enchanter": "56"
      },
      "npc": "false",
      "item": "false"
    },
    "augment_death": {
      "classes": {
        "necromancer": 39
      },
      "npc": "false",
      "item": "true"
    },
    "augmentation": {
      "classes": {
        "enchanter": "29"
      },
      "npc": "false",
      "item": "false"
    },
    "augmentation_of_death": {
      "classes": {
        "necromancer": 55
      },
      "npc": "false",
      "item": "false"
    },
    "aura_of_antibody": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "aura_of_battle": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "aura_of_black_petals": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "aura_of_blue_petals": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "aura_of_cold": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "aura_of_green_petals": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "aura_of_heat": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "aura_of_marr": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "aura_of_purity": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "aura_of_red_petals": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "aura_of_white_petals": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "avatar": {
      "classes": {
        "shaman": "60"
      },
      "npc": "false",
      "item": "true"
    },
    "avatar_snare": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "bane_of_nife": {
      "classes": {
        "shaman": 56
      },
      "npc": "false",
      "item": "false"
    },
    "banshee_aura": {
      "classes": {
        "necromancer": 16,
        "shadow knight": 54
      },
      "npc": "false",
      "item": "false"
    },
    "barbcoat": {
      "classes": {
        "druid": 19,
        "ranger": 30
      },
      "npc": "false",
      "item": "false"
    },
    "barrier_of_combustion": {
      "classes": {
        "magician": 39
      },
      "npc": "false",
      "item": "false"
    },
    "barrier_of_force": {
      "classes": {},
      "npc": "false",
      "item": "true"
    },
    "battery_vision": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "bedlam": {
      "classes": {
        "enchanter": "58"
      },
      "npc": "false",
      "item": "false"
    },
    "befriend_animal": {
      "classes": {
        "druid": 14,
        "shaman": 29
      },
      "npc": "false",
      "item": "true"
    },
    "beguile": {
      "classes": {
        "enchanter": "24"
      },
      "npc": "false",
      "item": "false"
    },
    "beguile_animals": {
      "classes": {
        "druid": 34
      },
      "npc": "false",
      "item": "false"
    },
    "beguile_plants": {
      "classes": {
        "druid": 29
      },
      "npc": "false",
      "item": "true"
    },
    "beguile_undead": {
      "classes": {
        "necromancer": 34
      },
      "npc": "false",
      "item": "false"
    },
    "bellowing_winds": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "berserker_madness_i": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "berserker_madness_ii": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "berserker_madness_iii": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "berserker_madness_iv": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "berserker_spirit": {
      "classes": {
        "enchanter": "49"
      },
      "npc": "false",
      "item": "false"
    },
    "berserker_strength": {
      "classes": {
        "enchanter": "20"
      },
      "npc": "false",
      "item": "true"
    },
    "bind_sight": {
      "classes": {
        "enchanter": "8",
        "ranger": 22,
        "wizard": 16
      },
      "npc": "false",
      "item": "false"
    },
    "bladecoat": {
      "classes": {
        "druid": 56
      },
      "npc": "false",
      "item": "false"
    },
    "blessing_of_nature": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "blessing_of_the_grove": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "blinding_fear": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "blinding_luminance": {
      "classes": {
        "cleric": 34,
        "shaman": 39
      },
      "npc": "false",
      "item": "true"
    },
    "blinding_poison_i": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "blinding_poison_iii": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "blinding_step": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "blood_claw": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "bobbing_corpse": {
      "classes": {
        "shadow knight": 55
      },
      "npc": "false",
      "item": "true"
    },
    "boil_blood": {
      "classes": {
        "necromancer": 29,
        "shadow knight": 53
      },
      "npc": "false",
      "item": "true"
    },
    "boiling_blood": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "boltrans_agacerie": {
      "classes": {
        "enchanter": "53"
      },
      "npc": "false",
      "item": "false"
    },
    "bond_of_death": {
      "classes": {
        "necromancer": 49
      },
      "npc": "false",
      "item": "false"
    },
    "bonds_of_force": {
      "classes": {
        "wizard": 29
      },
      "npc": "false",
      "item": "true"
    },
    "bonds_of_tunare": {
      "classes": {
        "druid": 57
      },
      "npc": "false",
      "item": "false"
    },
    "bone_melt": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "boon_of_immolation": {
      "classes": {
        "magician": 53
      },
      "npc": "false",
      "item": "false"
    },
    "boon_of_the_clear_mind": {
      "classes": {
        "enchanter": "52"
      },
      "npc": "false",
      "item": "false"
    },
    "boon_of_the_garou": {
      "classes": {
        "enchanter": "44"
      },
      "npc": "false",
      "item": "false"
    },
    "bramblecoat": {
      "classes": {
        "druid": 29,
        "ranger": 39
      },
      "npc": "false",
      "item": "true"
    },
    "bravery": {
      "classes": {
        "cleric": 24
      },
      "npc": "false",
      "item": "false"
    },
    "breath_of_ro": {
      "classes": {
        "druid": 52
      },
      "npc": "false",
      "item": "false"
    },
    "breath_of_the_dead": {
      "classes": {
        "necromancer": 24,
        "shadow knight": 49
      },
      "npc": "false",
      "item": "true"
    },
    "breath_of_the_sea": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "breeze": {
      "classes": {
        "enchanter": "16"
      },
      "npc": "false",
      "item": "false"
    },
    "brilliance": {
      "classes": {
        "enchanter": "44"
      },
      "npc": "false",
      "item": "false"
    },
    "brittle_haste_i": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "brittle_haste_ii": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "brittle_haste_iii": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "brittle_haste_iv": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "bulwark_of_faith": {
      "classes": {
        "cleric": 57
      },
      "npc": "false",
      "item": "false"
    },
    "burnout": {
      "classes": {
        "magician": 255
      },
      "npc": "false",
      "item": "false"
    },
    "burnout_ii": {
      "classes": {
        "magician": 29
      },
      "npc": "false",
      "item": "false"
    },
    "burnout_iii": {
      "classes": {
        "magician": 49
      },
      "npc": "false",
      "item": "true"
    },
    "burnout_iv": {
      "classes": {
        "magician": 55
      },
      "npc": "false",
      "item": "false"
    },
    "burrowing_scarab": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "burst_of_strength": {
      "classes": {
        "shaman": 14
      },
      "npc": "false",
      "item": "false"
    },
    "cadeau_of_flame": {
      "classes": {
        "magician": 56
      },
      "npc": "false",
      "item": "false"
    },
    "cajole_undead": {
      "classes": {
        "necromancer": 49
      },
      "npc": "false",
      "item": "false"
    },
    "calimony": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "call_of_bones": {
      "classes": {
        "necromancer": 34
      },
      "npc": "false",
      "item": "false"
    },
    "call_of_earth": {
      "classes": {
        "ranger": 50
      },
      "npc": "false",
      "item": "true"
    },
    "call_of_karana": {
      "classes": {
        "druid": 52
      },
      "npc": "false",
      "item": "false"
    },
    "call_of_sky": {
      "classes": {
        "ranger": 39
      },
      "npc": "false",
      "item": "false"
    },
    "call_of_the_predator": {
      "classes": {
        "ranger": 60
      },
      "npc": "false",
      "item": "false"
    },
    "calm": {
      "classes": {
        "cleric": 19,
        "enchanter": "20",
        "paladin": 49
      },
      "npc": "false",
      "item": "true"
    },
    "calm_animal": {
      "classes": {
        "druid": 19,
        "ranger": 39
      },
      "npc": "false",
      "item": "false"
    },
    "camouflage": {
      "classes": {
        "druid": 5,
        "ranger": 15
      },
      "npc": "false",
      "item": "false"
    },
    "captain_nalots_quickening": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "cascading_darkness": {
      "classes": {
        "necromancer": 49,
        "shadow knight": 59
      },
      "npc": "false",
      "item": "true"
    },
    "cassindras_chant_of_clarity": {
      "classes": {
        "bard": 20
      },
      "npc": "false",
      "item": "false"
    },
    "cassindras_elegy": {
      "classes": {
        "bard": 44
      },
      "npc": "false",
      "item": "false"
    },
    "cassindras_insipid_ditty": {
      "classes": {
        "bard": 57
      },
      "npc": "false",
      "item": "false"
    },
    "cast_sight": {
      "classes": {
        "enchanter": "34"
      },
      "npc": "false",
      "item": "false"
    },
    "celerity": {
      "classes": {
        "enchanter": "39",
        "shaman": 56
      },
      "npc": "false",
      "item": "false"
    },
    "celestial_cleansing": {
      "classes": {
        "paladin": 59
      },
      "npc": "false",
      "item": "false"
    },
    "celestial_healing": {
      "classes": {
        "cleric": 44
      },
      "npc": "false",
      "item": "false"
    },
    "celestial_tranquility": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "center": {
      "classes": {
        "cleric": 9,
        "paladin": 22
      },
      "npc": "false",
      "item": "false"
    },
    "cessation_of_cor": {
      "classes": {
        "necromancer": 56
      },
      "npc": "false",
      "item": "false"
    },
    "chant_of_battle": {
      "classes": {
        "bard": 1
      },
      "npc": "false",
      "item": "true"
    },
    "charisma": {
      "classes": {
        "shaman": 49
      },
      "npc": "false",
      "item": "false"
    },
    "chase_the_moon": {
      "classes": {
        "enchanter": "16"
      },
      "npc": "false",
      "item": "false"
    },
    "chill_bones": {
      "classes": {
        "necromancer": 55
      },
      "npc": "false",
      "item": "false"
    },
    "chill_of_unlife": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "chill_sight": {
      "classes": {
        "ranger": 56,
        "wizard": 39
      },
      "npc": "false",
      "item": "true"
    },
    "chilling_embrace": {
      "classes": {
        "necromancer": 39
      },
      "npc": "false",
      "item": "false"
    },
    "chloroplast": {
      "classes": {
        "druid": 44,
        "ranger": 55,
        "shaman": 39
      },
      "npc": "false",
      "item": "true"
    },
    "choke": {
      "classes": {
        "enchanter": "12"
      },
      "npc": "false",
      "item": "true"
    },
    "chords_of_dissonance": {
      "classes": {
        "bard": 2
      },
      "npc": "false",
      "item": "false"
    },
    "cindas_charismatic_carillon": {
      "classes": {
        "bard": 11
      },
      "npc": "false",
      "item": "false"
    },
    "circle_of_summer": {
      "classes": {
        "druid": 52
      },
      "npc": "false",
      "item": "false"
    },
    "circle_of_winter": {
      "classes": {
        "druid": 51
      },
      "npc": "false",
      "item": "false"
    },
    "clarity": {
      "classes": {
        "enchanter": "29"
      },
      "npc": "false",
      "item": "true"
    },
    "clarity_ii": {
      "classes": {
        "enchanter": "54"
      },
      "npc": "false",
      "item": "false"
    },
    "clinging_darkness": {
      "classes": {
        "necromancer": 4,
        "shadow knight": 15
      },
      "npc": "false",
      "item": "true"
    },
    "clockwork_poison": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "cloud": {
      "classes": {
        "enchanter": "20"
      },
      "npc": "false",
      "item": "true"
    },
    "cloud_of_disempowerment": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "cloud_of_fear": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "cloud_of_silence": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "cog_boost": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "cohesion": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "composition_of_ervaj": {
      "classes": {
        "bard": 60
      },
      "npc": "false",
      "item": "false"
    },
    "courage": {
      "classes": {
        "cleric": 1,
        "paladin": 9
      },
      "npc": "false",
      "item": "true"
    },
    "creeping_crud": {
      "classes": {
        "druid": 24
      },
      "npc": "false",
      "item": "false"
    },
    "creeping_vision": {
      "classes": {
        "shaman": 24
      },
      "npc": "false",
      "item": "true"
    },
    "cripple": {
      "classes": {
        "enchanter": "53",
        "shaman": 53
      },
      "npc": "false",
      "item": "false"
    },
    "crissions_pixie_strike": {
      "classes": {
        "bard": 28
      },
      "npc": "false",
      "item": "false"
    },
    "curse_of_the_simple_mind": {
      "classes": {
        "enchanter": "29"
      },
      "npc": "false",
      "item": "false"
    },
    "curse_of_the_spirits": {
      "classes": {},
      "npc": "false",
      "item": "true"
    },
    "dance_of_the_blade": {
      "classes": {},
      "npc": "false",
      "item": "true"
    },
    "daring": {
      "classes": {
        "cleric": 19,
        "paladin": 39
      },
      "npc": "false",
      "item": "true"
    },
    "dark_pact": {
      "classes": {
        "necromancer": 8
      },
      "npc": "false",
      "item": "false"
    },
    "dawncall": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "dazzle": {
      "classes": {
        "enchanter": "49"
      },
      "npc": "false",
      "item": "false"
    },
    "dead_man_floating": {
      "classes": {
        "necromancer": 44
      },
      "npc": "false",
      "item": "true"
    },
    "dead_men_floating": {
      "classes": {
        "necromancer": 49
      },
      "npc": "false",
      "item": "false"
    },
    "deadeye": {
      "classes": {
        "necromancer": 8,
        "shadow knight": 22
      },
      "npc": "false",
      "item": "true"
    },
    "deadly_poison": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "deadly_velium_poison": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "death_pact": {
      "classes": {
        "cleric": 51
      },
      "npc": "false",
      "item": "false"
    },
    "deftness": {
      "classes": {
        "shaman": 39
      },
      "npc": "false",
      "item": "true"
    },
    "deliriously_nimble": {
      "classes": {
        "shaman": 53
      },
      "npc": "false",
      "item": "false"
    },
    "demi_lich": {
      "classes": {
        "necromancer": 60
      },
      "npc": "false",
      "item": "false"
    },
    "denons_bereavement": {
      "classes": {
        "bard": 59
      },
      "npc": "false",
      "item": "false"
    },
    "denons_disruptive_discord": {
      "classes": {
        "bard": 18
      },
      "npc": "false",
      "item": "false"
    },
    "desperate_hope": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "devouring_darkness": {
      "classes": {
        "necromancer": 59
      },
      "npc": "false",
      "item": "false"
    },
    "dexterity": {
      "classes": {
        "shaman": 49
      },
      "npc": "false",
      "item": "false"
    },
    "dexterous_aura": {
      "classes": {
        "shaman": 1
      },
      "npc": "false",
      "item": "false"
    },
    "diamondskin": {
      "classes": {
        "necromancer": 44,
        "shadow knight": 59,
        "wizard": 44
      },
      "npc": "false",
      "item": "true"
    },
    "dictate": {
      "classes": {
        "enchanter": "60"
      },
      "npc": "false",
      "item": "false"
    },
    "disease": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "disease_cloud": {
      "classes": {
        "necromancer": 1,
        "shadow knight": 9
      },
      "npc": "false",
      "item": "true"
    },
    "diseased_cloud": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "disempower": {
      "classes": {
        "enchanter": "16",
        "shaman": 14
      },
      "npc": "false",
      "item": "true"
    },
    "divine_aura": {
      "classes": {
        "cleric": 1,
        "paladin": 55
      },
      "npc": "false",
      "item": "true"
    },
    "divine_barrier": {
      "classes": {
        "cleric": 29
      },
      "npc": "false",
      "item": "false"
    },
    "divine_favor": {
      "classes": {
        "paladin": 55
      },
      "npc": "false",
      "item": "false"
    },
    "divine_glory": {
      "classes": {
        "paladin": 53
      },
      "npc": "false",
      "item": "false"
    },
    "divine_intervention": {
      "classes": {
        "cleric": 60
      },
      "npc": "false",
      "item": "false"
    },
    "divine_might": {
      "classes": {
        "paladin": 49
      },
      "npc": "false",
      "item": "false"
    },
    "divine_purpose": {
      "classes": {
        "paladin": 39
      },
      "npc": "false",
      "item": "false"
    },
    "divine_strength": {
      "classes": {
        "paladin": 60
      },
      "npc": "false",
      "item": "false"
    },
    "dizzy_i": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "dizzy_ii": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "dizzy_iii": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "dizzy_iv": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "dominate_undead": {
      "classes": {
        "necromancer": 20
      },
      "npc": "false",
      "item": "false"
    },
    "dooming_darkness": {
      "classes": {
        "necromancer": 29,
        "shadow knight": 49
      },
      "npc": "false",
      "item": "true"
    },
    "draconic_rage": {
      "classes": {},
      "npc": "false",
      "item": "true"
    },
    "dragon_charm": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "dragon_roar": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "drifting_death": {
      "classes": {
        "druid": 44
      },
      "npc": "false",
      "item": "false"
    },
    "drones_of_doom": {
      "classes": {
        "druid": 34,
        "ranger": 54
      },
      "npc": "false",
      "item": "true"
    },
    "drowsy": {
      "classes": {
        "shaman": 5
      },
      "npc": "false",
      "item": "true"
    },
    "dulsehound": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "dyns_dizzying_draught": {
      "classes": {
        "enchanter": "29"
      },
      "npc": "false",
      "item": "false"
    },
    "earthcall": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "earthelementalattack": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "ebbing_strength": {
      "classes": {
        "enchanter": "12"
      },
      "npc": "false",
      "item": "false"
    },
    "echinacea_infusion": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "elemental_armor": {
      "classes": {
        "magician": 44,
        "wizard": 44
      },
      "npc": "false",
      "item": "true"
    },
    "elemental_maelstrom": {
      "classes": {
        "magician": 44
      },
      "npc": "false",
      "item": "false"
    },
    "elemental_rhythms": {
      "classes": {
        "bard": 9
      },
      "npc": "false",
      "item": "false"
    },
    "elemental_shield": {
      "classes": {
        "magician": 20,
        "wizard": 20
      },
      "npc": "false",
      "item": "false"
    },
    "embrace_of_the_kelpmaiden": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "endure_cold": {
      "classes": {
        "cleric": 14,
        "druid": 9,
        "necromancer": 4,
        "ranger": 22,
        "shadow knight": 15,
        "shaman": 1
      },
      "npc": "false",
      "item": "false"
    },
    "endure_disease": {
      "classes": {
        "cleric": 14,
        "druid": 19,
        "paladin": 39,
        "shadow knight": 30,
        "shaman": 9,
        "necromancer": 12
      },
      "npc": "false",
      "item": "false"
    },
    "endure_fire": {
      "classes": {
        "cleric": 9,
        "druid": 1,
        "ranger": 9,
        "shaman": 5
      },
      "npc": "false",
      "item": "true"
    },
    "endure_magic": {
      "classes": {
        "cleric": 19,
        "druid": 34,
        "enchanter": "20",
        "paladin": 30,
        "shaman": 19
      },
      "npc": "false",
      "item": "true"
    },
    "endure_poison": {
      "classes": {
        "cleric": 9,
        "druid": 19,
        "paladin": 22,
        "shaman": 14
      },
      "npc": "false",
      "item": "false"
    },
    "enduring_breath": {
      "classes": {
        "druid": 9,
        "enchanter": "12",
        "ranger": 22,
        "shaman": 14
      },
      "npc": "false",
      "item": "true"
    },
    "energy_sap": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "enfeeblement": {
      "classes": {
        "enchanter": "4"
      },
      "npc": "false",
      "item": "false"
    },
    "engulfing_darkness": {
      "classes": {
        "necromancer": 12,
        "shadow knight": 22
      },
      "npc": "false",
      "item": "true"
    },
    "enlightenment": {
      "classes": {
        "enchanter": "57"
      },
      "npc": "false",
      "item": "false"
    },
    "enslave_death": {
      "classes": {
        "necromancer": 60
      },
      "npc": "false",
      "item": "false"
    },
    "ensnare": {
      "classes": {
        "druid": 29,
        "ranger": 51
      },
      "npc": "false",
      "item": "true"
    },
    "enthrall": {
      "classes": {
        "enchanter": "16"
      },
      "npc": "false",
      "item": "false"
    },
    "entrance": {
      "classes": {
        "enchanter": "34"
      },
      "npc": "false",
      "item": "false"
    },
    "envenomed_bolt": {
      "classes": {
        "necromancer": 51,
        "shaman": 49
      },
      "npc": "false",
      "item": "false"
    },
    "envenomed_breath": {
      "classes": {
        "shaman": 24
      },
      "npc": "false",
      "item": "true"
    },
    "everlasting_breath": {
      "classes": {},
      "npc": "false",
      "item": "true"
    },
    "expedience": {
      "classes": {
        "magician": 29
      },
      "npc": "false",
      "item": "false"
    },
    "extended_regeneration": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "eye_of_confusion": {
      "classes": {
        "enchanter": "8"
      },
      "npc": "false",
      "item": "false"
    },
    "eye_of_tallon": {
      "classes": {
        "magician": 57,
        "wizard": 57
      },
      "npc": "false",
      "item": "false"
    },
    "eye_of_zomm": {
      "classes": {
        "magician": 8,
        "wizard": 8
      },
      "npc": "false",
      "item": "true"
    },
    "eyes_of_the_cat": {
      "classes": {
        "ranger": 30
      },
      "npc": "false",
      "item": "false"
    },
    "fascination": {
      "classes": {
        "enchanter": "52"
      },
      "npc": "false",
      "item": "false"
    },
    "feast_of_blood": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "feckless_might": {
      "classes": {
        "enchanter": "20"
      },
      "npc": "false",
      "item": "false"
    },
    "feeble_poison": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "feedback": {
      "classes": {
        "enchanter": "29"
      },
      "npc": "false",
      "item": "true"
    },
    "feet_like_cat": {
      "classes": {
        "ranger": 15,
        "shaman": 5
      },
      "npc": "false",
      "item": "true"
    },
    "fellspine": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "feral_spirit": {
      "classes": {
        "druid": 19
      },
      "npc": "false",
      "item": "false"
    },
    "fetter": {
      "classes": {
        "enchanter": "58",
        "wizard": 58
      },
      "npc": "false",
      "item": "false"
    },
    "fiery_might": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "fire": {
      "classes": {
        "druid": 49
      },
      "npc": "false",
      "item": "false"
    },
    "firefist": {
      "classes": {
        "druid": 9,
        "ranger": 22
      },
      "npc": "false",
      "item": "true"
    },
    "fist_of_water": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "fixation_of_ro": {
      "classes": {
        "druid": 44
      },
      "npc": "false",
      "item": "false"
    },
    "flame_lick": {
      "classes": {
        "druid": 1,
        "ranger": 9
      },
      "npc": "false",
      "item": "false"
    },
    "flash_of_light": {
      "classes": {
        "cleric": 1,
        "paladin": 9,
        "shaman": 1
      },
      "npc": "false",
      "item": "false"
    },
    "fleeting_fury": {
      "classes": {
        "shaman": 5
      },
      "npc": "false",
      "item": "true"
    },
    "flesh_rot_i": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "flesh_rot_ii": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "flesh_rot_iii": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "flurry": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "focus_of_spirit": {
      "classes": {
        "shaman": 60
      },
      "npc": "false",
      "item": "false"
    },
    "forlorn_deeds": {
      "classes": {
        "enchanter": "57"
      },
      "npc": "false",
      "item": "false"
    },
    "form_of_the_great_bear": {
      "classes": {
        "shaman": 55
      },
      "npc": "false",
      "item": "false"
    },
    "form_of_the_great_wolf": {
      "classes": {
        "druid": 44
      },
      "npc": "false",
      "item": "true"
    },
    "form_of_the_howler": {
      "classes": {
        "druid": 54
      },
      "npc": "false",
      "item": "false"
    },
    "form_of_the_hunter": {
      "classes": {
        "druid": 60
      },
      "npc": "false",
      "item": "false"
    },
    "fortitude": {
      "classes": {
        "cleric": 55
      },
      "npc": "false",
      "item": "true"
    },
    "freezing_breath": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "frenzied_strength": {
      "classes": {
        "cleric": 34,
        "paladin": 52
      },
      "npc": "false",
      "item": "false"
    },
    "frenzy": {
      "classes": {
        "shaman": 19
      },
      "npc": "false",
      "item": "false"
    },
    "froglok_poison": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "frost_storm": {
      "classes": {
        "wizard": 44
      },
      "npc": "false",
      "item": "false"
    },
    "frostbite": {
      "classes": {},
      "npc": "false",
      "item": "true"
    },
    "frostreavers_blessing": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "fufils_curtailing_chant": {
      "classes": {
        "bard": "30"
      },
      "npc": "false",
      "item": "false"
    },
    "fungal_regrowth": {
      "classes": {},
      "npc": "false",
      "item": "true"
    },
    "fungus_spores": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "furious_strength": {
      "classes": {
        "shaman": 39
      },
      "npc": "false",
      "item": "true"
    },
    "fury": {
      "classes": {
        "shaman": 34
      },
      "npc": "false",
      "item": "true"
    },
    "garzicors_vengeance": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "gasping_embrace": {
      "classes": {
        "enchanter": "49"
      },
      "npc": "false",
      "item": "true"
    },
    "gaze": {
      "classes": {
        "wizard": 12
      },
      "npc": "false",
      "item": "true"
    },
    "gift_of_brilliance": {
      "classes": {
        "enchanter": "60"
      },
      "npc": "false",
      "item": "false"
    },
    "gift_of_insight": {
      "classes": {
        "enchanter": "55"
      },
      "npc": "false",
      "item": "false"
    },
    "gift_of_magic": {
      "classes": {
        "enchanter": "34"
      },
      "npc": "false",
      "item": "false"
    },
    "gift_of_pure_thought": {
      "classes": {
        "enchanter": "59"
      },
      "npc": "false",
      "item": "false"
    },
    "girdle_of_karana": {
      "classes": {
        "druid": 55
      },
      "npc": "false",
      "item": "false"
    },
    "glamour": {
      "classes": {
        "shaman": 39
      },
      "npc": "false",
      "item": "true"
    },
    "glamour_of_kintaz": {
      "classes": {
        "enchanter": "54"
      },
      "npc": "false",
      "item": "false"
    },
    "glamour_of_tunare": {
      "classes": {
        "druid": 53
      },
      "npc": "false",
      "item": "false"
    },
    "glimpse": {
      "classes": {
        "druid": 4,
        "ranger": 9
      },
      "npc": "false",
      "item": "true"
    },
    "graveyard_dust": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "grease_injection": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "greater_shielding": {
      "classes": {
        "enchanter": "34",
        "magician": 34,
        "necromancer": 34,
        "wizard": 34
      },
      "npc": "false",
      "item": "false"
    },
    "greater_wolf_form": {
      "classes": {
        "druid": 34,
        "ranger": 56
      },
      "npc": "false",
      "item": "true"
    },
    "greenmist": {
      "classes": {},
      "npc": "false",
      "item": "true"
    },
    "grim_aura": {
      "classes": {
        "necromancer": 4,
        "shadow knight": 22
      },
      "npc": "false",
      "item": "true"
    },
    "group_resist_magic": {
      "classes": {
        "enchanter": "49"
      },
      "npc": "false",
      "item": "false"
    },
    "guard": {
      "classes": {
        "cleric": 29,
        "paladin": 39
      },
      "npc": "false",
      "item": "true"
    },
    "guardian": {
      "classes": {
        "shaman": 44
      },
      "npc": "false",
      "item": "false"
    },
    "guardian_rhythms": {
      "classes": {
        "bard": 17
      },
      "npc": "false",
      "item": "false"
    },
    "harmony": {
      "classes": {
        "druid": 5,
        "ranger": 22
      },
      "npc": "false",
      "item": "false"
    },
    "harmshield": {
      "classes": {
        "necromancer": 20
      },
      "npc": "false",
      "item": "true"
    },
    "harpy_voice": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "haste": {
      "classes": {},
      "npc": "false",
      "item": "true"
    },
    "haze": {
      "classes": {
        "enchanter": "4"
      },
      "npc": "false",
      "item": "false"
    },
    "health": {
      "classes": {
        "shaman": 34
      },
      "npc": "false",
      "item": "true"
    },
    "heart_flutter": {
      "classes": {
        "necromancer": 16,
        "shadow knight": 39
      },
      "npc": "false",
      "item": "false"
    },
    "heat_blood": {
      "classes": {
        "necromancer": 12,
        "shadow knight": 30
      },
      "npc": "false",
      "item": "true"
    },
    "heat_sight": {
      "classes": {
        "wizard": 16
      },
      "npc": "false",
      "item": "true"
    },
    "heroic_bond": {
      "classes": {
        "cleric": 52
      },
      "npc": "false",
      "item": "false"
    },
    "heroism": {
      "classes": {
        "cleric": 52
      },
      "npc": "false",
      "item": "false"
    },
    "holy_armor": {
      "classes": {
        "cleric": 5,
        "paladin": 15
      },
      "npc": "false",
      "item": "false"
    },
    "hug": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "hymn_of_restoration": {
      "classes": {
        "bard": 6
      },
      "npc": "false",
      "item": "false"
    },
    "ice": {
      "classes": {
        "druid": 49
      },
      "npc": "false",
      "item": "false"
    },
    "ice_breath": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "ice_strike": {
      "classes": {
        "shaman": 54
      },
      "npc": "false",
      "item": "false"
    },
    "ignite_blood": {
      "classes": {
        "necromancer": 49
      },
      "npc": "false",
      "item": "false"
    },
    "ignite_bones": {
      "classes": {
        "necromancer": 44
      },
      "npc": "false",
      "item": "true"
    },
    "ikatiars_revenge": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "immolate": {
      "classes": {
        "druid": 29,
        "ranger": 49
      },
      "npc": "false",
      "item": "false"
    },
    "immolating_breath": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "impart_strength": {
      "classes": {
        "necromancer": 8
      },
      "npc": "false",
      "item": "false"
    },
    "incapacitate": {
      "classes": {
        "enchanter": "44",
        "shaman": 44
      },
      "npc": "false",
      "item": "true"
    },
    "infectious_cloud": {
      "classes": {
        "necromancer": 16,
        "shaman": 19
      },
      "npc": "false",
      "item": "true"
    },
    "inferno_shield": {
      "classes": {
        "magician": 29
      },
      "npc": "false",
      "item": "true"
    },
    "inner_fire": {
      "classes": {
        "shaman": 1
      },
      "npc": "false",
      "item": "false"
    },
    "insidious_decay": {
      "classes": {
        "shaman": 52
      },
      "npc": "false",
      "item": "false"
    },
    "insidious_fever": {
      "classes": {
        "shaman": 19
      },
      "npc": "false",
      "item": "true"
    },
    "insidious_malady": {
      "classes": {
        "shaman": 39
      },
      "npc": "false",
      "item": "false"
    },
    "insight": {
      "classes": {
        "enchanter": "255"
      },
      "npc": "false",
      "item": "true"
    },
    "insipid_weakness": {
      "classes": {
        "enchanter": "34"
      },
      "npc": "false",
      "item": "true"
    },
    "inspire_fear": {
      "classes": {
        "cleric": 24
      },
      "npc": "false",
      "item": "false"
    },
    "intensify_death": {
      "classes": {
        "necromancer": 24
      },
      "npc": "false",
      "item": "false"
    },
    "invigor": {
      "classes": {
        "cleric": 9,
        "druid": 14,
        "enchanter": "24",
        "paladin": 22,
        "ranger": 30,
        "shaman": 24
      },
      "npc": "false",
      "item": "false"
    },
    "jonthans_inspiration": {
      "classes": {
        "bard": 58
      },
      "npc": "false",
      "item": "false"
    },
    "jonthans_provocation": {
      "classes": {
        "bard": 45
      },
      "npc": "false",
      "item": "false"
    },
    "jonthans_whistling_warsong": {
      "classes": {
        "bard": 7
      },
      "npc": "false",
      "item": "true"
    },
    "kazumis_note_of_preservation": {
      "classes": {
        "bard": 60
      },
      "npc": "false",
      "item": "false"
    },
    "kelins_lucid_lullaby": {
      "classes": {
        "bard": 15
      },
      "npc": "false",
      "item": "false"
    },
    "kelins_lugubrious_lament": {
      "classes": {
        "bard": 8
      },
      "npc": "false",
      "item": "false"
    },
    "kilvas_skin_of_flame": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "kylies_venom": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "languid_pace": {
      "classes": {
        "enchanter": "12"
      },
      "npc": "false",
      "item": "false"
    },
    "largarns_lamentation": {
      "classes": {
        "enchanter": "55"
      },
      "npc": "false",
      "item": "false"
    },
    "largos_absonant_binding": {
      "classes": {
        "bard": 51
      },
      "npc": "false",
      "item": "false"
    },
    "largos_melodic_binding": {
      "classes": {
        "bard": 20
      },
      "npc": "false",
      "item": "false"
    },
    "leach": {
      "classes": {
        "necromancer": 12
      },
      "npc": "false",
      "item": "true"
    },
    "leatherskin": {
      "classes": {
        "necromancer": 24,
        "wizard": 24
      },
      "npc": "false",
      "item": "false"
    },
    "legacy_of_spike": {
      "classes": {
        "druid": 51
      },
      "npc": "false",
      "item": "false"
    },
    "legacy_of_thorn": {
      "classes": {
        "druid": 59
      },
      "npc": "false",
      "item": "false"
    },
    "lesser_shielding": {
      "classes": {
        "enchanter": "8",
        "magician": 8,
        "necromancer": 8,
        "wizard": 8
      },
      "npc": "false",
      "item": "true"
    },
    "levitate": {
      "classes": {
        "druid": 14,
        "enchanter": "16",
        "ranger": 39,
        "shaman": 14,
        "wizard": 24
      },
      "npc": "false",
      "item": "true"
    },
    "levitation": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "lich": {
      "classes": {
        "necromancer": 49
      },
      "npc": "false",
      "item": "false"
    },
    "listless_power": {
      "classes": {
        "enchanter": "29",
        "shaman": 29
      },
      "npc": "false",
      "item": "false"
    },
    "lower_resists_i": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "lower_resists_ii": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "lower_resists_iii": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "lower_resists_iv": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "lull": {
      "classes": {
        "cleric": 1,
        "enchanter": "1",
        "paladin": 15
      },
      "npc": "false",
      "item": "true"
    },
    "lull_animal": {
      "classes": {
        "druid": 1,
        "ranger": 9
      },
      "npc": "false",
      "item": "false"
    },
    "lyssas_solidarity_of_vision": {
      "classes": {
        "bard": 34
      },
      "npc": "false",
      "item": "false"
    },
    "lyssas_veracious_concord": {
      "classes": {
        "bard": 24
      },
      "npc": "false",
      "item": "false"
    },
    "magi_curse": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "magnify": {
      "classes": {
        "wizard": 29
      },
      "npc": "false",
      "item": "false"
    },
    "major_shielding": {
      "classes": {
        "enchanter": "24",
        "magician": 24,
        "necromancer": 24,
        "wizard": 24
      },
      "npc": "false",
      "item": "true"
    },
    "mala": {
      "classes": {
        "magician": 60
      },
      "npc": "false",
      "item": "false"
    },
    "malevolent_grasp": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "malo": {
      "classes": {
        "shaman": 60
      },
      "npc": "false",
      "item": "false"
    },
    "malosi": {
      "classes": {
        "magician": 51,
        "shaman": 49
      },
      "npc": "false",
      "item": "false"
    },
    "malosini": {
      "classes": {
        "magician": 58,
        "shaman": 57
      },
      "npc": "false",
      "item": "false"
    },
    "mana_flare": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "mana_shroud": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "manasink": {
      "classes": {
        "wizard": 58
      },
      "npc": "false",
      "item": "false"
    },
    "manaskin": {
      "classes": {
        "necromancer": 52,
        "wizard": 52
      },
      "npc": "false",
      "item": "false"
    },
    "maniacal_strength": {
      "classes": {
        "shaman": 57
      },
      "npc": "false",
      "item": "false"
    },
    "manticore_poison": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "mark_of_karn": {
      "classes": {
        "cleric": 56
      },
      "npc": "false",
      "item": "true"
    },
    "mask_of_the_hunter": {
      "classes": {
        "druid": 60
      },
      "npc": "false",
      "item": "false"
    },
    "mcvaxius_berserker_crescendo": {
      "classes": {
        "bard": 42
      },
      "npc": "false",
      "item": "false"
    },
    "mcvaxius_rousing_rondo": {
      "classes": {
        "bard": 57
      },
      "npc": "false",
      "item": "false"
    },
    "melody_of_ervaj": {
      "classes": {
        "bard": 50
      },
      "npc": "false",
      "item": "false"
    },
    "mesmerization": {
      "classes": {
        "enchanter": "16"
      },
      "npc": "false",
      "item": "false"
    },
    "mesmerize": {
      "classes": {
        "enchanter": "4"
      },
      "npc": "false",
      "item": "false"
    },
    "mesmerizing_breath": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "mind_cloud": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "minion_of_hate": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "minor_shielding": {
      "classes": {
        "enchanter": "1",
        "magician": 1,
        "necromancer": 1,
        "wizard": 1
      },
      "npc": "false",
      "item": "false"
    },
    "mist": {
      "classes": {
        "enchanter": "12"
      },
      "npc": "false",
      "item": "false"
    },
    "mortal_deftness": {
      "classes": {
        "shaman": 58
      },
      "npc": "false",
      "item": "false"
    },
    "muscle_lock_i": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "muscle_lock_ii": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "muscle_lock_iii": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "muscle_lock_iv": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "mystic_precision": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "naltrons_mark": {
      "classes": {
        "cleric": 58
      },
      "npc": "false",
      "item": "false"
    },
    "natures_melody": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "natureskin": {
      "classes": {
        "druid": 57
      },
      "npc": "false",
      "item": "false"
    },
    "nillipus_march_of_the_wee": {
      "classes": {
        "bard": 52
      },
      "npc": "false",
      "item": "false"
    },
    "nimble": {
      "classes": {
        "shaman": 34
      },
      "npc": "false",
      "item": "true"
    },
    "nivs_harmonic": {
      "classes": {
        "bard": 58
      },
      "npc": "false",
      "item": "false"
    },
    "nivs_melody_of_preservation": {
      "classes": {
        "bard": 47
      },
      "npc": "false",
      "item": "true"
    },
    "null_aura": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "numb_the_dead": {
      "classes": {
        "necromancer": 4,
        "shadow knight": 15
      },
      "npc": "false",
      "item": "false"
    },
    "obscure": {
      "classes": {
        "enchanter": "29"
      },
      "npc": "false",
      "item": "false"
    },
    "obsidian_shatter": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "occlusion_of_sound": {
      "classes": {
        "bard": 55
      },
      "npc": "false",
      "item": "false"
    },
    "okeils_flickering_flame": {
      "classes": {
        "wizard": 34
      },
      "npc": "false",
      "item": "false"
    },
    "okeils_radiation": {
      "classes": {
        "wizard": 4
      },
      "npc": "false",
      "item": "true"
    },
    "one_hundred_blows": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "overwhelming_splendor": {
      "classes": {
        "enchanter": "56"
      },
      "npc": "false",
      "item": "false"
    },
    "pacify": {
      "classes": {
        "cleric": 39,
        "enchanter": "39",
        "paladin": 51
      },
      "npc": "false",
      "item": "true"
    },
    "pack_chloroplast": {
      "classes": {
        "druid": 49
      },
      "npc": "false",
      "item": "false"
    },
    "pack_regeneration": {
      "classes": {
        "druid": 39
      },
      "npc": "false",
      "item": "false"
    },
    "pack_spirit": {
      "classes": {
        "druid": 39
      },
      "npc": "false",
      "item": "false"
    },
    "pact_of_shadow": {
      "classes": {
        "necromancer": 44
      },
      "npc": "false",
      "item": "true"
    },
    "panic": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "panic_animal": {
      "classes": {
        "druid": 1,
        "ranger": 22
      },
      "npc": "false",
      "item": "true"
    },
    "panic_the_dead": {
      "classes": {
        "cleric": 29,
        "necromancer": 29,
        "shadow knight": 54
      },
      "npc": "false",
      "item": "false"
    },
    "paralyzing_poison_i": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "paralyzing_poison_ii": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "paralyzing_poison_iii": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "phantom_armor": {
      "classes": {
        "magician": 52
      },
      "npc": "false",
      "item": "false"
    },
    "phantom_chain": {
      "classes": {
        "magician": 29
      },
      "npc": "false",
      "item": "false"
    },
    "phantom_leather": {
      "classes": {
        "magician": 16
      },
      "npc": "false",
      "item": "false"
    },
    "phantom_plate": {
      "classes": {
        "magician": 44
      },
      "npc": "false",
      "item": "true"
    },
    "plague": {
      "classes": {
        "necromancer": 52,
        "shaman": 49
      },
      "npc": "false",
      "item": "false"
    },
    "plagueratdisease": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "plainsight": {
      "classes": {
        "wizard": 55
      },
      "npc": "false",
      "item": "false"
    },
    "poison": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "poison_bolt": {
      "classes": {
        "necromancer": 4
      },
      "npc": "false",
      "item": "true"
    },
    "poison_breath": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "power": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "pox_of_bertoxxulous": {
      "classes": {
        "shaman": 59
      },
      "npc": "false",
      "item": "false"
    },
    "primal_avatar": {
      "classes": {
        "shaman": 60
      },
      "npc": "false",
      "item": "false"
    },
    "primal_essence": {
      "classes": {},
      "npc": "false",
      "item": "true"
    },
    "prime_healers_blessing": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "protect": {
      "classes": {
        "shaman": 24
      },
      "npc": "false",
      "item": "false"
    },
    "protection_of_the_glades": {
      "classes": {
        "druid": 60
      },
      "npc": "false",
      "item": "false"
    },
    "psalm_of_cooling": {
      "classes": {
        "bard": 33
      },
      "npc": "false",
      "item": "false"
    },
    "psalm_of_mystic_shielding": {
      "classes": {
        "bard": 41
      },
      "npc": "false",
      "item": "false"
    },
    "psalm_of_purity": {
      "classes": {
        "bard": 37
      },
      "npc": "false",
      "item": "false"
    },
    "psalm_of_vitality": {
      "classes": {
        "bard": 29
      },
      "npc": "false",
      "item": "false"
    },
    "psalm_of_warmth": {
      "classes": {
        "bard": 25
      },
      "npc": "false",
      "item": "false"
    },
    "purifying_rhythms": {
      "classes": {
        "bard": 13
      },
      "npc": "false",
      "item": "false"
    },
    "putrefy_flesh": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "putrid_breath": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "pyrocruor": {
      "classes": {
        "necromancer": 58
      },
      "npc": "false",
      "item": "false"
    },
    "quickness": {
      "classes": {
        "enchanter": "16",
        "shaman": 29
      },
      "npc": "false",
      "item": "false"
    },
    "quivering_veil_of_xarn": {
      "classes": {
        "necromancer": 58
      },
      "npc": "false",
      "item": "false"
    },
    "rabies": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "radiant_visage": {
      "classes": {
        "enchanter": "34"
      },
      "npc": "false",
      "item": "false"
    },
    "rage": {
      "classes": {
        "shaman": 49
      },
      "npc": "false",
      "item": "false"
    },
    "rage_of_tallon": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "rage_of_vallon": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "rage_of_zek": {
      "classes": {},
      "npc": "false",
      "item": "true"
    },
    "rampage": {
      "classes": {
        "enchanter": "39"
      },
      "npc": "false",
      "item": "true"
    },
    "rapture": {
      "classes": {
        "enchanter": "59"
      },
      "npc": "false",
      "item": "false"
    },
    "reckless_health": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "reckless_strength": {
      "classes": {
        "cleric": 5,
        "paladin": 22
      },
      "npc": "false",
      "item": "true"
    },
    "regeneration": {
      "classes": {
        "druid": 34,
        "shaman": 24
      },
      "npc": "false",
      "item": "true"
    },
    "regrowth": {
      "classes": {
        "druid": 54,
        "shaman": 52
      },
      "npc": "false",
      "item": "false"
    },
    "regrowth_of_the_grove": {
      "classes": {
        "druid": 58
      },
      "npc": "false",
      "item": "true"
    },
    "rejuvenation": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "repulse_animal": {
      "classes": {
        "druid": 51
      },
      "npc": "false",
      "item": "false"
    },
    "resist_cold": {
      "classes": {
        "cleric": 39,
        "druid": 34,
        "necromancer": 24,
        "ranger": 55,
        "shadow knight": 39,
        "shaman": 24
      },
      "npc": "false",
      "item": "true"
    },
    "resist_disease": {
      "classes": {
        "cleric": 39,
        "druid": 44,
        "necromancer": 34,
        "paladin": 51,
        "shaman": 34
      },
      "npc": "false",
      "item": "false"
    },
    "resist_fire": {
      "classes": {
        "cleric": 34,
        "druid": 24,
        "ranger": 49,
        "shaman": 29
      },
      "npc": "false",
      "item": "false"
    },
    "resist_magic": {
      "classes": {
        "cleric": 44,
        "druid": 49,
        "enchanter": "39",
        "paladin": 55,
        "shaman": 44
      },
      "npc": "false",
      "item": "true"
    },
    "resist_poison": {
      "classes": {
        "cleric": 34,
        "druid": 44,
        "shaman": 39
      },
      "npc": "false",
      "item": "false"
    },
    "resistance_to_magic": {
      "classes": {},
      "npc": "false",
      "item": "true"
    },
    "resistant_skin": {
      "classes": {
        "wizard": 12
      },
      "npc": "false",
      "item": "false"
    },
    "resolution": {
      "classes": {
        "cleric": 44,
        "paladin": 60
      },
      "npc": "false",
      "item": "false"
    },
    "rest_the_dead": {
      "classes": {
        "necromancer": 24,
        "shadow knight": 52
      },
      "npc": "false",
      "item": "false"
    },
    "resurrection_effects": {
      "classes": {},
      "npc": "false",
      "item": "false"
    },
    "riotous_health": {
      "classes": {
        "shaman": 54
      },
      "npc": "false",
      "item": "true"
    },
    "rising_dexterity": {
      "classes": {
        "shaman": 29
      },
      "npc": "false",
      "item": "false"
    },
    "rodricks_gift": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "ros_fiery_sundering": {
      "classes": {
        "druid": 39
      },
      "npc": "false",
      "item": "false"
    },
    "rotting_flesh": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "rubicite_aura": {
      "classes": {},
      "npc": "false",
      "item": "true"
    },
    "rune_i": {
      "classes": {
        "enchanter": "16"
      },
      "npc": "false",
      "item": "false"
    },
    "rune_ii": {
      "classes": {
        "enchanter": "24"
      },
      "npc": "false",
      "item": "false"
    },
    "rune_iii": {
      "classes": {
        "enchanter": "34"
      },
      "npc": "false",
      "item": "true"
    },
    "rune_iv": {
      "classes": {
        "enchanter": "44"
      },
      "npc": "false",
      "item": "true"
    },
    "rune_v": {
      "classes": {
        "enchanter": "52"
      },
      "npc": "false",
      "item": "false"
    },
    "savage_spirit": {
      "classes": {
        "druid": 44
      },
      "npc": "false",
      "item": "false"
    },
    "scale_of_wolf": {
      "classes": {
        "druid": 24,
        "shaman": 24
      },
      "npc": "false",
      "item": "true"
    },
    "scale_skin": {
      "classes": {
        "shaman": 5
      },
      "npc": "false",
      "item": "false"
    },
    "scarab_storm": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "scent_of_darkness": {
      "classes": {
        "necromancer": 39
      },
      "npc": "false",
      "item": "true"
    },
    "scent_of_dusk": {
      "classes": {
        "necromancer": 12
      },
      "npc": "false",
      "item": "false"
    },
    "scent_of_shadow": {
      "classes": {
        "necromancer": 24
      },
      "npc": "false",
      "item": "false"
    },
    "scent_of_terris": {
      "classes": {
        "necromancer": 52
      },
      "npc": "false",
      "item": "false"
    },
    "scorching_skin": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "scourge": {
      "classes": {
        "necromancer": 39,
        "shaman": 34
      },
      "npc": "false",
      "item": "true"
    },
    "screaming_mace": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "screaming_terror": {
      "classes": {
        "necromancer": 24
      },
      "npc": "false",
      "item": "false"
    },
    "sear": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "sebilite_pox": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "see_invisible": {
      "classes": {
        "druid": 14,
        "enchanter": "8",
        "magician": 16,
        "ranger": 39,
        "wizard": 4
      },
      "npc": "false",
      "item": "true"
    },
    "seething_fury": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "selos_accelerando": {
      "classes": {
        "bard": 4
      },
      "npc": "false",
      "item": "false"
    },
    "selos_assonant_strane": {
      "classes": {
        "bard": 54
      },
      "npc": "false",
      "item": "false"
    },
    "selos_chords_of_cessation": {
      "classes": {
        "bard": 48
      },
      "npc": "false",
      "item": "false"
    },
    "selos_consonant_chain": {
      "classes": {
        "bard": 23
      },
      "npc": "false",
      "item": "false"
    },
    "selos_song_of_travel": {
      "classes": {
        "bard": 51
      },
      "npc": "false",
      "item": "true"
    },
    "serpent_sight": {
      "classes": {
        "enchanter": "12",
        "shaman": 9
      },
      "npc": "false",
      "item": "true"
    },
    "shade": {
      "classes": {
        "enchanter": "39"
      },
      "npc": "false",
      "item": "false"
    },
    "shadow": {
      "classes": {
        "enchanter": "49"
      },
      "npc": "false",
      "item": "true"
    },
    "shadow_compact": {
      "classes": {
        "necromancer": 20
      },
      "npc": "false",
      "item": "false"
    },
    "shadow_sight": {
      "classes": {
        "necromancer": 24,
        "shadow knight": 49
      },
      "npc": "false",
      "item": "false"
    },
    "shadow_vortex": {
      "classes": {
        "necromancer": 20,
        "shadow knight": 39
      },
      "npc": "false",
      "item": "true"
    },
    "shadowbond": {
      "classes": {
        "necromancer": 54
      },
      "npc": "false",
      "item": "false"
    },
    "shallow_breath": {
      "classes": {
        "enchanter": "1"
      },
      "npc": "false",
      "item": "true"
    },
    "share_wolf_form": {
      "classes": {
        "druid": 39
      },
      "npc": "false",
      "item": "true"
    },
    "shauris_sonorous_clouding": {
      "classes": {
        "bard": 19
      },
      "npc": "false",
      "item": "false"
    },
    "shield_of_barbs": {
      "classes": {
        "druid": 19
      },
      "npc": "false",
      "item": "false"
    },
    "shield_of_blades": {
      "classes": {
        "druid": 58
      },
      "npc": "false",
      "item": "false"
    },
    "shield_of_brambles": {
      "classes": {
        "druid": 29,
        "ranger": 49
      },
      "npc": "false",
      "item": "true"
    },
    "shield_of_fire": {
      "classes": {
        "magician": 8
      },
      "npc": "false",
      "item": "false"
    },
    "shield_of_flame": {
      "classes": {
        "magician": 20
      },
      "npc": "false",
      "item": "true"
    },
    "shield_of_lava": {
      "classes": {
        "magician": 49
      },
      "npc": "false",
      "item": "true"
    },
    "shield_of_song": {
      "classes": {
        "bard": 49
      },
      "npc": "false",
      "item": "false"
    },
    "shield_of_spikes": {
      "classes": {
        "druid": 39,
        "ranger": 58
      },
      "npc": "false",
      "item": "false"
    },
    "shield_of_the_magi": {
      "classes": {
        "enchanter": "54",
        "magician": 54,
        "necromancer": 54,
        "wizard": 54
      },
      "npc": "false",
      "item": "false"
    },
    "shield_of_thistles": {
      "classes": {
        "druid": 9,
        "ranger": 30
      },
      "npc": "false",
      "item": "true"
    },
    "shield_of_words": {
      "classes": {
        "cleric": 49,
        "paladin": 60
      },
      "npc": "false",
      "item": "true"
    },
    "shielding": {
      "classes": {
        "enchanter": "16",
        "magician": 16,
        "necromancer": 16,
        "wizard": 16
      },
      "npc": "false",
      "item": "false"
    },
    "shieldskin": {
      "classes": {
        "necromancer": 16,
        "shadow knight": 34,
        "wizard": 16
      },
      "npc": "false",
      "item": "true"
    },
    "shifting_shield": {
      "classes": {
        "shaman": 34
      },
      "npc": "false",
      "item": "true"
    },
    "shifting_sight": {
      "classes": {
        "enchanter": "20",
        "wizard": 39
      },
      "npc": "false",
      "item": "false"
    },
    "shiftless_deeds": {
      "classes": {
        "enchanter": "44"
      },
      "npc": "false",
      "item": "true"
    },
    "shroud_of_death": {
      "classes": {
        "shadow knight": 55
      },
      "npc": "false",
      "item": "false"
    },
    "shroud_of_hate": {
      "classes": {
        "shadow knight": 39
      },
      "npc": "false",
      "item": "false"
    },
    "shroud_of_pain": {
      "classes": {
        "shadow knight": 50
      },
      "npc": "false",
      "item": "false"
    },
    "shroud_of_the_spirits": {
      "classes": {
        "shaman": 54
      },
      "npc": "false",
      "item": "false"
    },
    "shroud_of_undeath": {
      "classes": {
        "shadow knight": 55
      },
      "npc": "false",
      "item": "false"
    },
    "sicken": {
      "classes": {
        "shaman": 5
      },
      "npc": "false",
      "item": "true"
    },
    "sight": {
      "classes": {
        "wizard": 20
      },
      "npc": "false",
      "item": "false"
    },
    "sight_graft": {
      "classes": {
        "necromancer": 12
      },
      "npc": "false",
      "item": "false"
    },
    "silver_skin": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "siphon_strength": {
      "classes": {
        "necromancer": 1,
        "shadow knight": 9
      },
      "npc": "false",
      "item": "true"
    },
    "siphon_strength_recourse": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "skin_like_diamond": {
      "classes": {
        "druid": 39,
        "ranger": 54
      },
      "npc": "false",
      "item": "true"
    },
    "skin_like_nature": {
      "classes": {
        "druid": 49,
        "ranger": 59
      },
      "npc": "false",
      "item": "true"
    },
    "skin_like_rock": {
      "classes": {
        "druid": 14,
        "ranger": 22
      },
      "npc": "false",
      "item": "true"
    },
    "skin_like_steel": {
      "classes": {
        "druid": 24,
        "ranger": 39
      },
      "npc": "false",
      "item": "false"
    },
    "skin_like_wood": {
      "classes": {
        "druid": 1,
        "ranger": 9
      },
      "npc": "false",
      "item": "false"
    },
    "skin_of_the_shadow": {
      "classes": {
        "necromancer": 55
      },
      "npc": "false",
      "item": "false"
    },
    "skunkspray": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "slime_mist": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "snare": {
      "classes": {
        "druid": 1,
        "ranger": 9
      },
      "npc": "false",
      "item": "true"
    },
    "solons_bewitching_bravura": {
      "classes": {
        "bard": 39
      },
      "npc": "false",
      "item": "false"
    },
    "solons_charismatic_concord": {
      "classes": {
        "bard": 59
      },
      "npc": "false",
      "item": "false"
    },
    "solons_song_of_the_sirens": {
      "classes": {
        "bard": 27
      },
      "npc": "false",
      "item": "false"
    },
    "song_of_midnight": {
      "classes": {
        "bard": 56
      },
      "npc": "false",
      "item": "false"
    },
    "song_of_the_deep_seas": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "song_of_twilight": {
      "classes": {
        "bard": 53
      },
      "npc": "false",
      "item": "false"
    },
    "soothe": {
      "classes": {
        "cleric": 9,
        "enchanter": "8",
        "paladin": 30
      },
      "npc": "false",
      "item": "true"
    },
    "soul_bond": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "soul_consumption": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "soul_well": {
      "classes": {},
      "npc": "false",
      "item": "true"
    },
    "speed_of_the_shissar": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "spikecoat": {
      "classes": {
        "druid": 39,
        "ranger": 49
      },
      "npc": "false",
      "item": "true"
    },
    "spin_the_bottle": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "spirit_armor": {
      "classes": {
        "cleric": 19,
        "necromancer": 16,
        "paladin": 30
      },
      "npc": "false",
      "item": "true"
    },
    "spirit_of_bear": {
      "classes": {
        "shaman": 9
      },
      "npc": "false",
      "item": "false"
    },
    "spirit_of_cat": {
      "classes": {
        "shaman": 19
      },
      "npc": "false",
      "item": "true"
    },
    "spirit_of_cheetah": {
      "classes": {
        "druid": 24,
        "shaman": 24
      },
      "npc": "false",
      "item": "true"
    },
    "spirit_of_monkey": {
      "classes": {
        "shaman": 24
      },
      "npc": "false",
      "item": "false"
    },
    "spirit_of_oak": {
      "classes": {
        "druid": 59
      },
      "npc": "false",
      "item": "false"
    },
    "spirit_of_ox": {
      "classes": {
        "shaman": 24
      },
      "npc": "false",
      "item": "true"
    },
    "spirit_of_scale": {
      "classes": {
        "druid": 53,
        "shaman": 52
      },
      "npc": "false",
      "item": "false"
    },
    "spirit_of_snake": {
      "classes": {
        "shaman": 14
      },
      "npc": "false",
      "item": "false"
    },
    "spirit_of_wolf": {
      "classes": {
        "druid": 14,
        "ranger": 30,
        "shaman": 9
      },
      "npc": "false",
      "item": "true"
    },
    "spirit_quickening": {
      "classes": {
        "shaman": 50
      },
      "npc": "false",
      "item": "false"
    },
    "spirit_sight": {
      "classes": {
        "shaman": 9
      },
      "npc": "false",
      "item": "false"
    },
    "spirit_strength": {
      "classes": {
        "shaman": 19
      },
      "npc": "false",
      "item": "true"
    },
    "splurt": {
      "classes": {
        "necromancer": 51
      },
      "npc": "false",
      "item": "false"
    },
    "spook_the_dead": {
      "classes": {
        "cleric": 1,
        "necromancer": 12,
        "paladin": 9,
        "shadow knight": 22
      },
      "npc": "false",
      "item": "true"
    },
    "stability": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "stalking_probe": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "stalwart_regeneration": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "stamina": {
      "classes": {
        "shaman": 44
      },
      "npc": "false",
      "item": "false"
    },
    "steal_strength": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "steam_overload": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "steelskin": {
      "classes": {
        "necromancer": 34,
        "shadow knight": 56,
        "wizard": 34
      },
      "npc": "false",
      "item": "true"
    },
    "stinging_swarm": {
      "classes": {
        "druid": 14,
        "ranger": 30
      },
      "npc": "false",
      "item": "true"
    },
    "storm_strength": {
      "classes": {
        "druid": 44,
        "ranger": 53
      },
      "npc": "false",
      "item": "true"
    },
    "stream_of_acid": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "strength": {
      "classes": {
        "shaman": 49
      },
      "npc": "false",
      "item": "false"
    },
    "strength_of_earth": {
      "classes": {
        "druid": 9,
        "ranger": 30
      },
      "npc": "false",
      "item": "true"
    },
    "strength_of_nature": {
      "classes": {
        "ranger": 51
      },
      "npc": "false",
      "item": "false"
    },
    "strength_of_stone": {
      "classes": {
        "druid": 34
      },
      "npc": "false",
      "item": "false"
    },
    "strength_of_the_kunzar": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "strengthen": {
      "classes": {
        "enchanter": "1",
        "shaman": 1
      },
      "npc": "false",
      "item": "true"
    },
    "strengthen_death": {
      "classes": {
        "shadow knight": 29
      },
      "npc": "false",
      "item": "false"
    },
    "strike_of_thunder": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "strong_disease": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "strong_poison": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "suffocate": {
      "classes": {
        "enchanter": "29"
      },
      "npc": "false",
      "item": "true"
    },
    "suffocating_sphere": {
      "classes": {
        "enchanter": "4"
      },
      "npc": "false",
      "item": "false"
    },
    "sunbeam": {
      "classes": {
        "druid": 24
      },
      "npc": "false",
      "item": "true"
    },
    "sunskin": {
      "classes": {
        "cleric": 51
      },
      "npc": "false",
      "item": "false"
    },
    "surge_of_enfeeblement": {
      "classes": {
        "necromancer": 34
      },
      "npc": "false",
      "item": "false"
    },
    "swarm_of_retribution": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "swarming_pain": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "swift_like_the_wind": {
      "classes": {
        "enchanter": "49"
      },
      "npc": "false",
      "item": "true"
    },
    "swift_spirit": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "sympathetic_aura": {
      "classes": {
        "enchanter": "20"
      },
      "npc": "false",
      "item": "false"
    },
    "tagars_insects": {
      "classes": {
        "shaman": 29
      },
      "npc": "false",
      "item": "true"
    },
    "tainted_breath": {
      "classes": {
        "shaman": 9
      },
      "npc": "false",
      "item": "true"
    },
    "talisman_of_altuna": {
      "classes": {
        "shaman": 44
      },
      "npc": "false",
      "item": "false"
    },
    "talisman_of_jasinth": {
      "classes": {
        "shaman": 51
      },
      "npc": "false",
      "item": "false"
    },
    "talisman_of_kragg": {
      "classes": {
        "shaman": 55
      },
      "npc": "false",
      "item": "false"
    },
    "talisman_of_shadoo": {
      "classes": {
        "shaman": 53
      },
      "npc": "false",
      "item": "false"
    },
    "talisman_of_the_brute": {
      "classes": {
        "shaman": 57
      },
      "npc": "false",
      "item": "false"
    },
    "talisman_of_the_cat": {
      "classes": {
        "shaman": 57
      },
      "npc": "false",
      "item": "false"
    },
    "talisman_of_the_raptor": {
      "classes": {
        "shaman": 59
      },
      "npc": "false",
      "item": "false"
    },
    "talisman_of_the_rhino": {
      "classes": {
        "shaman": 58
      },
      "npc": "false",
      "item": "false"
    },
    "talisman_of_the_serpent": {
      "classes": {
        "shaman": 58
      },
      "npc": "false",
      "item": "false"
    },
    "talisman_of_tnarg": {
      "classes": {
        "shaman": 34
      },
      "npc": "false",
      "item": "false"
    },
    "tarews_aquatic_ayre": {
      "classes": {
        "bard": 16
      },
      "npc": "false",
      "item": "false"
    },
    "tashan": {
      "classes": {
        "enchanter": "4"
      },
      "npc": "false",
      "item": "true"
    },
    "tashani": {
      "classes": {
        "enchanter": "20"
      },
      "npc": "false",
      "item": "true"
    },
    "tashania": {
      "classes": {
        "enchanter": "44"
      },
      "npc": "false",
      "item": "true"
    },
    "tashanian": {
      "classes": {
        "enchanter": "255"
      },
      "npc": "false",
      "item": "false"
    },
    "telescope": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "tepid_deeds": {
      "classes": {
        "enchanter": "24"
      },
      "npc": "false",
      "item": "true"
    },
    "terrorize_animal": {
      "classes": {
        "druid": 19
      },
      "npc": "false",
      "item": "false"
    },
    "the_unspoken_word": {
      "classes": {
        "cleric": 59
      },
      "npc": "false",
      "item": "false"
    },
    "thistlecoat": {
      "classes": {
        "druid": 9,
        "ranger": 15
      },
      "npc": "false",
      "item": "false"
    },
    "thorncoat": {
      "classes": {
        "druid": 49,
        "ranger": 60
      },
      "npc": "false",
      "item": "false"
    },
    "thorny_shield": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "thrall_of_bones": {
      "classes": {
        "necromancer": 54
      },
      "npc": "false",
      "item": "false"
    },
    "thunder_blast": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "tigirs_insects": {
      "classes": {
        "shaman": 58
      },
      "npc": "false",
      "item": "false"
    },
    "torment": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "torment_of_argli": {
      "classes": {
        "enchanter": "56"
      },
      "npc": "false",
      "item": "false"
    },
    "torment_of_shadows": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "torpor": {
      "classes": {
        "shaman": 60
      },
      "npc": "false",
      "item": "false"
    },
    "track_corpse": {
      "classes": {
        "necromancer": 20
      },
      "npc": "false",
      "item": "false"
    },
    "travelerboots": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "treeform": {
      "classes": {
        "druid": 9
      },
      "npc": "false",
      "item": "true"
    },
    "trepidation": {
      "classes": {
        "cleric": 57,
        "enchanter": "56",
        "necromancer": 56
      },
      "npc": "false",
      "item": "false"
    },
    "tumultuous_strength": {
      "classes": {
        "shaman": 39
      },
      "npc": "false",
      "item": "false"
    },
    "tunares_request": {
      "classes": {
        "druid": 55
      },
      "npc": "false",
      "item": "false"
    },
    "turgurs_insects": {
      "classes": {
        "shaman": 51
      },
      "npc": "false",
      "item": "false"
    },
    "turning_of_the_unnatural": {
      "classes": {
        "cleric": 255
      },
      "npc": "false",
      "item": "false"
    },
    "tuyens_chant_of_flame": {
      "classes": {
        "bard": 38
      },
      "npc": "false",
      "item": "false"
    },
    "tuyens_chant_of_frost": {
      "classes": {
        "bard": 46
      },
      "npc": "false",
      "item": "false"
    },
    "ultravision": {
      "classes": {
        "enchanter": "29",
        "shaman": 29
      },
      "npc": "false",
      "item": "true"
    },
    "umbra": {
      "classes": {
        "enchanter": "57"
      },
      "npc": "false",
      "item": "false"
    },
    "unfailing_reverence": {
      "classes": {
        "shaman": 59
      },
      "npc": "false",
      "item": "false"
    },
    "valiant_companion": {
      "classes": {
        "magician": 59
      },
      "npc": "false",
      "item": "false"
    },
    "valor": {
      "classes": {
        "cleric": 34,
        "paladin": 49
      },
      "npc": "false",
      "item": "true"
    },
    "vampire_charm": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "velocity": {
      "classes": {
        "magician": 58
      },
      "npc": "false",
      "item": "false"
    },
    "vengeance_of_the_glades": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "venom_of_the_snake": {
      "classes": {
        "necromancer": 34,
        "shaman": 39
      },
      "npc": "false",
      "item": "false"
    },
    "vexing_mordinia": {
      "classes": {
        "necromancer": 57
      },
      "npc": "false",
      "item": "false"
    },
    "vigor": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "vision": {
      "classes": {
        "shaman": 19
      },
      "npc": "false",
      "item": "false"
    },
    "visions_of_grandeur": {
      "classes": {
        "enchanter": "60"
      },
      "npc": "false",
      "item": "false"
    },
    "voice_graft": {
      "classes": {
        "necromancer": 16
      },
      "npc": "false",
      "item": "true"
    },
    "voice_of_the_berserker": {
      "classes": {
        "shaman": 59
      },
      "npc": "false",
      "item": "false"
    },
    "wake_of_tranquility": {
      "classes": {
        "cleric": 55,
        "enchanter": "51"
      },
      "npc": "false",
      "item": "false"
    },
    "walking_sleep": {
      "classes": {
        "shaman": 14
      },
      "npc": "false",
      "item": "true"
    },
    "wandering_mind": {
      "classes": {
        "enchanter": "39"
      },
      "npc": "false",
      "item": "false"
    },
    "wave_of_enfeeblement": {
      "classes": {
        "necromancer": 12,
        "shadow knight": 30
      },
      "npc": "false",
      "item": "false"
    },
    "wave_of_fear": {
      "classes": {
        "cleric": 24
      },
      "npc": "false",
      "item": "false"
    },
    "wave_of_heat": {
      "classes": {},
      "npc": "true",
      "item": "false"
    },
    "waves_of_the_deep_sea": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "weak_poison": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "weaken": {
      "classes": {
        "enchanter": "1"
      },
      "npc": "false",
      "item": "true"
    },
    "weakness": {
      "classes": {
        "enchanter": "44"
      },
      "npc": "false",
      "item": "false"
    },
    "whirl_till_you_hurl": {
      "classes": {
        "enchanter": "12"
      },
      "npc": "false",
      "item": "false"
    },
    "whirlwind": {
      "classes": {},
      "npc": "true",
      "item": "true"
    },
    "wind_of_tishani": {
      "classes": {
        "enchanter": "55"
      },
      "npc": "false",
      "item": "false"
    },
    "wind_of_tishanian": {
      "classes": {
        "enchanter": "60"
      },
      "npc": "false",
      "item": "false"
    },
    "winged_death": {
      "classes": {
        "druid": 53
      },
      "npc": "false",
      "item": "false"
    },
    "wolf_form": {
      "classes": {
        "druid": 24,
        "ranger": 49
      },
      "npc": "false",
      "item": "false"
    },
    "wonderous_rapidity": {
      "classes": {
        "enchanter": "58"
      },
      "npc": "false",
      "item": "false"
    },
    "wrath_of_nature": {
      "classes": {},
      "npc": "false",
      "item": "true"
    },
    "yaulp": {
      "classes": {
        "cleric": 1,
        "paladin": 9
      },
      "npc": "false",
      "item": "true"
    },
    "yaulp_ii": {
      "classes": {
        "cleric": 19,
        "paladin": 39
      },
      "npc": "false",
      "item": "true"
    },
    "yaulp_iii": {
      "classes": {
        "cleric": 44,
        "paladin": 56
      },
      "npc": "false",
      "item": "true"
    },
    "yaulp_iv": {
      "classes": {
        "cleric": 53,
        "paladin": 60
      },
      "npc": "false",
      "item": "true"
    }
  },
  "version": "%s"
}
"""

    try:
        spell_casters_path = data_path + "spell-casters.json"
        generate = True

        if os.path.isfile(spell_casters_path):
            json_data = open(spell_casters_path, "r", encoding="utf-8")
            spell_casters = json.load(json_data)
            json_data.close()

            if spell_casters["version"] == version:
                generate = False

        if generate:
            print("    - generating spell-casters.json")
            f = open(spell_casters_path, "w", encoding="utf-8")
            f.write(new_spell_caster_data % (version))
            f.close()

    except Exception as e:
        eqa_settings.log(
            "update spell casters: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def update_spell_lines(data_path, version):
    """Update data/spell-lines.json"""

    new_spell_lines_data = """
{
  "spell_lines": {
    "spell_line_potion_you_on": {
      "accuracy": {},
      "adroitness": {},
      "aura_of_antibody": {},
      "aura_of_cold": {},
      "aura_of_heat": {},
      "aura_of_purity": {},
      "cohesion": {},
      "null_aura": {},
      "power": {},
      "stability": {},
      "vigor": {}
    },
    "spell_line_dot_disease_you_on": {
      "affliction": {},
      "plague": {},
      "scourge": {},
      "sebilite_pox": {},
      "sicken": {}
    },
    "spell_line_haste_you_on": {
      "alacrity": {},
      "celerity": {},
      "quickness": {},
      "swift_like_the_wind": {}
    },
    "spell_line_nec_regen_you_on": {
      "arch_lich": {},
      "call_of_bones": {},
      "demi_lich": {},
      "lich": {}
    },
    "spell_line_int_caster_shield_you_on": {
      "arch_shielding": {},
      "greater_shielding": {},
      "lesser_shielding": {},
      "major_shielding": {},
      "minor_shielding": {},
      "shield_of_the_magi": {},
      "shielding": {}
    },
    "spell_line_holy_armor_you_on": {
      "armor_of_faith": {},
      "guard": {},
      "holy_armor": {},
      "shield_of_words": {}
    },
    "spell_line_protection_you_on": {
      "armor_of_protection": {}
    },
    "spell_line_dot_enc_you_on": {
      "asphyxiate": {},
      "choke": {},
      "gasping_embrace": {},
      "shallow_breath": {},
      "suffocate": {}
    },
    "spell_line_haste_stats_you_on": {
      "augment": {},
      "augmentation": {},
      "inner_fire": {}
    },
    "spell_line_regen_you_on": {
      "aura_of_battle": {},
      "chloroplast": {},
      "extended_regeneration": {},
      "pack_chloroplast": {},
      "pack_regeneration": {},
      "regeneration": {},
      "regrowth": {},
      "regrowth_of_the_grove": {}
    },
    "spell_line_spin_you_on": {
      "bellowing_winds": {},
      "dyns_dizzying_draught": {},
      "rodricks_gift": {},
      "spin_the_bottle": {},
      "whirl_till_you_hurl": {}
    },
    "spell_line_berserker_madness_you_on": {
      "berserker_madness_i": {},
      "berserker_madness_ii": {},
      "berserker_madness_iii": {},
      "berserker_madness_iv": {}
    },
    "spell_line_npc_item_haste_you_on": {
      "blessing_of_the_grove": {},
      "haste": {},
      "swift_spirit": {}
    },
    "spell_line_blind_you_on": {
      "blinding_luminance": {},
      "flash_of_light": {}
    },
    "spell_line_high_mag_ds_you_on": {
      "boon_of_immolation": {},
      "shield_of_lava": {}
    },
    "spell_line_dru_fire_you_on": {
      "breath_of_ro": {},
      "ros_fiery_sundering": {}
    },
    "spell_line_pacify_you_on": {
      "calm": {},
      "calm_animal": {},
      "pacify": {},
      "soothe": {},
      "wake_of_tranquility": {}
    },
    "spell_line_nec_snare_you_on": {
      "cascading_darkness": {},
      "dooming_darkness": {},
      "engulfing_darkness": {}
    },
    "spell_line_raid_silence_you_on": {
      "cloud_of_silence": {},
      "mesmerizing_breath": {}
    },
    "spell_line_swarms_you_on": {
      "creeping_crud": {},
      "drifting_death": {},
      "drones_of_doom": {},
      "stinging_swarm": {}
    },
    "spell_line_mez_you_on": {
      "dazzle": {},
      "mesmerization": {},
      "mesmerize": {}
    },
    "spell_line_poison_you_on": {
      "deadly_poison": {},
      "envenomed_bolt": {},
      "envenomed_breath": {},
      "feeble_poison": {},
      "froglok_poison": {},
      "ikatiars_revenge": {},
      "manticore_poison": {},
      "poison": {},
      "poison_bolt": {},
      "strong_poison": {},
      "tainted_breath": {},
      "venom_of_the_snake": {},
      "weak_poison": {}
    },
    "spell_line_dexterity_you_on": {
      "deftness": {},
      "dexterity": {},
      "dexterous_aura": {},
      "rising_dexterity": {}
    },
    "spell_line_npc_disease_you_on": {
      "disease": {},
      "plagueratdisease": {},
      "rabies": {},
      "strong_disease": {}
    },
    "spell_line_debuff_you_on": {
      "disempower": {},
      "incapacitate": {},
      "listless_power": {}
    },
    "spell_line_dizzy_you_on": {
      "dizzy_ii": {},
      "dizzy_iii": {}
    },
    "spell_line_slow_you_on": {
      "drowsy": {},
      "tagars_insects": {},
      "tigirs_insects": {},
      "turgurs_insects": {},
      "walking_sleep": {}
    },
    "spell_line_strength_debuff_you_on": {
      "ebbing_strength": {},
      "weaken": {}
    },
    "spell_line_int_resists_you_on": {
      "elemental_armor": {},
      "elemental_shield": {}
    },
    "spell_line_cold_resist_you_on": {
      "endure_cold": {}
    },
    "spell_line_disease_resist_you_on": {
      "endure_disease": {}
    },
    "spell_line_fire_resist_you_on": {
      "endure_fire": {}
    },
    "spell_line_magic_resist_you_on": {
      "endure_magic": {},
      "group_resist_magic": {}
    },
    "spell_line_poison_resist_you_on": {
      "endure_poison": {}
    },
    "spell_line_enduring_breath_you_on": {
      "enduring_breath": {},
      "everlasting_breath": {}
    },
    "spell_line_snare_you_on": {
      "ensnare": {},
      "snare": {}
    },
    "spell_line_leach_you_on": {
      "feast_of_blood": {},
      "soul_bond": {},
      "soul_consumption": {},
      "soul_well": {}
    },
    "spell_line_enc_debuff_you_on": {
      "feckless_might": {},
      "insipid_weakness": {},
      "weakness": {}
    },
    "spell_line_enc_slow_you_on": {
      "forlorn_deeds": {},
      "languid_pace": {},
      "rejuvenation_pace": {},
      "shiftless_deeds": {},
      "tepid_deeds": {}
    },
    "spell_line_wolf_form_you_on": {
      "form_of_the_great_wolf": {},
      "form_of_the_howler": {},
      "form_of_the_hunter": {},
      "greater_wolf_form": {},
      "share_wolf_form": {},
      "wolf_form": {}
    },
    "spell_line_berserk_you_on": {
      "frenzy": {},
      "fury": {}
    },
    "spell_line_strength_you_on": {
      "furious_strength": {},
      "impart_strength": {},
      "spirit_strength": {},
      "storm_strength": {},
      "strength_of_earth": {},
      "strength_of_stone": {},
      "strength_of_the_kunzar": {},
      "strengthen": {},
      "tumultuous_strength": {}
    },
    "spell_line_heroic_valor_you_on": {
      "heroic_bond": {},
      "heroism": {}
    },
    "spell_line_charisma_you_on": {
      "charisma": {},
      "glamour": {}
    },
    "spell_line_low_mag_ds_you_on": {
      "inferno_shield": {},
      "shield_of_flame": {}
    },
    "spell_line_shm_insidious_you_on": {
      "insidious_decay": {},
      "insidious_fever": {},
      "insidious_malady": {}
    },
    "spell_line_dru_ds_you_on": {
      "legacy_of_spike": {},
      "legacy_of_thorn": {},
      "shield_of_barbs": {},
      "shield_of_brambles": {},
      "shield_of_spikes": {},
      "shield_of_thistles": {},
      "thorny_shield": {}
    },
    "spell_line_wiz_ds_you_on": {
      "okeils_flickering_flame": {},
      "okeils_radiation": {}
    },
    "spell_line_paralyzing_poison_you_on": {
      "paralyzing_poison_i": {},
      "paralyzing_poison_ii": {},
      "paralyzing_poison_iii": {}
    },
    "spell_line_npc_sick_you_on": {
      "putrid_breath": {},
      "rodricks_gift": {}
    },
    "spell_line_fragile_sow_you_on": {
      "scale_of_wolf": {},
      "spirit_of_scale": {}
    },
    "pell_line_siphon_strength_you_on": {
      "siphon_strength": {},
      "surge_of_enfeeblement": {},
      "wave_of_enfeeblement": {}
    },
    "spell_line_siphon_strength_you_on": {
      "siphon_strength_recourse": {},
      "steal_strength": {}
    },
    "spell_line_dru_tree_you_on": {
      "spirit_of_oak": {},
      "treeform": {}
    },
    "spell_line_shm_hp_you_on": {
      "talisman_of_altuna": {},
      "talisman_of_kragg": {},
      "talisman_of_tnarg": {}
    },
    "spell_line_low_tash_you_on": {
      "tashani": {},
      "wind_of_tishani": {}
    },
    "spell_line_tash_you_on": {
      "tashanian": {},
      "wind_of_tishanian": {}
    },
    "spell_line_malo_you_on": {
      "mala": {},
      "malo": {},
      "malosi": {},
      "malosini": {}
    },
    "spell_line_see_invis_you_on": {
      "acumen": {},
      "chill_sight": {},
      "heat_sight": {},
      "plainsight": {},
      "see_invisible": {},
      "serpent_sight": {},
      "spirit_sight": {},
      "ultravision": {}
    },
    "spell_line_blinding_poison_you_on": {
      "blinding_poison_i": {},
      "blinding_poison_iii": {}
    },
    "spell_line_mind_clears_you_on": {
      "brilliance": {}
    },
    "spell_line_brittle_haste_you_on": {
      "brittle_haste_ii": {},
      "brittle_haste_iii": {},
      "brittle_haste_iv": {}
    },
    "spell_line_infravision_you_on": {
      "deadeye": {},
      "eyes_of_the_cat": {}
    },
    "spell_line_dru_root_you_on": {
      "engulfing_roots": {},
      "ensnaring_roots": {},
      "entrapping_roots": {},
      "enveloping_roots": {},
      "grasping_roots": {}
    },
    "spell_line_root_you_on": {
      "enstill": {},
      "fetter": {},
      "immobilize": {},
      "paralyzing_earth": {},
      "root": {},
      "vengeance_of_the_glades": {}
    },
    "spell_line_flesh_rot_you_on": {
      "flesh_rot_i": {},
      "flesh_rot_ii": {},
      "flesh_rot_iii": {},
      "rotting_flesh": {}
    },
    "spell_line_enc_mana_buff_you_on": {
      "gift_of_brilliance": {},
      "gift_of_insight": {},
      "gift_of_magic": {}
    },
    "spell_line_magnify_you_on": {
      "glimpse": {},
      "magnify": {},
      "sight": {}
    },
    "spell_line_enc_ac_you_on": {
      "haze": {},
      "mist": {}
    },
    "spell_line_nec_fire_you_on": {
      "ignite_blood": {},
      "pyrocruor": {}
    },
    "spell_line_potion_ds_you_on": {
      "kilvas_skin_of_flame": {},
      "scorching_skin": {}
    },
    "spell_line_lower_resists_you_on": {
      "lower_resists_ii": {},
      "lower_resists_iii": {},
      "lower_resists_iv": {}
    },
    "spell_line_dru_best_hp_you_on": {
      "natureskin": {},
      "protection_of_the_glades": {}
    },
    "spell_line_clarity_you_on": {
      "boon_of_the_clear_mind": {},
      "clarity": {}
    },
    "spell_line_clarity_ii_you_on": {
      "clarity_ii": {},
      "gift_of_pure_thought": {}
    },
    "spell_line_rune_you_on": {
      "rune_iv": {},
      "rune_v": {}
    },
    "spell_line_potion_other_on": {
      "accuracy": {},
      "adroitness": {},
      "aura_of_antibody": {},
      "aura_of_cold": {},
      "aura_of_heat": {},
      "aura_of_purity": {},
      "cohesion": {},
      "null_aura": {},
      "power": {},
      "stability": {},
      "vigor": {}
    },
    "spell_line_see_invis_other_on": {
      "acumen": {},
      "spirit_sight": {}
    },
    "spell_line_dot_disease_other_on": {
      "affliction": {},
      "insidious_decay": {},
      "insidious_fever": {},
      "insidious_malady": {},
      "plague": {},
      "scourge": {},
      "sebilite_pox": {},
      "sicken": {}
    },
    "spell_line_haste_other_on": {
      "blessing_of_the_grove": {},
      "brittle_haste_ii": {},
      "brittle_haste_iii": {},
      "brittle_haste_iv": {},
      "haste": {},
      "swift_spirit": {}
    },
    "spell_line_low_nec_mana_regen_other_on": {
      "allure_of_death": {},
      "dark_pact": {}
    },
    "spell_line_nec_regen_other_on": {
      "arch_lich": {},
      "call_of_bones": {},
      "demi_lich": {},
      "lich": {}
    },
    "spell_line_holy_armor_other_on": {
      "armor_of_faith": {},
      "guard": {},
      "holy_armor": {},
      "shield_of_words": {}
    },
    "spell_line_dot_enc_other_on": {
      "asphyxiate": {},
      "choke": {},
      "gasping_embrace": {},
      "shallow_breath": {},
      "suffocate": {}
    },
    "spell_line_target_vision_other_on": {
      "assiduous": {},
      "sight_graft": {},
      "vision": {}
    },
    "spell_dot_nec_heart_other_on": {
      "asystole": {},
      "heart_flutter": {}
    },
    "spell_line_nec_haste_other_on": {
      "augment_death": {},
      "augmentation_of_death": {},
      "intensify_death": {},
      "strengthen_death": {}
    },
    "spell_line_regen_other_on": {
      "aura_of_battle": {},
      "chloroplast": {},
      "extended_regeneration": {},
      "pack_chloroplast": {},
      "pack_regeneration": {},
      "regeneration": {},
      "regrowth": {},
      "regrowth_of_the_grove": {}
    },
    "spell_line_mag_ds_other_on": {
      "inferno_shield": {},
      "shield_of_flame": {},
      "shield_of_lava": {},
      "wave_of_flame": {}
    },
    "spell_line_spin_other_on": {
      "bellowing_winds": {},
      "dyns_dizzying_draught": {},
      "rodricks_gift": {},
      "spin_the_bottle": {},
      "whirl_till_you_hurl": {}
    },
    "spell_line_berserker_madness_other_on": {
      "berserker_madness_i": {},
      "berserker_madness_ii": {},
      "berserker_madness_iii": {},
      "berserker_madness_iv": {},
      "berserker_spirit": {}
    },
    "spell_line_blind_other_on": {
      "blinding_luminance": {},
      "flash_of_light": {}
    },
    "spell_line_blinding_poison_other_on": {
      "blinding_poison_i": {},
      "blinding_poison_iii": {}
    },
    "spell_line_clarity_other_on": {
      "boon_of_the_clear_mind": {},
      "clarity": {}
    },
    "spell_line_dru_fire_other_on": {
      "breath_of_ro": {},
      "ros_fiery_sundering": {}
    },
    "spell_line_berserk_other_on": {
      "burnout": {},
      "burnout_ii": {},
      "burnout_iii": {},
      "burnout_iv": {},
      "frenzy": {},
      "fury": {},
      "voice_of_the_berserker": {}
    },
    "spell_line_scarab_other_on": {
      "burrowing_scarab": {},
      "scarab_storm": {}
    },
    "spell_line_strength_other_on": {
      "burst_of_strength": {},
      "furious_strength": {},
      "girdle_of_karana": {},
      "impart_strength": {},
      "spirit_strength": {},
      "storm_strength": {},
      "strength_of_earth": {},
      "strength_of_stone": {},
      "strength_of_the_kunzar": {},
      "strengthen": {},
      "tumultuous_strength": {}
    },
    "spell_line_pacify_other_on": {
      "calm": {},
      "calm_animal": {},
      "lull": {},
      "pacify": {},
      "soothe": {},
      "wake_of_tranquility": {}
    },
    "spell_line_nec_snare_other_on": {
      "cascading_darkness": {},
      "dooming_darkness": {},
      "engulfing_darkness": {}
    },
    "spell_line_charisma_other_on": {
      "charisma": {},
      "glamour": {},
      "talisman_of_the_serpent": {}
    },
    "spell_line_ultravision_other_on": {
      "chill_sight": {},
      "plainsight": {},
      "shadow_sight": {},
      "ultravision": {}
    },
    "spell_line_clarity_ii_other_on": {
      "clarity_ii": {},
      "gift_of_pure_thought": {}
    },
    "spell_line_raid_silence_other_on": {
      "cloud_of_silence": {},
      "mesmerizing_breath": {}
    },
    "spell_line_swarm_other_on": {
      "creeping_crud": {},
      "drifting_death": {},
      "drones_of_doom": {},
      "stinging_swarm": {}
    },
    "spell_line_infravision_other_on": {
      "deadeye": {},
      "heat_sight": {},
      "serpent_sight": {}
    },
    "spell_line_poison_other_on": {
      "deadly_poison": {},
      "dizzy_i": {},
      "dizzy_ii": {},
      "dizzy_iii": {},
      "dizzy_iv": {},
      "envenomed_bolt": {},
      "feeble_mind_i": {},
      "feeble_mind_ii": {},
      "feeble_mind_iii": {},
      "feeble_mind_iv": {},
      "feeble_poison": {},
      "froglok_poison": {},
      "ikatiars_revenge": {},
      "lower_resists_i": {},
      "lower_resists_ii": {},
      "lower_resists_iii": {},
      "lower_resists_iv": {},
      "manticore_poison": {},
      "poison": {},
      "poison_bolt": {},
      "strong_poison": {},
      "system_shock_i": {},
      "system_shock_ii": {},
      "system_shock_iii": {},
      "system_shock_iv": {},
      "system_shock_v": {},
      "tainted_breath": {},
      "venom_of_the_snake": {},
      "weak_poison": {}
    },
    "spell_line_dexterity_other_on": {
      "deftness": {},
      "dexterity": {},
      "rising_dexterity": {},
      "talisman_of_the_raptor": {}
    },
    "spell_line_npc_disease_other_on": {
      "disease": {},
      "plagueratdisease": {},
      "rabies": {},
      "strong_disease": {}
    },
    "spell_line_debuff_other_on": {
      "disempower": {},
      "incapacitate": {},
      "listless_power": {}
    },
    "spell_line_slow_other_on": {
      "drowsy": {},
      "tagars_insects": {},
      "tigirs_insects": {},
      "turgurs_insects": {},
      "walking_sleep": {}
    },
    "spell_line_hungry_earth_other_on": {
      "hungry_earth": {},
      "earthelementalattack": {}
    },
    "spell_line_strength_debuff_other_on": {
      "ebbing_strength": {},
      "siphon_strength": {},
      "surge_of_enfeeblement": {},
      "wave_of_enfeeblement": {},
      "weaken": {}
    },
    "spell_line_int_resists_other_on": {
      "elemental_armor": {},
      "elemental_shield": {}
    },
    "spell_line_enduring_breath_other_on": {
      "enduring_breath": {},
      "everlasting_breath": {}
    },
    "spell_line_dru_root_other_on": {
      "engulfing_roots": {},
      "ensnaring_roots": {},
      "entrapping_roots": {},
      "enveloping_roots": {},
      "grasping_roots": {}
    },
    "spell_line_snare_other_on": {
      "ensnare": {},
      "snare": {}
    },
    "spell_line_root_other_on": {
      "enstill": {},
      "fetter": {},
      "immobilize": {},
      "paralyzing_earth": {},
      "root": {}
    },
    "spell_line_mag_sow_other_on": {
      "expedience": {},
      "velocity": {}
    },
    "spell_line_enc_debuff_other_on": {
      "feckless_might": {},
      "insipid_weakness": {},
      "weakness": {}
    },
    "spell_line_pet_haste_or_rabies_other_on": {
      "feral_spirit": {},
      "rabies": {},
      "spirit_quickening": {}
    },
    "spell_line_flesh_rot_other_on": {
      "flesh_rot_i": {},
      "flesh_rot_ii": {},
      "flesh_rot_iii": {}
    },
    "spell_line_enc_slow_other_on": {
      "forlorn_deeds": {},
      "languid_pace": {},
      "rejuvenation": {},
      "shiftless_deeds": {},
      "tepid_deeds": {}
    },
    "spell_line_wolf_form_other_on": {
      "form_of_the_great_wolf": {},
      "form_of_the_howler": {},
      "form_of_the_hunter": {},
      "greater_wolf_form": {},
      "share_wolf_form": {},
      "wolf_form": {}
    },
    "spell_line_shm_poison_other_on": {
      "gale_of_poison": {},
      "poison_storm": {},
      "sear": {}
    },
    "spell_line_enc_mana_buff_other_on": {
      "gift_of_brilliance": {},
      "gift_of_insight": {},
      "gift_of_magic": {}
    },
    "spell_line_npc_root_other_on": {
      "gelatroot": {},
      "ghoul_root": {}
    },
    "spell_line_magnify_other_on": {
      "glimpse": {},
      "magnify": {},
      "sight": {}
    },
    "spell_line_magic_resist_other_on": {
      "group_resist_magic": {},
      "resist_magic": {},
      "resistance_to_magic": {}
    },
    "spell_line_enc_ac_other_on": {
      "haze": {},
      "mist": {}
    },
    "spell_line_heroic_valor_other_on": {
      "heroic_bond": {},
      "heroism": {}
    },
    "spell_line_nec_fire_other_on": {
      "ignite_blood": {},
      "pyrocruor": {}
    },
    "spell_line_potion_ds_other_on": {
      "kilvas_skin_of_flame": {},
      "scorching_skin": {}
    },
    "spell_line_dru_ds_other_on": {
      "legacy_of_spike": {},
      "legacy_of_thorn": {},
      "shield_of_barbs": {},
      "shield_of_brambles": {},
      "shield_of_spikes": {},
      "shield_of_thistles": {},
      "thorny_shield": {}
    },
    "spell_line_malo_other_on": {
      "mala": {},
      "malo": {},
      "malosi": {},
      "malosini": {}
    },
    "spell_line_dru_best_hp_other_on": {
      "natureskin": {},
      "protection_of_the_glades": {}
    },
    "spell_line_pacify_undead_other_on": {
      "numb_the_dead": {},
      "rest_the_dead": {}
    },
    "spell_line_wiz_ds_other_on": {
      "okeils_flickering_flame": {},
      "okeils_radiation": {}
    },
    "spell_line_nec_heal_other_on": {
      "pact_of_shadow": {},
      "shadow_compact": {},
      "shadowbond": {}
    },
    "spell_line_paralyzing_poison_other_on": {
      "paralyzing_poison_i": {},
      "paralyzing_poison_ii": {},
      "paralyzing_poison_iii": {}
    },
    "spell_line_rune_other_on": {
      "rune_i": {},
      "rune_ii": {},
      "rune_iii": {},
      "rune_iv": {},
      "rune_v": {}
    },
    "spell_line_fragile_sow_other_on": {
      "scale_of_wolf": {},
      "spirit_of_scale": {}
    },
    "spell_line_nec_scent_other_on": {
      "scent_of_darkness": {},
      "scent_of_terris": {}
    },
    "spell_line_yaulp_other_on": {
      "screaming_mace": {},
      "yaulp": {},
      "yaulp_ii": {},
      "yaulp_iii": {},
      "yaulp_iv": {}
    },
    "spell_line_siphon_strength_other_on": {
      "siphon_strength_recourse": {},
      "steal_strength": {}
    },
    "spell_line_cat_other_on": {
      "spirit_of_cat": {},
      "spirit_of_cheetah": {}
    },
    "spell_line_dru_tree_other_on": {
      "spirit_of_oak": {},
      "treeform": {}
    },
    "spell_line_shm_sta_other_on": {
      "stamina": {},
      "talisman_of_the_brute": {}
    },
    "spell_line_shm_str_other_on": {
      "strength": {},
      "talisman_of_the_rhino": {}
    },
    "spell_line_shm_hp_other_on": {
      "talisman_of_altuna": {},
      "talisman_of_kragg": {},
      "talisman_of_tnarg": {}
    },
    "spell_line_tash_other_on": {
      "tashan": {},
      "tashani": {},
      "tashania": {},
      "tashanian": {},
      "wind_of_tishani": {},
      "wind_of_tishanian": {}
    },
    "spell_line_holy_guard_you_off": {
      "aegis": {},
      "bulwark_of_faith": {}
    },
    "spell_line_holy_armor_you_off": {
      "armor_of_faith": {},
      "guard": {},
      "holy_armor": {},
      "shield_of_words": {}
    },
    "spell_line_dot_enc_you_off": {
      "asphyxiate": {},
      "choke": {},
      "gasping_embrace": {},
      "shallow_breath": {},
      "suffocate": {}
    },
    "spell_line_target_vision_you_off": {
      "assiduous_vision": {},
      "vision": {}
    },
    "spell_line_regen_you_off": {
      "aura_of_battle": {},
      "chloroplast": {},
      "extended_regeneration": {},
      "fungal_regrowth": {},
      "pack_chloroplast": {},
      "pack_regeneration": {},
      "regeneration": {},
      "regrowth": {},
      "regrowth_of_the_grove": {},
      "stalwart_regeneration": {}
    },
    "spell_line_spin_you_off": {
      "bellowing_winds": {},
      "dyns_dizzying_draught": {},
      "spin_the_bottle": {},
      "whirl_till_you_hurl": {}
    },
    "spell_line_berserker_madness_you_off": {
      "berserker_madness_i": {},
      "berserker_madness_ii": {},
      "berserker_madness_iii": {},
      "berserker_madness_iv": {}
    },
    "spell_line_enduring_breath_you_off": {
      "breath_of_the_dead": {},
      "enduring_breath": {},
      "everlasting_breath": {}
    },
    "spell_line_brittle_haste_you_off": {
      "brittle_haste_ii": {},
      "brittle_haste_iii": {},
      "brittle_haste_iv": {}
    },
    "spell_line_enc_ac_you_off": {
      "cloud": {},
      "haze": {},
      "mist": {},
      "obscure": {},
      "shade": {},
      "shadow": {},
      "umbra": {}
    },
    "spell_line_debuff_you_off": {
      "cripple": {},
      "disempower": {},
      "frenzied_strength": {},
      "incapacitate": {},
      "listless_power": {},
      "reckless_strength": {},
      "resurrection_effects": {},
      "surge_of_enfeeblement": {},
      "wave_of_enfeeblement": {}
    },
    "spell_line_npc_disease_you_off": {
      "disease": {},
      "plagueratdisease": {},
      "rabies": {},
      "strong_disease": {}
    },
    "spell_line_slow_you_off": {
      "drowsy": {},
      "tagars_insects": {},
      "tigirs_insects": {},
      "turgurs_insects": {},
      "walking_sleep": {}
    },
    "spell_line_flesh_rot_you_off": {
      "flesh_rot_i": {},
      "flesh_rot_ii": {},
      "flesh_rot_iii": {}
    },
    "spell_line_wolf_form_you_off": {
      "form_of_the_great_wolf": {},
      "form_of_the_howler": {},
      "form_of_the_hunter": {},
      "greater_wolf_form": {},
      "share_wolf_form": {},
      "wolf_form": {}
    },
    "spell_line_enc_slow_you_off": {
      "forlorn_deeds": {},
      "shiftless_deeds": {},
      "tepid_deeds": {}
    },
    "spell_line_dru_tree_you_off": {
      "spirit_of_oak": {},
      "treeform": {}
    },
    "spell_line_haste_you_off": {
      "aanyas_quickening": {},
      "blessing_of_the_grove": {},
      "alacrity": {},
      "celerity": {},
      "haste": {},
      "quickness": {},
      "swift_like_the_wind": {},
      "swift_spirit": {},
      "wonderous_rapidity": {}
    },
    "spell_line_see_invis_you_off": {
      "acumen": {},
      "see_invisible": {},
      "spirit_sight": {}
    },
    "spell_line_enc_charisma_you_off": {
      "adorning_grace": {},
      "overwhelming_splendor": {}
    },
    "spell_line_dot_disease_you_off": {
      "affliction": {},
      "insidious_decay": {},
      "insidious_fever": {},
      "insidious_malady": {},
      "plague": {},
      "scourge": {},
      "sebilite_pox": {},
      "sicken": {}
    },
    "spell_line_agility_you_off": {
      "agility": {},
      "deliriously": {},
      "nimble": {},
      "feet_like_cat": {}
    },
    "spell_line_nec_regen_you_off": {
      "arch_lich": {},
      "call_of_bones": {},
      "demi_lich": {},
      "lich": {}
    },
    "spell_line_int_caster_shield_you_off": {
      "arch_shielding": {},
      "greater_shielding": {},
      "lesser_shielding": {},
      "major_shielding": {}
    },
    "spell_line_protection_you_off": {
      "armor_of_protection": {},
      "nivs_melody_of_preservation": {},
      "protect": {},
      "group_resist_magic": {}
    },
    "spell_line_root_you_off": {
      "atols_spectral_shackles": {},
      "enstill": {},
      "bonds_of_force": {},
      "bonds_of_tunare": {},
      "earthelementalattack": {},
      "fetter": {},
      "immobilize": {},
      "paralyzing_earth": {},
      "paralyzing_poison_i": {},
      "paralyzing_poison_ii": {},
      "paralyzing_poison_iii": {},
      "root": {},
      "vengeance_of_the_glades": {}
    },
    "spell_line_skin_you_off": {
      "barbcoat": {},
      "bladecoat": {},
      "bobbing_corpse": {},
      "bramblecoat": {},
      "diamondskin": {},
      "leatherskin": {},
      "manasink": {},
      "manaskin": {},
      "natureskin": {},
      "protection_of_the_glades": {},
      "shieldskin": {},
      "skin_like_diamond": {},
      "skin_like_nature": {},
      "skin_like_rock": {},
      "skin_like_steel": {},
      "skin_like_wood": {},
      "skin_of_the_shadow": {},
      "spikecoat": {},
      "steelskin": {},
      "thistlecoat": {},
      "thorncoat": {}
    },
    "spell_line_blind_you_off": {
      "blinding_luminance": {},
      "flash_of_light": {},
      "blinding_poison_i": {},
      "blinding_poison_iii": {},
      "sunbeam": {}
    },
    "spell_line_boil_blood_you_off": {
      "boil_blood": {},
      "boiling_blood": {},
      "heat_blood": {},
      "ignite_blood": {},
      "pyrocruor": {}
    },
    "spell_line_strength_you_off": {
      "burst_of_strength": {},
      "furious_strength": {},
      "maniacal_strength": {},
      "spirit_strength": {},
      "storm_strength": {},
      "strength": {},
      "strength_of_earth": {},
      "strength_of_stone": {},
      "strength_of_the_kunzar": {},
      "strengthen": {},
      "tumultuous_strength": {}
    },
    "spell_line_charisma_you_off": {
      "charisma": {},
      "glamour": {},
      "unfailing_reverence": {}
    },
    "spell_line_ultravision_you_off": {
      "chill_sight": {},
      "ultravision": {}
    },
    "spell_line_infravision_you_off": {
      "heat_sight": {},
      "serpent_sight": {}
    },
    "spell_line_dexterity_you_off": {
      "deftness": {},
      "dexterity": {},
      "rising_dexterity": {}
    },
    "spell_line_invulnerable_you_off": {
      "divine_aura": {},
      "harmshield": {},
      "quivering_veil_of_xarn": {}
    },
    "spell_line_npc_buff_you_off": {
      "dulsehound": {},
      "graveyard_dust": {}
    },
    "spell_line_strength_debuff_you_off": {
      "enfeeblement": {},
      "feckless_might": {},
      "insipid_weakness": {},
      "siphon_strength": {},
      "weakness": {}
    },
    "spell_line_fury_you_off": {
      "fleeting_fury": {},
      "whirlwind": {}
    },
    "spell_line_berserk_you_off": {
      "frenzy": {},
      "fury": {},
      "voice_of_the_berserker": {}
    },
    "spell_line_magnify_you_off": {
      "glimpse": {},
      "magnify": {},
      "sight": {}
    },
    "spell_line_shm_sta_you_off": {
      "health": {},
      "riotous_health": {}
    },
    "spell_line_heroic_valor_you_off": {
      "heroic_bond": {},
      "heroism": {}
    },
    "spell_line_nec_heal_you_off": {
      "pact_of_shadow": {},
      "shadow_compact": {}
    },
    "spell_line_mag_armor_you_off": {
      "phantom_armor": {},
      "phantom_chain": {},
      "phantom_leather": {},
      "phantom_plate": {}
    },
    "spell_line_malo_you_off": {
      "mala": {},
      "malo": {},
      "malosi": {},
      "malosini": {}
    },
    "spell_line_siphon_strength_you_off": {
      "siphon_strength_recourse": {},
      "steal_strength": {}
    },
    "spell_line_shm_hp_you_off": {
      "talisman_of_altuna": {},
      "talisman_of_kragg": {},
      "talisman_of_tnarg": {}
    },
    "spell_line_potion_you_off": {
      "accuracy": {},
      "adroitness": {},
      "aura_of_antibody": {},
      "aura_of_cold": {},
      "aura_of_heat": {},
      "aura_of_purity": {},
      "cohesion": {},
      "null": {},
      "power": {},
      "stability": {},
      "vigor": {}
    },
    "spell_haste_you_off": {
      "augment": {},
      "augmentation": {}
    },
    "spell_line_poison_you_off": {
      "bane_of_nife": {},
      "dizzy_i": {},
      "dizzy_ii": {},
      "dizzy_iii": {},
      "dizzy_iv": {},
      "feeble_mind_i": {},
      "feeble_mind_ii": {},
      "feeble_mind_iii": {},
      "feeble_mind_iv": {},
      "feeble_poison": {},
      "kylies_venom": {},
      "deadly_poison": {},
      "envenomed_bolt": {},
      "envenomed_breath": {},
      "froglok_poison": {},
      "ikatiars_revenge": {},
      "lower_resists_i": {},
      "lower_resists_ii": {},
      "lower_resists_iii": {},
      "lower_resists_iv": {},
      "manticore_poison": {},
      "poison": {},
      "poison_bolt": {},
      "strong_poison": {},
      "system_shock_i": {},
      "system_shock_ii": {},
      "system_shock_iii": {},
      "system_shock_iv": {},
      "system_shock_v": {},
      "venom_of_the_snake": {},
      "weak_poison": {}
    },
    "spell_line_fire_ds_you_off": {
      "barrier_of_combustion": {},
      "boon_of_immolation": {},
      "breath_of_ro": {},
      "cadeau_of_flame": {},
      "inferno_shield": {},
      "obsidian_shatter": {},
      "ros_fiery_sundering": {},
      "shield_of_flame": {},
      "shield_of_lava": {}
    },
    "spell_line_holy_ds_you_off": {
      "blessing_of_nature": {},
      "death_pact": {},
      "mark_of_karn": {}
    },
    "spell_line_nec_hp_you_off": {
      "bond_of_death": {},
      "soul_bond": {},
      "soul_consumption": {},
      "soul_well": {}
    },
    "spell_line_clarity_you_off": {
      "boon_of_the_clear_mind": {},
      "clarity": {}
    },
    "spell_line_clarity_ii_you_off": {
      "clarity_ii": {},
      "gift_of_pure_thought": {}
    },
    "spell_line_nec_snare_you_off": {
      "cascading_darkness": {},
      "clinging_darkness": {},
      "devouring_darkness": {},
      "dooming_darkness": {},
      "engulfing_darkness": {}
    },
    "spell_line_swarm_you_off": {
      "creeping_crud": {},
      "drifting_death": {},
      "drones_of_doom": {},
      "stinging_swarm": {},
      "swarm_of_retribution": {},
      "swarming_pain": {},
      "winged_death": {}
    },
    "spell_line_dru_root_you_off": {
      "engorging_roots": {},
      "engulfing_roots": {},
      "ensnaring_roots": {},
      "entrapping_roots": {},
      "enveloping_roots": {},
      "grasping_roots": {}
    },
    "spell_line_dru_ds_you_off": {
      "legacy_of_spike": {},
      "legacy_of_thorn": {},
      "shield_of_barbs": {},
      "shield_of_brambles": {},
      "shield_of_spikes": {},
      "shield_of_thistles": {},
      "thorny_shield": {}
    },
    "spell_line_wiz_ds_you_off": {
      "okeils_flickering_flame": {},
      "okeils_radiation": {}
    },
    "spell_line_rune_you_off": {
      "rune_i": {},
      "rune_ii": {},
      "rune_iii": {},
      "rune_iv": {},
      "rune_v": {}
    },
    "spell_line_shm_dr_you_off": {
      "talisman_of_jasinth": {},
      "talisman_of_shadoo": {}
    },
    "spell_line_tash_you_off": {
      "tashan": {},
      "tashani": {},
      "tashania": {},
      "tashanian": {},
      "wind_of_tishani": {},
      "wind_of_tishanian": {}
    }
  },
  "version": "%s"
}
"""

    try:
        spell_lines_path = data_path + "spell-lines.json"
        generate = True

        if os.path.isfile(spell_lines_path):
            json_data = open(spell_lines_path, "r", encoding="utf-8")
            spell_lines = json.load(json_data)
            json_data.close()

            if spell_lines["version"] == version:
                generate = False

        if generate:
            print("    - generating spell-lines.json")
            f = open(spell_lines_path, "w", encoding="utf-8")
            f.write(new_spell_lines_data % (version))
            f.close()

    except Exception as e:
        eqa_settings.log(
            "update spell lines: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def get_spell_lines(data_path):
    """Return spell-lines.json"""

    try:
        spell_lines_path = data_path + "spell-lines.json"
        json_data = open(spell_lines_path, "r", encoding="utf-8")
        spell_lines = json.load(json_data)
        json_data.close()

        return spell_lines

    except Exception as e:
        eqa_settings.log(
            "get spell lines: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def update_spell_timers(data_path, eq_spells_file_path):
    """Parse spells_us.txt to data/spell-timers.json"""

    try:
        # Valid Spells
        valid_spells = [
            "aanyas_animation",
            "aanyas_quickening",
            "abolish_disease",
            "abolish_enchantment",
            "abolish_posion",
            "abscond",
            "abundant_drink",
            "abundant_food",
            "accuracy",
            "acid_jet",
            "acumen",
            "adorning_grace",
            "adroitness",
            "aegis",
            "aegis_of_bathezid",
            "aegis_of_ro",
            "aegolism",
            "affliction",
            "agility",
            "agilmentes_aria_of_eagles",
            "alacrity",
            "alenias_disenchanting_melody",
            "alliance",
            "allure",
            "allure_of_death",
            "allure_of_the_wild",
            "alluring_aura",
            "alluring_whispers",
            "aloe_sweat",
            "alter_plane_hate",
            "alter_plane_sky",
            "anarchy",
            "ancient_breath",
            "angstilchs_appalling_screech",
            "angstilchs_assonance",
            "animate_dead",
            "annul_magic",
            "ant_legs",
            "anthem_de_arms",
            "antidote",
            "arch_lich",
            "arch_shielding",
            "armor_of_faith",
            "armor_of_protection",
            "asphyxiate",
            "assiduous_vision",
            "asystole",
            "atols_spectral_shackles",
            "atone",
            "augment",
            "augment_death",
            "augmentation",
            "augmentation_of_death",
            "aura_of_antibody",
            "aura_of_battle",
            "aura_of_black_petals",
            "aura_of_blue_petals",
            "aura_of_cold",
            "aura_of_green_petals",
            "aura_of_heat",
            "aura_of_marr",
            "aura_of_purity",
            "aura_of_red_petals",
            "aura_of_white_petals",
            "avalanche",
            "avatar",
            "avatar_power",
            "avatar_snare",
            "bandoleer_of_luclin",
            "bane_of_nife",
            "banish_summoned",
            "banish_undead",
            "banishment",
            "banishment_of_shadows",
            "banshee_aura",
            "barbcoat",
            "barrier_of_combustion",
            "barrier_of_force",
            "battery_vision",
            "bedlam",
            "befriend_animal",
            "beguile",
            "beguile_animals",
            "beguile_plants",
            "beguile_undead",
            "bellowing_winds",
            "benevolence",
            "berserker_madness_i",
            "berserker_madness_ii",
            "berserker_madness_iii",
            "berserker_madness_iv",
            "berserker_spirit",
            "berserker_strength",
            "bind_affinity",
            "bind_sight",
            "bladecoat",
            "blanket_of_forgetfulness",
            "blast_of_cold",
            "blast_of_poison",
            "blaze",
            "blessing_of_nature",
            "blessing_of_the_blackstar",
            "blessing_of_the_grove",
            "blessing_of_the_theurgist",
            "blinding_fear",
            "blinding_luminance",
            "blinding_poison_i",
            "blind_poison_ii",
            "blinding_poison_iii",
            "blinding_step",
            "blizzard",
            "blizzard_blast",
            "blood_claw",
            "bobbing_corpse",
            "boil_blood",
            "boiling_blood",
            "bolt_of_flame",
            "bolt_of_karana",
            "boltrans_agacerie",
            "boltrans_animation",
            "bond_of_death",
            "bonds_of_force",
            "bonds_of_tunare",
            "bone_melt",
            "bone_shatter",
            "bone_walk",
            "boneshear",
            "boon_of_immolation",
            "boon_of_the_clear_mind",
            "boon_of_the_garou",
            "bramblecoat",
            "bravery",
            "breath_of_karana",
            "breath_of_ro",
            "breath_of_the_dead",
            "breath_of_the_sea",
            "breeze",
            "brilliance",
            "bristlebanes_bundle",
            "bittle_haste_i",
            "brittle_haste_ii",
            "brittle_haste_iii",
            "brittle_haste_iv",
            "bruscos_boastful_bellow",
            "bruscos_bombastic_bellow",
            "bulwark_of_faith",
            "burn",
            "burning_vengeance",
            "burningtouch",
            "burnout",
            "burnout_ii",
            "burnout_iii",
            "burnout_iv",
            "burrowing_scarab",
            "burst_of_fire",
            "burst_of_flame",
            "burst_of_flametest",
            "burst_of_strength",
            "cackling_bones",
            "cadeau_of_flame",
            "cajole_undead",
            "calefaction",
            "calimony",
            "call_of_bones",
            "call_of_earth",
            "call_of_flame",
            "call_of_karana",
            "call_of_sky",
            "call_of_sky_strike",
            "call_of_the_hero",
            "call_of_the_predator",
            "call_of_the_zero",
            "calm",
            "calm_animal",
            "camouflage",
            "can_owhoop_ass",
            "cancel_magic",
            "cannibalize",
            "cannibalize_ii",
            "cannibalize_iii",
            "cannibalize_iv",
            "cantata_of_replenishment",
            "cantata_of_soothin",
            "captain_nalots_quickening",
            "careless_lightning",
            "cascade_of_hail",
            "cascading_darkness",
            "cassindras_chant_of_clarity",
            "cassindras_chorus_of_clarity",
            "cassindras_elegy",
            "cassindras_insipid_ditty",
            "cast_force",
            "cast_sight",
            "cavorting_bones",
            "cazic_gate",
            "cazic_portal",
            "cazic_touch",
            "celerity",
            "celestial_cleansing",
            "celestial_elixer",
            "celestial_healing",
            "celestial_tranquility",
            "center",
            "cessation_of_cor",
            "ceticious_cloud",
            "chant_of_battle",
            "chaos_breath",
            "chaos_flux",
            "chaotic_feedback",
            "char",
            "charisma",
            "charm",
            "charm_animals",
            "chase_the_moon",
            "chill_bones",
            "chill_of_unlife",
            "chill_sight",
            "chilling_embrace",
            "chloroblast",
            "chloroplast",
            "choke",
            "chords_of_dissonance",
            "cindas_charismatic_carillon",
            "cinder_bolt",
            "cinder_jolt",
            "circle_of_butcher",
            "circle_of_cobalt_scar",
            "circle_of_commons",
            "circle_of_feerrott",
            "circle_of_force",
            "circle_of_great_divide",
            "circle_of_iceclad",
            "circle_of_karana",
            "circle_of_lavastorm",
            "circle_of_misty",
            "circle_of_ro",
            "circle_of_steamfont",
            "circle_of_summer",
            "circle_of_surefall_glades",
            "circle_of_the_combines",
            "circle_of_toxxulia",
            "circle_of_wakening_lands",
            "circle_of_winter",
            "clarify_mana",
            "clarity",
            "clarity_ii",
            "cleanse",
            "clinging_darkness",
            "clockwork_poison",
            "cloud",
            "cloud_of_disempowerment",
            "cloud_of_fear",
            "cloud_of_silence",
            "cobalt_scar_gate",
            "cobalt_scar_portal",
            "cog_boost",
            "cohesion",
            "coldlight",
            "collaboration",
            "color_flux",
            "color_shift",
            "color_skew",
            "color_slant",
            "column_of_fire",
            "column_of_frost",
            "column_of_lightning",
            "combine_gate",
            "combine_portal",
            "combust",
            "common_gate",
            "common_portal",
            "companion_spirit",
            "complete_heal",
            "complete_healing",
            "composition_of_ervaj",
            "concussion",
            "conflagration",
            "conglaciation_of_bone",
            "conjuration_air",
            "conjuration_earth",
            "conjuration_fire",
            "conjuration_water",
            "conjure_corpse",
            "contact_poision_i",
            "contact_poision_ii",
            "contact_poision_iii",
            "contact_poision_iv",
            "convergence",
            "convoke_shadow",
            "cornucopia",
            "corporeal_empathy",
            "counteract_disease",
            "counteract_poison",
            "courage",
            "covetous_subversion",
            "creeping_crud",
            "creeping_vision",
            "cripple",
            "crissions_pixie_strike",
            "crystallize_mana",
            "cure_blindness",
            "cure_disease",
            "cure_poison",
            "curse_of_the_garou",
            "curse_of_the_simple_mind",
            "curse_of_the_spirits",
            "dagger_of_symbols",
            "damage_shield",
            "dance_of_the_blade",
            "dance_of_the_fireflies",
            "daring",
            "dark_empathy",
            "dark_pact",
            "dawncall",
            "dazzle",
            "dead_man_floating",
            "dead_men_floating",
            "deadeye",
            "deadly_lifetap",
            "deadly_poison",
            "deadly_velium_poison",
            "death_pact",
            "death_peace",
            "deflux",
            "defoliate",
            "defoliation",
            "deftness",
            "deliriously_nimble",
            "dementia",
            "dementing_visions",
            "demi_lich",
            "denons_bereavement",
            "denons_desperate_dirge",
            "denons_disruptive_discord",
            "denons_dissension",
            "desperate_hope",
            "devouring_darkness",
            "dexterity",
            "dexterous_aura",
            "diamondskin",
            "dictate",
            "dimensional_hole",
            "dimensional_pocket",
            "discordant_mind",
            "disease",
            "disease_cloud",
            "diseased_cloud",
            "disempower",
            "disintegrate",
            "dismiss_summoned",
            "dismiss_undead",
            "distill_mana",
            "distraction",
            "divine_aura",
            "divine_barrier",
            "divine_favor",
            "divine_glory",
            "divine_intervention",
            "divine_light",
            "divine_might",
            "divine_might_effect",
            "divine_purpose",
            "divine_strength",
            "divine_wrath",
            "dizzy_i",
            "dizzy_ii",
            "dizzy_iii",
            "dizzy_iv",
            "dizzying_winds",
            "doljons_rage",
            "dominate_undead",
            "dooming_darkness",
            "draconic_rage",
            "dragon_charm",
            "dragon_roar",
            "drain_soul",
            "drain_spirit",
            "draught_of_fire",
            "draught_of_ice",
            "draught_of_jiva",
            "draught_of_night",
            "drifting_death",
            "drones_of_doom",
            "drowsy",
            "drybonefireburst",
            "dulsehound",
            "dyns_dizzying_draught",
            "dyzils_deafening_decoy",
            "earthcall",
            "earthelementalattack",
            "earthquake",
            "ebbing_strength",
            "echinacea_infusion",
            "effect_flamesong",
            "efreeti_fire",
            "egress",
            "electric_blast",
            "elemental_armor",
            "elemental_maelstrom",
            "elemental_rhythms",
            "elemental_shield",
            "elemental_air",
            "elemental_earth",
            "elemental_fire",
            "elemental_water",
            "elementaling_air",
            "elementaling_earth",
            "elementaling_fire",
            "elementaling_water",
            "elementalkin_air",
            "elementalkin_earth",
            "elementalkin_fire",
            "elementalkin_water",
            "embrace_of_the_kelpmaiden",
            "emmisary_of_thule",
            "enchant_adamantite",
            "enchant_brellium",
            "enchant_clay",
            "enchant_electrum",
            "enchant_gold",
            "enchant_mithril",
            "enchant_platinum",
            "enchant_silver",
            "enchant_steel",
            "enchant_velium",
            "endure_cold",
            "endure_disease",
            "endure_fire",
            "endure_fire",
            "endure_magic",
            "endure_poison",
            "enduring_breath",
            "energy_sap",
            "energy_storm",
            "enfeeblement",
            "enforced_reverence",
            "engorging_roots",
            "engulfing_darkness",
            "engulfing_roots",
            "enlightenment",
            "enslave_death",
            "ensnare",
            "ensnaring_roots",
            "enstill",
            "enthrall",
            "enticement_of_flame",
            "entomb_in_ice",
            "entrance",
            "entrapping_roots",
            "enveloping_roots",
            "envenomed_bolt",
            "envenomed_breath",
            "envenomed_heal",
            "essence_drain",
            "essence_tap",
            "evacuate",
            "evacuate_fay",
            "evacuate_nek",
            "evacuate_north",
            "evacuate_ro",
            "evacuate_west",
            "everfount",
            "everlasting_breath",
            "exile_summoned",
            "exile_undead",
            "expedience",
            "expel_summoned",
            "expel_undead",
            "expulse_summoned",
            "expulse_undead",
            "extended_regeneration",
            "extinguish_fatigue",
            "eye_of_confusion",
            "eye_of_tallon",
            "eye_of_zomm",
            "eyes_of_the_cat",
            "fade",
            "fangols_breath",
            "fascination",
            "fatigue_drain",
            "fay_gate",
            "fay_portal",
            "fear",
            "feast_of_blood",
            "feckless_might",
            "feeble_mind_i",
            "feeble_mind_ii",
            "feeble_mind_iii",
            "feeble_mind_iv",
            "feeble_poison",
            "feedback",
            "feet_like_cat",
            "feign_death",
            "fellspine",
            "feral_spirit",
            "fetter",
            "field_of_bone_port",
            "fiery_death",
            "fiery_might",
            "fingers_of_fire",
            "fire",
            "fire_bolt",
            "fire_flux",
            "fire_spiral_of_alkabor",
            "firefist",
            "firestorm",
            "firestrike",
            "fist_of_air",
            "fist_of_fire",
            "fist_of_karana",
            "fist_of_mastery",
            "fist_of_sentience",
            "fist_of_water",
            "fixation_of_ro",
            "flame_arc",
            "flame_bolt",
            "flame_flux",
            "flame_jet",
            "flame_lick",
            "flame_of_light",
            "flame_of_the_efreeti",
            "flame_shock",
            "flame_song_of_ro",
            "flames_of_ro",
            "flaming_sword_of_xuzl",
            "flare",
            "flash_of_light",
            "fleeting_fury",
            "flesh_rot_i",
            "flesh_rot_ii",
            "flesh_rot_iii",
            "flowing_thought_i",
            "flowing_thought_ii",
            "flowing_thought_iii",
            "flowing_thought_iv",
            "flurry",
            "focus_of_spirit",
            "force",
            "force_shock",
            "force_spiral_of_alkabor",
            "force_strike",
            "forlorn_deeds",
            "form_of_the_great_bear",
            "form_of_the_great_wolf",
            "form_of_the_howler",
            "form_of_the_hunter",
            "fortitude",
            "freezing_breath",
            "frenzied_spirit",
            "frenzied_strength",
            "frenzy",
            "froglok_poison",
            "frost",
            "frost_bolt",
            "frost_breath",
            "frost_port",
            "frost_rift",
            "frost_shards",
            "frost_shock",
            "frost_spiral_of_alkabor",
            "frost_storm",
            "frost_strike",
            "frostbite",
            "frostreavers_blessing",
            "frosty_death",
            "fufils_curtailing_chant",
            "fungal_regrowth",
            "fungus_spores",
            "furious_strength",
            "furor",
            "fury",
            "fury_of_air",
            "gale_of_poison",
            "gangrenous_touch_of_zumuul",
            "garzicors_vengeance",
            "gasping_embrace",
            "gate",
            "gather_shadows",
            "gaze",
            "gelatroot",
            "ghoul_root",
            "gift_of_aerr",
            "gift_of_brilliance",
            "gift_of_insight",
            "gift_of_magic",
            "gift_of_pure_thought",
            "gift_of_xev",
            "girdle_of_karana",
            "glamour",
            "glamour_of_kintaz",
            "glamour_of_tunare",
            "glimpse",
            "grasping_roots",
            "graveyard_dust",
            "gravity_flux",
            "grease_injection",
            "great_divide_gate",
            "great_divide_portal",
            "greater_conjuration_air",
            "greater_conjuration_earth",
            "greater_conjuration_fire",
            "greater_conjuration_water",
            "greater_healing",
            "greater_shielding",
            "greater_summoning_air",
            "greater_summoning_earth",
            "greater_summoning_fire",
            "greater_summoning_water",
            "greater_vocaration_air",
            "greater_vocaration_earth",
            "greater_vocaration_fire",
            "greater_vocaration_water",
            "greater_wolf_form",
            "greenmist",
            "grim_aura",
            "group_resist_magic",
            "guard",
            "guardian",
            "guardian_rhythms",
            "guardian_spirit",
            "halo_of_light",
            "hammer_of_requital",
            "hammer_of_striking",
            "hammer_of_wrath",
            "harmony",
            "harmshield",
            "harpy_voice",
            "harvest",
            "harvest_leaves",
            "haste",
            "haunting_corpse",
            "haze",
            "healing",
            "health",
            "heart_flutter",
            "heat_blood",
            "heat_sight",
            "heroic_bond",
            "heroism",
            "holy_armor",
            "holy_might",
            "holy_shock",
            "hsagras_wrath",
            "hug",
            "hungry_earth",
            "hymn_of_restoration",
            "ice",
            "ice_breath",
            "ice_comet",
            "ice_rend",
            "ice_shock",
            "ice_spear_of_solist",
            "ice_strike",
            "iceclad_gate",
            "iceclad_portal",
            "icestrike",
            "identity",
            "ignite",
            "ignite_blood",
            "ignite_bones",
            "ikatiars_revenge",
            "illusion_air_elemental",
            "illusion_barbarian",
            "illusion_dry_bone",
            "illusion_dwarf",
            "illusion_earth_elemental",
            "illusion_erudite",
            "illusion_fire_elemental",
            "illusion_gnome",
            "illusion_halfelf",
            "illusion_halfling",
            "illusion_high_elf",
            "illusion_human",
            "illusion_iksar",
            "illusion_ogre",
            "illusion_skeleton",
            "illusion_spirit_wolf",
            "illusion_tree",
            "illusion_troll",
            "illusion_water_elemental",
            "illusion_werewolf",
            "illusion_wood_elf",
            "imbue_amber",
            "imbue_black_pearl",
            "imbue_black_sapphire",
            "imbue_diamond",
            "imbue_emerald",
            "imbue_fire_opal",
            "imbue_ivory",
            "imbue_jade",
            "imbue_opal",
            "imbue_peridot",
            "imbue_plains_pebble",
            "imbue_rose_quartz",
            "imbue_ruby",
            "imbue_sapphire",
            "imbue_topaz",
            "immobilize",
            "immolate",
            "immolating_breath",
            "impart_strength",
            "improved_invis_to_undead",
            "improved_invisibility",
            "improved_superior_camouflage",
            "incapacitate",
            "incinerate_bones",
            "infectious_cloud",
            "inferno_of_alkabor",
            "inferno_shield",
            "inferno_shock",
            "infusion",
            "injection_poison_i",
            "injection_poison_ii",
            "injection_poison_iii",
            "injection_poison_iv",
            "injection_poison_v",
            "inner_fire",
            "insidious_decay",
            "insidious_fever",
            "insidious_malady",
            "insight",
            "insipid_weakness",
            "inspire_fear",
            "intensify_death",
            "invert_gravity",
            "invigor",
            "invigorate",
            "invisibility",
            "invisibility_cloak",
            "invisibility_to_undead",
            "invisibility_versus_animal",
            "invisibility_versus_animals",
            "invisibility_versus_undead",
            "invoke_death",
            "invoke_fear",
            "invoke_lightning",
            "invoke_shadow",
            "jaxans_jig_ovigor",
            "jolt",
            "jonthans_inspiration",
            "jonthans_provocation",
            "jonthans_whistling_warsong",
            "journeymansboots",
            "judgement_of_ice",
            "julis_animation",
            "jylls_static_pulse",
            "jylls_wave_of_heat",
            "jylls_zephyr_of_ice",
            "kazumis_note_of_preservation",
            "kelins_lucid_lullaby",
            "kelins_lugubrious_lament",
            "kilans_animation",
            "kilvas_skin_of_flame",
            "kintazs_animation",
            "knights_blessing",
            "knockback",
            "kurrats_magician_epic_guide",
            "kylies_venom",
            "languid_pace",
            "largarns_lamentation",
            "largos_absonant_binding",
            "largos_melodic_binding",
            "lava_bolt",
            "lava_breath",
            "lava_storm",
            "leach",
            "leatherskin",
            "leering_corpse",
            "legacy_of_spike",
            "legacy_of_thorn",
            "lesser_conjuration_air",
            "lesser_conjuration_earth",
            "lesser_conjuration_fire",
            "lesser_conjuration_water",
            "lesser_shielding",
            "lesser_summoning_air",
            "lesser_summoning_earth",
            "lesser_summoning_fire",
            "lesser_summoning_water",
            "levant",
            "levitate",
            "levitation",
            "lich",
            "life_leech",
            "lifedraw",
            "lifespike",
            "lifetap",
            "light_healing",
            "lightning_blast",
            "lightning_bolt",
            "lightning_breath",
            "lightning_shock",
            "lightning_storm",
            "lightning_strike",
            "liquid_silver_i",
            "liquid_silver_ii",
            "liquid_silver_iii",
            "listless_power",
            "locate_corpse",
            "lower_element",
            "lower_resists_i",
            "lower_resists_ii",
            "lower_resists_iii",
            "lower_resists_iv",
            "lull",
            "lull_animal",
            "lure_of_flame",
            "lure_of_frost",
            "lure_of_ice",
            "lure_of_lightning",
            "lyssas_cataloging_libretto",
            "lyssas_locating_lyric",
            "lyssas_solidarity_of_vision",
            "lyssas_veracious_concord",
            "magi_curse",
            "magnify",
            "major_shielding",
            "mala",
            "malaise",
            "malaisement",
            "malevolent_grasp",
            "malo",
            "malosi",
            "malosini",
            "mana_conversion",
            "mana_convert",
            "mana_flare",
            "mana_shroud",
            "mana_sieve",
            "mana_sink",
            "manasink",
            "manaskin",
            "manastorm",
            "maniacal_strength",
            "manifest_elements",
            "manticore_poison",
            "mark_of_karn",
            "markars_clash",
            "markars_discord",
            "markars_relocation",
            "mask_of_the_hunter",
            "mcvaxius_berserker_crescendo",
            "mcvaxius_rousing_rondo",
            "melanies_mellifluous_motion",
            "melodious_beffuddlement",
            "melody_of_ervaj",
            "memory_blur",
            "memory_flux",
            "mend_bones",
            "mesmerization",
            "mesmerize",
            "mesmerizing_breath",
            "mind_cloud",
            "mind_wipe",
            "minion_of_hate",
            "minion_of_shadows",
            "minor_conjuration_air",
            "minor_conjuration_earth",
            "minor_conjuration_fire",
            "minor_conjuration_water",
            "minor_healing",
            "minor_illusion",
            "minor_shielding",
            "minor_summoning_air",
            "minor_summoning_earth",
            "minor_summoning_fire",
            "minor_summoning_water",
            "mircyls_animation",
            "mist",
            "mistwalker",
            "modulating_rod",
            "modulation",
            "monster_summoning_i",
            "monster_summoning_ii",
            "monster_summoning_iii",
            "mortal_deftness",
            "muscle_lock_i",
            "muscle_lock_ii",
            "muscle_lock_iii",
            "muscle_lock_iv",
            "muzzle_of_mardu",
            "mystic_precision",
            "naltrons_mark",
            "nature_walkers_behest",
            "natures_holy_wrath",
            "natures_melody",
            "natures_touch",
            "natures_wrath",
            "natureskin",
            "nek_gate",
            "nek_portal",
            "neutralize_magic",
            "nillipus_march_of_the_wee",
            "nimble",
            "nivs_harmonic",
            "nivs_melody_of_preservation",
            "north_gate",
            "null_aura",
            "nullify_magic",
            "numb_the_dead",
            "numbing_cold",
            "okeils_flickering_flame",
            "okeils_radiation",
            "obscure",
            "obsidian_shatter",
            "occlusion_of_sound",
            "one_hundred_blows",
            "open_black_box",
            "overthere",
            "overwhelming_splendor",
            "pacify",
            "pack_chloroplast",
            "pack_regeneration",
            "pack_spirit",
            "pact_of_shadow",
            "panic",
            "panic_animal",
            "panic_the_dead",
            "paralyzing_earth",
            "paralyzing_poison_i",
            "paralyzing_poison_ii",
            "paralyzing_poison_iii",
            "pendrils_animation",
            "phantom_armor",
            "phantom_chain",
            "phantom_leather",
            "phantom_plate",
            "phobocancel",
            "pillage_enchantment",
            "pillar_of_fire",
            "pillare_of_flame",
            "pillar_of_frost",
            "pillar_of_lightning",
            "plague",
            "plagueratdisease",
            "plainsight",
            "pogonip",
            "poison",
            "poison_animal_i",
            "poison_animal_ii",
            "poison_animal_iii",
            "poison_bolt",
            "poison_breath",
            "poison_storm",
            "poison_summoned_i",
            "poison_summoned_ii",
            "poison_summoned_iii",
            "poisonous_chill",
            "porlos_fury",
            "pouch_of_quellious",
            "power",
            "power_of_the_forests",
            "pox_of_bertoxxulous",
            "primal_avatar",
            "primal_essence",
            "prime_healers_blessing",
            "produce_wrench",
            "project_lightning",
            "protect",
            "protection_of_the_glades",
            "psalm_of_cooling",
            "psalm_of_mystic_shielding",
            "psalm_of_purity",
            "psalm_of_vitality",
            "psalm_of_warmth",
            "purge",
            "purify_mana",
            "purifying_rhythms",
            "putrefy_flesh",
            "putrid_breath",
            "pyrocruor",
            "quickness",
            "quiver_of_marr",
            "quivering_veil_of_xarn",
            "rabies",
            "radiant_visage",
            "rage",
            "rage_of_tallon",
            "rage_of_the_sky",
            "rage_of_vallon",
            "rage_of_zek",
            "rage_of_zomm",
            "rage_of_strength",
            "rage_of_blades",
            "rage_of_fire",
            "rage_of_lava",
            "rage_of_molten_lava",
            "rage_of_spikes",
            "rage_of_swords",
            "rampage",
            "rapacious_subversion",
            "rapture",
            "recant_magic",
            "reckless_health",
            "reckless_strength",
            "reckoning",
            "reclaim_energy",
            "regeneration",
            "regrowth",
            "regrowth_of_the_grove",
            "rejuvenation",
            "remedy",
            "rend",
            "renew_bones",
            "renew_elements",
            "renew_summoning",
            "reoccurring_amnesia",
            "repulse_animal",
            "resist_cold",
            "resist_disease",
            "resist_fire",
            "resist_magic",
            "resist_poison",
            "resistance_to_magic",
            "resistant_skin",
            "resolution",
            "rest_the_dead",
            "restless_bones",
            "restore_sight",
            "resurrection",
            "resurrection_effects",
            "resuscitate",
            "retribution",
            "retribution_of_alkabor",
            "revive",
            "reviviscence",
            "ring_of_butcher",
            "ring_of_cobolt_scar",
            "ring_of_commons",
            "ring_of_faydark",
            "ring_of_feerrott",
            "ring_of_great_divide",
            "ring_of_iceclad",
            "ring_of_karana",
            "ring_of_lavastorm",
            "ring_of_misty",
            "ring_of_ro",
            "ring_of_steamfont",
            "ring_of_surefall_glade",
            "ring_of_the_combines",
            "ring_of_toxxulia",
            "ring_of_wakening_lands",
            "riotous_health",
            "rising_dexterity",
            "ro_gate",
            "ro_portal",
            "ros_fiery_sundering",
            "rodricks_gift",
            "root",
            "rotting_flesh",
            "rubicite_aura",
            "rune_i",
            "rune_ii",
            "rune_iii",
            "rune_iv",
            "rune_v",
            "sacrifice",
            "sagars_animation",
            "sanity_wrap",
            "sathirs_mesmerization",
            "savage_spirit",
            "scale_of_wolf",
            "scale_skin",
            "scarab_storm",
            "scareling_step",
            "scars_of_sigil",
            "scent_of_darkness",
            "scent_of_dusk",
            "scent_of_shadow",
            "scent_of_terris",
            "scintillation",
            "scorching_skin",
            "scoriae",
            "scourge",
            "scream_of_chaos",
            "screaming_mace",
            "screaming_terror",
            "sear",
            "sebilite_pox",
            "sedulous_subversion",
            "see_invisible",
            "seeking_flame_of_seukor",
            "seething_fury",
            "selos_accelerando",
            "selos_assonant_strane",
            "selos_chords_of_cessation",
            "selos_consonant_chain",
            "selos_song_of_travel",
            "sense_animals",
            "sense_summoned",
            "sense_the_dead",
            "sentinel",
            "serpent_sight",
            "servant_of_bones",
            "shade",
            "shadow",
            "shadow_compact",
            "shadow_sight",
            "shadow_step",
            "shadow_vortex",
            "shadowbond",
            "shalees_animation",
            "shallow_breath",
            "shards_of_sorrow",
            "share_wolf_form",
            "shauris_sonorous_clouding",
            "shield_of_barbs",
            "shield_of_blades",
            "shield_of_brambles",
            "shield_of_fire",
            "shield_of_flame",
            "shield_of_lava",
            "shield_of_song",
            "shield_of_spikes",
            "shield_of_eighth",
            "shield_of_the_magi",
            "shield_of_thistles",
            "shield_of_words",
            "shielding",
            "shieldskin",
            "shifting_shield",
            "shifting_sight",
            "shiftless_deeds",
            "shock_of_blades",
            "shock_of_fire",
            "shock_of_flame",
            "shock_of_frost",
            "shock_of_ice",
            "shock_of_lightning",
            "shock_of_poison",
            "shock_of_spikes",
            "shock_of_steel",
            "shock_of_swords",
            "shock_of_the_tainted",
            "shock_spiral_of_alkabor",
            "shrieking_howl",
            "shrink",
            "shroud_of_death",
            "shroud_of_hate",
            "shroud_of_pain",
            "shroud_of_the_spirits",
            "shroud_of_undeath",
            "sicken",
            "sight",
            "sight_graft",
            "silver_breath",
            "silver_skin",
            "siphon",
            "siphon_life",
            "siphon_strength",
            "siphon_strength_recourse",
            "sirocco",
            "sisnas_animation",
            "skin_like_diamond",
            "skin_like_nature",
            "skin_like_rock",
            "skin_like_steel",
            "skin_like_wood",
            "skin_of_the_shadow",
            "skunkspray",
            "slime_mist",
            "smite",
            "smolder",
            "snakeelefireburst",
            "snare",
            "solons_bewitching_bravura",
            "solons_bravura",
            "solons_charismatic_concord",
            "solons_song_of_the_sirens",
            "song_of_dawn",
            "song_of_highsun",
            "song_of_midnight",
            "song_of_the_deep_seas",
            "song_of_twilight",
            "song_composition_of_ervaj",
            "song_melody_of_ervaj",
            "song_occlusion_of_sound",
            "sonic_scream",
            "soothe",
            "soul_bond",
            "soul_consumption",
            "soul_devour",
            "soul_leech",
            "soul_well",
            "sound_of_force",
            "spear_of_warding",
            "specter_lifetap",
            "speed_of_the_shissar",
            "sphere_of_light",
            "spikecoat",
            "spin_the_bottle",
            "spirit_armor",
            "spirit_of_bear",
            "spirit_of_cat",
            "spirit_of_cheetah",
            "spirit_of_monkey",
            "spirit_of_oak",
            "spirit_of_ox",
            "spirit_of_scale",
            "spirit_of_snake",
            "spirit_of_the_howler",
            "spirit_of_wolf",
            "spirit_pouch",
            "spirit_quickening",
            "spirit_sight",
            "spirit_strength",
            "spirit_strike",
            "spirit_tap",
            "splurt",
            "spook_the_dead",
            "stability",
            "staff_of_runes",
            "staff_of_symbols",
            "staff_of_tracing",
            "staff_of_warding",
            "stalking_probe",
            "stalwart_regeneration",
            "stamina",
            "starfire",
            "starshine",
            "static",
            "static_strike",
            "steal_strength",
            "steam_overload",
            "steelskin",
            "stinging_swarm",
            "stone_breath",
            "stone_spider_stun",
            "storm_strength",
            "stream_of_acid",
            "strength",
            "strength_of_earth",
            "strength_of_nature",
            "strength_of_stone",
            "strength_of_the_kunzar",
            "strengthen",
            "strengthen_death",
            "strike",
            "strike_of_the_chosen",
            "strike_of_thunder",
            "strip_enchantment",
            "strong_disease",
            "strong_poison",
            "stun",
            "stun_breath",
            "stun_command",
            "stunning_blow",
            "succor",
            "succor_butcher",
            "succor_east",
            "succor_lavastorm",
            "succor_north",
            "succor_ro",
            "suffocate",
            "suffocating_sphere",
            "summon_arrows",
            "summon_bandages",
            "summon_coldstone",
            "summon_companion",
            "summon_corpse",
            "summon_dagger",
            "summon_dead",
            "summon_drink",
            "summon_fang",
            "summon_food",
            "summon_golin",
            "summon_heatstone",
            "summon_holy_ale_of_brell",
            "summon_lava_diamond",
            "summon_orb",
            "summon_ring_of_flight",
            "summon_shard_of_the_core",
            "summon_throwing_dagger",
            "summon_throwing_hammer",
            "summon_waterstone",
            "summon_wisp",
            "summoning_air",
            "summoning_earth",
            "summoning_fire",
            "summoning_water",
            "sunbeam",
            "sunskin",
            "sunstrike",
            "superior_camouflage",
            "superior_healing",
            "supernova",
            "surge_of_enfeeblement",
            "swamp_port",
            "swarm_of_retribution",
            "swarming_pain",
            "swift_like_the_wind",
            "swift_spirit",
            "sword_of_runes",
            "sword_of_marzin",
            "sword_of_naltron",
            "sword_of_pinzarn",
            "sword_of_ryltan",
            "sword_of_transal",
            "sympathetic_aura",
            "symphonic_harmony",
            "system_shock_i",
            "system_shock_ii",
            "system_shock_iii",
            "system_shock_iv",
            "system_shock_v",
            "syvelians_antimagic_aria",
            "tagars_insects",
            "tainted_breath",
            "talisman_of_altuna",
            "talisman_of_jasinth",
            "talisman_of_kragg",
            "talisman_of_shadoo",
            "talisman_of_the_brute",
            "talisman_of_the_cat",
            "talisman_of_the_raptor",
            "talisman_of_the_rhino",
            "talisman_of_the_serpent",
            "talisman_of_tnarg",
            "taper_enchantment",
            "tarews_aquatic_ayre",
            "tashan",
            "tashani",
            "tashania",
            "tashanian",
            "tears_of_druzzil",
            "tears_of_solusek",
            "telescope",
            "tepid_deeds",
            "terrorize_animal",
            "the_dains_justice",
            "the_unspoken_word",
            "theft_of_thought",
            "thicken_mana",
            "thistlecoat",
            "thorncoat",
            "thorny_shield",
            "thrall_of_bones",
            "thunder_blast",
            "thunder_strike",
            "thunderbold",
            "thunderclap",
            "thurgadin_gate",
            "tigirs_insects",
            "tishans_clash",
            "tishans_relocation",
            "tishans_discord",
            "torgors_insects",
            "torbas_acid_blast",
            "torment",
            "torment_of_argli",
            "torment_of_shadows",
            "torpor",
            "torrent_of_poison",
            "touch_of_night",
            "tox_gate",
            "tox_portal",
            "track_corpse",
            "trakanon_tail",
            "trakanons_touch",
            "translocate",
            "translocate_cazic",
            "translocate_cobolt_scar",
            "translocate_combine",
            "translocate_common",
            "translocate_fay",
            "translocate_great_divide",
            "translocate_group",
            "translocate_iceclad",
            "translocate_nek",
            "translocate_north",
            "translocate_ro",
            "translocate_tox",
            "translocate_wakening_lands",
            "translocate_west",
            "travelerboots",
            "treeform",
            "tremor",
            "trepidation",
            "trucudation",
            "true_north",
            "tsunami",
            "tumultuous_strength",
            "tunares_request",
            "turgurs_insects",
            "turning_of_the_unnatural",
            "tuyens_chant_of_flame",
            "tuyens_chant_of_frost",
            "uleens_animation",
            "ultravision",
            "umbra",
            "unfailing_reverence",
            "unswerving_hammer",
            "upheaval",
            "valiant_companion",
            "valor",
            "vampire_charm",
            "vampire_curse",
            "vampire_embrace",
            "valium_shards",
            "velocity",
            "vengeance_of_alkabor",
            "vengeance_of_the_glades",
            "venom_of_the_snake",
            "verlekarnorms_disaster",
            "versus_of_victory",
            "vexing_mordinia",
            "vigilant_spirit",
            "vigor",
            "villas_chorus_of_celerity",
            "villas_versus_of_celerity",
            "vision",
            "visions_of_grandeur",
            "vocarate_air",
            "vocarate_earth",
            "vocarate_fire",
            "vocarate_water",
            "voice_graft",
            "voice_of_the_berserker",
            "voltaic_draught",
            "wake_of_karana",
            "wake_of_tranquility",
            "wakening_lands_gate",
            "wakening_lands_portal",
            "walking_sleep",
            "wandering_mind",
            "ward_summoned",
            "ward_undead",
            "wave_of_cold",
            "wave_of_enfeeblement",
            "wave_of_fear",
            "wave_of_fire",
            "wave_of_flame",
            "wave_of_healing",
            "wave_of_heat",
            "waves_of_the_deep_sea",
            "weak_poison",
            "weaken",
            "weakning_poison_i",
            "weakning_poison_ii",
            "weakning_poison_iii",
            "weakning_poison_iv",
            "weakness",
            "west_gate",
            "west_portal",
            "whirl_till_you_hurl",
            "whirlwind",
            "wildfire",
            "wind_of_the_north",
            "wind_of_the_south",
            "wind_of_tishani",
            "wind_of_tishanian",
            "winds_of_gelid",
            "winged_death",
            "winters_roar",
            "wolf_form",
            "wonderous_rapidity",
            "word_divine",
            "word_of_healing",
            "word_of_health",
            "word_of_pain",
            "word_of_redemption",
            "word_of_restoration",
            "word_of_shadow",
            "word_of_souls",
            "word_of_spirit",
            "word_of_vigor",
            "wrath",
            "wrath_of_alkabor",
            "wrath_of_nature",
            "wrath_of_elements",
            "yaulp",
            "yaulp_ii",
            "yaulp_iii",
            "yaulp_iv",
            "yegoreffs_animation",
            "ykesha",
            "yonder",
            "zumaiks_animation",
        ]

        spell_timers_file_name = "spell-timers.json"
        spell_timer_file = data_path + spell_timers_file_name

        # Read spells_us.txt
        eq_spells_file = open(eq_spells_file_path, "r")
        eq_spells_file_lines = eq_spells_file.readlines()
        eq_spells_file.close()

        # Calculate file hash
        BLOCKSIZE = 65536
        file_hash = hashlib.md5()
        with open(eq_spells_file_path, "r") as spells_file:
            buf = spells_file.read(BLOCKSIZE)
            while len(buf) > 0:
                file_hash.update(buf.encode("utf-8"))
                buf = spells_file.read(BLOCKSIZE)
        spells_file.close()
        spells_hash = file_hash.hexdigest()

        # Check spell-timers.json version
        if os.path.isfile(spell_timer_file):
            # Generate Spell Timers
            json_data = open(spell_timer_file, "r", encoding="utf-8")
            spell_timers_hash_check = json.load(json_data)
            json_data.close()

            if "hash" not in spell_timers_hash_check.keys():
                generate_spell_timer_file = True
            elif not spell_timers_hash_check["hash"] == spells_hash:
                generate_spell_timer_file = True
            else:
                # Legacy check
                file_hash = hashlib.md5()
                with open(spell_timer_file, "r") as check_file:
                    buf = check_file.read(BLOCKSIZE)
                    while len(buf) > 0:
                        file_hash.update(buf.encode("utf-8"))
                        buf = check_file.read(BLOCKSIZE)
                spells_timer_hash = file_hash.hexdigest()
                if spells_timer_hash == "5f6460b226f5f765de13f3f758fff4d9":
                    generate_spell_timer_file = True
                else:
                    generate_spell_timer_file = False

            if generate_spell_timer_file:
                print("    - generating spell-timers.json (this may take a minute)")
                # Bootstrap new spell-timers.json
                spell_timer_json = {"spells": {}, "hash": spells_hash}

                # Read spells_us.txt line
                for line in eq_spells_file_lines:
                    modified_line = line.split("^")

                    ## Relevant values
                    spell_name = modified_line[1]
                    spell_cast_time = str(int(modified_line[13]) / 1000)
                    spell_buff_duration = modified_line[17]
                    spell_buffdurationformula = modified_line[16]

                    ## Clean spell name
                    line_type_spell_name = re.sub(
                        r"[^a-z\s]", "", spell_name.lower()
                    ).replace(" ", "_")

                    if (
                        line_type_spell_name in valid_spells
                        and spell_buffdurationformula != "0"
                    ):
                        spell_timer_json["spells"].update(
                            {
                                line_type_spell_name: {
                                    "cast_time": spell_cast_time,
                                    "duration": spell_buff_duration,
                                    "formula": spell_buffdurationformula,
                                }
                            }
                        )

                    spell_timer_json.update({"hash": spells_hash})

                    json_data = open(spell_timer_file, "w")
                    json.dump(spell_timer_json, json_data, sort_keys=True, indent=2)
                    json_data.close()
        else:
            print("Generating new spell-timers.json. This may take a minute . . .")
            # Bootstrap new spell-timers.json
            spell_timer_json = {"spells": {}, "hash": spells_hash}

            # Read spells_us.txt line
            for line in eq_spells_file_lines:
                modified_line = line.split("^")

                ## Relevant values
                spell_name = modified_line[1]
                spell_cast_time = str(int(modified_line[13]) / 1000)
                spell_buff_duration = modified_line[17]
                spell_buffdurationformula = modified_line[16]

                ## Clean spell name
                line_type_spell_name = re.sub(
                    r"[^a-z\s]", "", spell_name.lower()
                ).replace(" ", "_")

                if line_type_spell_name in valid_spells:
                    spell_timer_json["spells"].update(
                        {
                            line_type_spell_name: {
                                "cast_time": spell_cast_time,
                                "duration": spell_buff_duration,
                                "formula": spell_buffdurationformula,
                            }
                        }
                    )

                json_data = open(spell_timer_file, "w")
                json.dump(spell_timer_json, json_data, sort_keys=True, indent=2)
                json_data.close()

    except Exception as e:
        eqa_settings.log(
            "update spell timers: Error on line "
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
        configs.settings.config["settings"]["timers"]["spell"].update(
            {
                "guild_only": state.spell_timer_guild_only,
            }
        )
        configs.settings.config["settings"]["timers"]["spell"].update(
            {
                "yours_only": state.spell_timer_yours_only,
            }
        )
        configs.settings.config["settings"]["timers"]["spell"].update(
            {
                "other": str(state.spell_timer_other),
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
            "guild_only"
        ]
        spell_timer_yours_only = configs.settings.config["settings"]["timers"]["spell"][
            "yours_only"
        ]
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
        json_data.close()
        data["line"].update(
            {line_type: {"sound": "false", "reaction": "false", "alert": {}}}
        )
        json_data = open(
            base_path + "config/line-alerts/other.json", "w", encoding="utf-8"
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


def get_players_file(player_data_path, server):
    """Update Player Data File"""

    try:
        player_data_file = player_data_path + "players.json"
        json_data = open(player_data_file, "r", encoding="utf-8")
        player_json_data = json.load(json_data)
        json_data.close()

        player_list = player_json_data["server"][server]["players"]

        return player_list

    except Exception as e:
        eqa_settings.log(
            "get players file: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def update_players_file(player_data_path, server, player_list):
    """Update Player Data File"""

    try:
        player_data_file = player_data_path + "players.json"
        json_data = open(player_data_file, "r", encoding="utf-8")
        player_json_data = json.load(json_data)
        json_data.close

        if server not in player_json_data["server"].keys():
            player_json_data["servers"][server] = {"players": {}}

        player_json_data["server"][server]["players"].update(player_list)

        json_data = open(player_data_file, "w", encoding="utf-8")
        json.dump(player_json_data, json_data, sort_keys=True, indent=2)
        json_data.close()

    except Exception as e:
        eqa_settings.log(
            "update players file: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


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
        f = open(player_data_file, "w", encoding="utf-8")
        f.write(new_players_data % (version))
        f.close()

    except Exception as e:
        eqa_settings.log(
            "generate players file: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def validate_players_file(player_data_file, version):
    """Validate Player Data File"""

    try:
        json_data = open(player_data_file, "r", encoding="utf-8")
        player_json_data = json.load(json_data)
        json_data.close()

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

            json_data = open(player_data_file, "w", encoding="utf-8")
            json.dump(updated_player_list, json_data, sort_keys=True, indent=2)
            json_data.close()

    except Exception as e:
        eqa_settings.log(
            "validate players file: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def build_config(base_path, version):
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
    "consider_eval": {
      "enabled": false
    },
    "debug_mode": {
      "enabled": false
    },
    "detect_character": {
      "enabled": true
    },
    "encounter_parsing": {
      "auto_save": "false",
      "enabled": "true"
    },
    "mute": {
      "enabled": "false"
    },
    "paths": {
      "eqalert_log": "%slog/",
      "data": "%sdata/",
      "encounter": "%sencounters/",
      "everquest_logs": "%s/.wine/drive_c/Program Files/Sony/EverQuest/Logs/",
      "everquest_files": "%s/.wine/drive_c/Program Files/Sony/EverQuest/",
      "sound": "%ssound/",
      "tmp_sound": "/tmp/eqa/sound/"
    },
    "player_data": {
      "persist": true
    },
    "raid_mode": {
      "auto_set": true
    },
    "speech": {
      "expand_lingo": true,
      "tld": "com",
      "lang": "en"
    },
    "timers": {
      "mob": {
        "auto": false,
        "auto_delay": 10
      },
      "spell": {
        "delay": 24,
        "guess": true,
        "other": true,
        "guild_only": false,
        "yours_only": true,
        "self": true,
        "zone_drift": true
      }
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
    },
    "unavailable": {
      "raid_mode": "false",
      "timer": "0"
    }
  },
  "version": "%s"
}
"""

    new_line_combat_config = """
{
  "line": {
    "combat_no_target": {
      "alert": {},
      "reaction": "solo",
      "sound": "no target"
    },
    "combat_other_ds_fire_damage": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_other_ds_thorns_damage": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_other_flurry": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
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
    "combat_other_melee_riposte": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_other_rune_damage": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_ranger_drake": {
      "alert": {},
      "reaction": "solo",
      "sound": "ranger drake"
    },
    "combat_you_cannot_hit": {
      "alert": {},
      "reaction": "solo",
      "sound": "can't hit"
    },
    "combat_you_cannot_see": {
      "alert": {},
      "reaction": "solo",
      "sound": "can't see"
    },
    "combat_you_ds_fire_damage": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_you_ds_thorns_damage": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_you_melee": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_you_melee_dodge": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_you_melee_dodge": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_you_melee_invulnerable": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_your_melee_invulnerable": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_you_melee_parry": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_you_melee_riposte": {
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
    "combat_you_rune_damage": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_your_rune_damage": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
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
    },
    "unconscious": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_slain": {
      "alert": {},
      "reaction": "solo_only",
      "sound": "true"
    }
  },
  "version": "%s"
}
"""

    new_line_spell_general_config = """
{
  "line": {
    "songs_interrupted_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_bind_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_cast_item_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_cast_oom": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_cast_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_cast_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_cooldown_active": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_cured_other": {
      "alert": {},
      "reaction": "solo",
      "sound": "cured"
    },
    "spells_damage_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_damage_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_distracted": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_fizzle_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_fizzle_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_forget": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_gate_collapse": {
      "alert": {},
      "reaction": "solo",
      "sound": "gate collapse"
    },
    "spells_gate_npc_casting": {
      "alert": {},
      "reaction": "solo",
      "sound": "mob gating"
    },
    "spells_gated_npc": {
      "alert": {},
      "reaction": "solo",
      "sound": "mob gated"
    },
    "spells_heal_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_heal_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_illusion_dropping_you": {
      "alert": {},
      "reaction": "solo",
      "sound": "illusion is dropping"
    },
    "spells_interrupt_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_interrupt_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_invis_already": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_invis_dropping_you": {
      "alert": {},
      "reaction": "solo",
      "sound": "invis is dropping"
    },
    "spells_levitate_block": {
      "alert": {},
      "reaction": "solo",
      "sound": "levitate blocked"
    },
    "spells_levitate_dropping_you": {
      "alert": {},
      "reaction": "solo",
      "sound": "levitate is dropping"
    },
    "spells_memorize_abort": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_memorize_already": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_memorize_begin": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_memorize_finish": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_memorize_too_high": {
      "alert": {},
      "reaction": "solo",
      "sound": "I need more experience before learning that"
    },
    "spells_no_target": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_not_hold": {
      "alert": {},
      "reaction": "raid",
      "sound": "did not hold"
    },
    "spells_protected_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_protected_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_recover_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_recover_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_resist_other": {
      "alert": {},
      "reaction": "solo",
      "sound": "resist"
    },
    "spells_resist_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_scribe_begin": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_scribe_finish": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_scribe_swap": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_scribe_swap_instruction": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_sitting": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_song_end": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spells_stun_cast_block": {
      "alert": {},
      "reaction": "solo",
      "sound": "cant cast"
    },
    "spells_summoned_you": {
      "alert": {},
      "reaction": "solo",
      "sound": "you have been summoned"
    },
    "spells_too_powerful": {
      "alert": {},
      "reaction": "solo",
      "sound": "too powerful"
    },
    "spells_worn_off": {
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
    "spell_aanyas_quickening_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_aanyas_quickening_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_abolish_enchantment_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_abolish_enchantment_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_acid_jet_other_casts": {
      "alert": {},
      "reaction": "solo",
      "sound": "acid jet"
    },
    "spell_acid_jet_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_adorning_grace_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_adorning_grace_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_aegis_of_bathezid_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_aegis_of_bathezid_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "aegis of bathezid dropped"
    },
    "spell_aegis_of_bathezid_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_aegis_of_ro_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_aegis_of_ro_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "aegis of ro dropped"
    },
    "spell_aegis_of_ro_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_aegis_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_aegis_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_aegolism_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_aegolism_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "aegolism dropped"
    },
    "spell_aegolism_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_agility_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_agilmentes_aria_of_eagles_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_agilmentes_aria_of_eagles_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "agilementes aria of eagles dropped"
    },
    "spell_agilmentes_aria_of_eagles_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_allure_of_death_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_alluring_aura_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_alluring_aura_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_aloe_sweat_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_aloe_sweat_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "aloe swear dropped"
    },
    "spell_aloe_sweat_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_anarchy_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_anarchy_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_ancient_breath_you_on": {
      "alert": {},
      "reaction": "solo",
      "sound": "get a disease cure"
    },
    "spell_annul_magic_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_annul_magic_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_anthem_de_arms_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_armor_of_protection_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_asystole_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "asystole dropped"
    },
    "spell_asystole_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_atols_spectral_shackles_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_atols_spectral_shackles_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_atone_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_atone_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_aura_of_black_petals_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_aura_of_black_petals_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "aura of black petals dropped"
    },
    "spell_aura_of_black_petals_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_aura_of_blue_petals_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_aura_of_blue_petals_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "aura of blue petals dropped"
    },
    "spell_aura_of_blue_petals_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_aura_of_green_petals_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_aura_of_green_petals_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "aura of green petals dropped"
    },
    "spell_aura_of_green_petals_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_aura_of_marr_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_aura_of_marr_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "aura of marr dropped"
    },
    "spell_aura_of_red_petals_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_aura_of_red_petals_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "aura of red petals dropped"
    },
    "spell_aura_of_red_petals_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_aura_of_white_petals_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_aura_of_white_petals_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "aura of white petals dropped"
    },
    "spell_aura_of_white_petals_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_avalanche_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_avalanche_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_avatar_other_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_avatar_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_avatar_power_you_on": {
      "alert": {},
      "reaction": "raid",
      "sound": "avatar power"
    },
    "spell_avatar_snare_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_avatar_snare_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "avatar snare dropped"
    },
    "spell_avatar_snare_you_on": {
      "alert": {},
      "reaction": "raid",
      "sound": "avatar snare"
    },
    "spell_avatar_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "avatar dropped"
    },
    "spell_avatar_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_bane_of_nife_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_bane_of_nife_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_banshee_aura_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_banshee_aura_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "banshee aura dropped"
    },
    "spell_banshee_aura_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_barbcoat_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_barbcoat_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_barrier_of_combustion_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_barrier_of_force_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_barrier_of_force_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "barrier of force dropped"
    },
    "spell_barrier_of_force_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_battery_vision_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_battery_vision_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "battery vision dropped"
    },
    "spell_battery_vision_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_bedlam_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_bedlam_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "bedlam dropped"
    },
    "spell_bedlam_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_berserker_spirit_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "berserker spirit dropped"
    },
    "spell_berserker_spirit_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_berserker_strength_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_berserker_strength_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "berserker strength dropped"
    },
    "spell_berserker_strength_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_bind_affinity_other_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_bind_affinity_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_bind_affinity_you_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_bind_affinity_you_on": {
      "alert": {},
      "reaction": "solo",
      "sound": "character bind updated"
    },
    "spell_bind_sight_you_off": {
      "alert": {},
      "reaction": "spell",
      "sound": "bind sight dropped"
    },
    "spell_bind_sight_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_bladecoat_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_bladecoat_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_blast_of_cold_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_blast_of_cold_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_blessing_of_nature_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_blessing_of_nature_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_blessing_of_the_blackstar_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_blessing_of_the_blackstar_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_blessing_of_the_theurgist_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_blinding_fear_other_cast": {
      "alert": {},
      "reaction": "raid",
      "sound": "blinding fear"
    },
    "spell_blinding_fear_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_blizzard_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_blizzard_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_blood_claw_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_blood_claw_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "blood claw dropped"
    },
    "spell_blood_claw_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_bobbing_corpse_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_bobbing_corpse_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_boil_blood_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_boil_blood_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_bonds_of_force_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_bonds_of_force_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_bonds_of_tunare_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_bonds_of_tunare_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_bone_shatter_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_boneshear_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_boon_of_the_garou_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_boon_of_the_garou_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_bramblecoat_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_bramblecoat_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_bravery_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_bravery_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "bravery dropped"
    },
    "spell_bravery_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_breath_of_karana_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_breath_of_karana_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_breath_of_the_dead_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_breath_of_the_dead_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_breath_of_the_sea_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_breath_of_the_sea_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "breath of the sea dropped"
    },
    "spell_breath_of_the_sea_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_breeze_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_breeze_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "breeze dropped"
    },
    "spell_breeze_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_brilliance_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_brilliance_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "brilliance dropped"
    },
    "spell_bruscos_boastful_bellow_other_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_bruscos_boastful_bellow_you_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_bruscos_bombastic_bellow_other_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_bruscos_bombastic_bellow_you_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_bulwark_of_faith_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_bulwark_of_faith_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_burn_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_burn_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_burning_vengeance_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_burning_vengeance_you_on": {
      "alert": {},
      "reaction": "group",
      "sound": "burning vengeance"
    },
    "spell_burrowing_scarab_other_cast": {
      "alert": {},
      "reaction": "solo",
      "sound": "burrowing scarab"
    },
    "spell_burrowing_scarab_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "burrowing scarab dropped"
    },
    "spell_burrowing_scarab_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_burst_of_fire_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_burst_of_fire_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_burst_of_flame_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_burst_of_flame_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_burst_of_strength_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_cadeau_of_flame_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_cadeau_of_flame_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_calefaction_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_calefaction_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_calimony_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_calimony_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "calimony dropped"
    },
    "spell_calimony_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_call_of_earth_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_call_of_earth_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "call of earth dropped"
    },
    "spell_call_of_earth_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_call_of_flame_other_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_call_of_flame_you_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_call_of_sky_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_call_of_sky_strike_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_call_of_sky_strike_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_call_of_sky_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "call of sky dropped"
    },
    "spell_call_of_sky_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_call_of_the_hero_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_call_of_the_predator_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_call_of_the_predator_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "call of the predator dropped"
    },
    "spell_call_of_the_predator_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_call_of_the_zero_other_on": {
      "alert": {},
      "reaction": "raid",
      "sound": "call of the zero"
    },
    "spell_call_of_the_zero_you_on": {
      "alert": {},
      "reaction": "raid",
      "sound": "call of the zero"
    },
    "spell_camouflage_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "camouflage dropped"
    },
    "spell_camouflage_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_cancel_magic_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_cancel_magic_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_captain_nalots_quickening_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_captain_nalots_quickening_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "captain nalots quickening dropped"
    },
    "spell_captain_nalots_quickening_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_cascade_of_hail_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_cascade_of_hail_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_cassindras_chorus_of_clarity_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_cassindras_chorus_of_clarity_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_cassindras_elegy_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_cassindras_elegy_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_cassindras_insipid_ditty_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_cassindras_insipid_ditty_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "cassindras insipid ditty dropped"
    },
    "spell_cassindras_insipid_ditty_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_cast_force_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_cast_force_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_cast_sight_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "cast sight dropped"
    },
    "spell_cast_sight_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_center_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_center_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "center dropped"
    },
    "spell_center_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_cessation_of_cor_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_cessation_of_cor_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "cessation of cor dropped"
    },
    "spell_cessation_of_cor_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_ceticious_cloud_other_cast": {
      "alert": {},
      "reaction": "raid",
      "sound": "sev poison"
    },
    "spell_ceticious_cloud_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_ceticious_cloud_you_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_ceticious_cloud_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_chant_of_battle_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_chant_of_battle_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_chaos_flux_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_chaos_flux_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_chaotic_feedback_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_chaotic_feedback_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_char_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_char_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_chase_the_moon_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_chase_the_moon_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "chase the moon dropped"
    },
    "spell_chase_the_moon_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_chill_bones_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_chill_bones_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_chill_of_unlife_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_chill_of_unlife_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "chill of unlife dropped"
    },
    "spell_chill_of_unlife_you_on": {
      "alert": {},
      "reaction": "group",
      "sound": "chill of unlife"
    },
    "spell_chilling_embrace_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_chilling_embrace_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "chilling embrace dropped"
    },
    "spell_chilling_embrace_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_chloroblast_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_chloroblast_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_cindas_charismatic_carillon_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "cindas charismatic carillion dropped"
    },
    "spell_cindas_charismatic_carillon_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_circle_of_force_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_circle_of_force_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_circle_of_summer_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_circle_of_summer_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "circle of summer dropped"
    },
    "spell_circle_of_summer_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_circle_of_the_combines_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_circle_of_winter_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_circle_of_winter_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "circle of winter dropped"
    },
    "spell_circle_of_winter_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_cleanse_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_clinging_darkness_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_clinging_darkness_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_clockwork_poison_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_clockwork_poison_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "clockwork poison dropped"
    },
    "spell_clockwork_poison_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_cloud_of_fear_you_on": {
      "alert": {},
      "reaction": "raid",
      "sound": "silence"
    },
    "spell_cloud_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_cloud_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_cog_boost_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_cog_boost_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "cog boost dropped"
    },
    "spell_cog_boost_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_coldlight_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_coldlight_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_color_slant_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_color_slant_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_column_of_fire_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_column_of_fire_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_column_of_lightning_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_column_of_lightning_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_combust_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_companion_spirit_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_complete_healing_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_complete_healing_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_concussion_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_concussion_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_conglaciation_of_bone_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_conglaciation_of_bone_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_courage_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_courage_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "courage dropped"
    },
    "spell_courage_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_creeping_vision_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_creeping_vision_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_cripple_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_cripple_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_crissions_pixie_strike_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_cure_blindness_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_curse_of_the_simple_mind_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_curse_of_the_simple_mind_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "curse of the simple mind dropped"
    },
    "spell_curse_of_the_simple_mind_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_curse_of_the_spirits_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_curse_of_the_spirits_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "curse of the spirits dropped"
    },
    "spell_curse_of_the_spirits_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_dance_of_the_blade_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "dance of the blade dropped"
    },
    "spell_dance_of_the_blade_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_dance_of_the_fireflies_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_dance_of_the_fireflies_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_daring_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_daring_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "daring dropped"
    },
    "spell_daring_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_dark_empathy_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_dark_empathy_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_dark_pact_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_dawncall_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_dawncall_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "dawncall dropped"
    },
    "spell_dawncall_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_dead_man_floating_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_dead_man_floating_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "dead man floating dropped"
    },
    "spell_dead_man_floating_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_deadly_lifetap_other_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_deadly_lifetap_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_deadly_velium_poison_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_deadly_velium_poison_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "deadly velium poison dropped"
    },
    "spell_deadly_velium_poison_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_death_pact_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_death_pact_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_deliriously_nimble_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_deliriously_nimble_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_dementia_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_dementia_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_dementing_visions_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_dementing_visions_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_denons_bereavement_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_denons_bereavement_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_denons_desperate_dirge_other_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_denons_desperate_dirge_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_denons_desperate_dirge_you_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_denons_desperate_dirge_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_desperate_hope_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_desperate_hope_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "desperate hope dropped"
    },
    "spell_desperate_hope_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_devouring_darkness_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_devouring_darkness_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_dexterous_aura_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_dexterous_aura_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "dexterous aura dropped"
    },
    "spell_diamondskin_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_diamondskin_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_discordant_mind_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_discordant_mind_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_disease_cloud_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_disease_cloud_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "disease cloud dropped"
    },
    "spell_disease_cloud_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_diseased_cloud_other_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_diseased_cloud_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_diseased_cloud_you_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_diseased_cloud_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_disintegrate_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_distraction_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_distraction_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_divine_aura_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_divine_barrier_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_divine_barrier_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "divine barrier dropped"
    },
    "spell_divine_barrier_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_divine_favor_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_divine_favor_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "divine favor dropped"
    },
    "spell_divine_favor_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_divine_glory_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_divine_glory_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "divine glory dropped"
    },
    "spell_divine_glory_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_divine_intervention_other_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_divine_intervention_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_divine_intervention_you_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_divine_intervention_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "divine intervention dropped"
    },
    "spell_divine_intervention_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_divine_light_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_divine_light_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_divine_might_effect_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_divine_might_effect_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_divine_might_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_divine_might_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "divine might dropped"
    },
    "spell_divine_might_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_divine_purpose_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_divine_purpose_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "divine purpose dropped"
    },
    "spell_divine_purpose_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_divine_strength_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_divine_strength_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "divine strength dropped"
    },
    "spell_divine_strength_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_divine_wrath_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_dizzy_i_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_dizzy_iv_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_doljons_rage_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_doljons_rage_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_dot_nec_heart_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_draconic_rage_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_draconic_rage_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "draconic rage dropped"
    },
    "spell_draconic_rage_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_dragon_roar_other_cast": {
      "alert": {},
      "reaction": "raid",
      "sound": "roar"
    },
    "spell_dragon_roar_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_draught_of_fire_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_draught_of_fire_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_draught_of_ice_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_draught_of_ice_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_draught_of_jiva_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_draught_of_jiva_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_drybonefireburst_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_drybonefireburst_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_dulsehound_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_dulsehound_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_earthcall_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_earthcall_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "earthcall dropped"
    },
    "spell_earthcall_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_earthelementalattack_other_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_earthelementalattack_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_earthquake_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_earthquake_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_echinacea_infusion_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_echinacea_infusion_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "echinacea infusion dropped"
    },
    "spell_echinacea_infusion_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_efreeti_fire_you_on": {
      "alert": {},
      "reaction": "group",
      "sound": "efreeti fire"
    },
    "spell_egress_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_electric_blast_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_electric_blast_you_on": {
      "alert": {},
      "reaction": "raid",
      "sound": "electric blast"
    },
    "spell_elemental_armor_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "elemental armor dropped"
    },
    "spell_elemental_maelstrom_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_elemental_maelstrom_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "elemental maelstrom dropped"
    },
    "spell_elemental_maelstrom_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_elemental_rhythms_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_elemental_shield_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "elemental shield dropped"
    },
    "spell_embrace_of_the_kelpmaiden_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_embrace_of_the_kelpmaiden_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "embrace of the kelp maiden dropped"
    },
    "spell_embrace_of_the_kelpmaiden_you_on": {
      "alert": {},
      "reaction": "solo",
      "sound": "kelp maiden snare"
    },
    "spell_endure_cold_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_endure_cold_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "endure cold dropped"
    },
    "spell_endure_disease_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_endure_disease_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "endure disease dropped"
    },
    "spell_endure_fire_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_endure_fire_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "endure fire dropped"
    },
    "spell_endure_magic_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_endure_magic_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "endure magic dropped"
    },
    "spell_endure_poison_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_endure_poison_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "endure poison dropped"
    },
    "spell_energy_sap_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_energy_sap_you_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_energy_sap_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "energy sap dropped"
    },
    "spell_energy_sap_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_energy_storm_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_energy_storm_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_enfeeblement_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_enfeeblement_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_enforced_reverence_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_enforced_reverence_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_engorging_roots_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_engorging_roots_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_enlightenment_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_enlightenment_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "enlightenment dropped"
    },
    "spell_enlightenment_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_ensnare_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "ensnare dropped"
    },
    "spell_enthrall_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_enthrall_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "enthrall dropped"
    },
    "spell_enthrall_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_enticement_of_flame_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_enticement_of_flame_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_entomb_in_ice_other_cast": {
      "alert": {},
      "reaction": "raid",
      "sound": "ice"
    },
    "spell_entomb_in_ice_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "entomb in ice dropped"
    },
    "spell_entrance_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_entrance_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "entrance dropped"
    },
    "spell_entrance_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_envenomed_breath_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_envenomed_heal_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_envenomed_heal_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_essence_drain_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_essence_tap_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_eye_of_confusion_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_eye_of_confusion_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "eye of confusion dropped"
    },
    "spell_eye_of_confusion_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_eye_of_tallon_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "eye of tallon dropped"
    },
    "spell_eyes_of_the_cat_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_fade_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_fade_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "fade dropped"
    },
    "spell_fade_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_fangols_breath_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_fangols_breath_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_fascination_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_fascination_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "fascination dropped"
    },
    "spell_fascination_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_fatigue_drain_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_fatigue_drain_you_on": {
      "alert": {},
      "reaction": "solo",
      "sound": "fatigue drain"
    },
    "spell_fear_other_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_fear_you_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_feeble_mind_iv_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_feedback_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_feedback_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "feedback dropped"
    },
    "spell_feedback_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_feet_like_cat_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_feet_like_cat_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_feign_death_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_feign_death_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "feign death dropped"
    },
    "spell_fellspine_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_fellspine_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "fellspine dropped"
    },
    "spell_fellspine_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_fiery_might_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_fiery_might_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "fiery might dropped"
    },
    "spell_fiery_might_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_fingers_of_fire_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_fire_spiral_of_alkabor_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_fire_spiral_of_alkabor_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_firefist_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_firefist_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "firefist dropped"
    },
    "spell_firefist_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_firestorm_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_fist_of_karana_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_fist_of_karana_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_fist_of_sentience_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_fist_of_sentience_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "fist of sentience dropped"
    },
    "spell_fist_of_sentience_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_fist_of_water_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_fist_of_water_you_on": {
      "alert": {},
      "reaction": "solo",
      "sound": "fist of water"
    },
    "spell_fixation_of_ro_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_fixation_of_ro_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "fixation of ro dropped"
    },
    "spell_fixation_of_ro_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_flame_jet_other_cast": {
      "alert": {},
      "reaction": "group",
      "sound": "flame jet"
    },
    "spell_flame_jet_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_flame_lick_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_flame_lick_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "flame lick dropped"
    },
    "spell_flame_lick_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_flame_of_light_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_flame_of_light_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_flame_of_the_efreeti_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_flame_of_the_efreeti_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_flames_of_ro_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_flames_of_ro_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_flavor_nec_hp": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_fleeting_fury_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_fleeting_fury_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_flurry_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_flurry_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "flurry dropped"
    },
    "spell_flurry_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_focus_of_spirit_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_focus_of_spirit_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "focus of spirit dropped"
    },
    "spell_focus_of_spirit_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_force_spiral_of_alkabor_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_force_spiral_of_alkabor_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_form_of_the_great_bear_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_form_of_the_great_bear_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "form of the great bear dropped"
    },
    "spell_form_of_the_great_bear_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_fortitude_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_fortitude_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_freezing_breath_other_cast": {
      "alert": {},
      "reaction": "raid",
      "sound": "freezing breath"
    },
    "spell_freezing_breath_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_freezing_breath_you_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_freezing_breath_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_frenzied_spirit_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_frenzied_spirit_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_frenzied_strength_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_frenzied_strength_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_frost_bolt_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_frost_bolt_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_frost_breath_other_cast": {
      "alert": {},
      "reaction": "raid",
      "sound": "frost breath"
    },
    "spell_frost_breath_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_frost_breath_you_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_frost_breath_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_frost_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_frost_rift_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_frost_rift_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_frost_storm_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_frost_storm_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "frost storm dropped"
    },
    "spell_frost_storm_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_frost_strike_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_frost_strike_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_frost_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_frostbite_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_frostbite_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_frostreavers_blessing_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_frostreavers_blessing_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "frostreavers blessing dropped"
    },
    "spell_frostreavers_blessing_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_frosty_death_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_frosty_death_you_on": {
      "alert": {},
      "reaction": "solo",
      "sound": "frosty death"
    },
    "spell_fufils_curtailing_chant_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_fufils_curtailing_chant_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "fufils curtailing chant dropped"
    },
    "spell_fufils_curtailing_chant_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_fungal_regrowth_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_fungal_regrowth_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_fungus_spores_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_fungus_spores_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "fungus spores dropped"
    },
    "spell_fungus_spores_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_furor_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_furor_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_gangrenous_touch_of_zumuul_other_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_gangrenous_touch_of_zumuul_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_gangrenous_touch_of_zumuul_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_garzicors_vengeance_other_on": {
      "alert": {},
      "reaction": "solo",
      "sound": "garzicor is not happy"
    },
    "spell_garzicors_vengeance_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "garzicors vengeance dropped"
    },
    "spell_gather_shadows_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_gather_shadows_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "gather shadows dropped"
    },
    "spell_gather_shadows_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_gaze_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "gaze dropped"
    },
    "spell_gaze_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_gelatroot_other_cast": {
      "alert": {},
      "reaction": "solo",
      "sound": "gel root"
    },
    "spell_gelatroot_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "gelatinous root dropped"
    },
    "spell_gelatroot_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_ghoul_root_other_cast": {
      "alert": {},
      "reaction": "solo",
      "sound": "ghoul root"
    },
    "spell_ghoul_root_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "ghoul root dropped"
    },
    "spell_ghoul_root_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_gift_of_aerr_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_gift_of_aerr_you_on": {
      "alert": {},
      "reaction": "raid",
      "sound": "lifetap a.e."
    },
    "spell_gift_of_brilliance_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "gift of brilliance dropped"
    },
    "spell_gift_of_insight_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "gift of insight dropped"
    },
    "spell_gift_of_magic_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "gift of magic dropped"
    },
    "spell_girdle_of_karana_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "girdle of karana dropped"
    },
    "spell_girdle_of_karana_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_glamour_of_kintaz_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_glamour_of_kintaz_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_glamour_of_tunare_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_glamour_of_tunare_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "glamour of tunare dropped"
    },
    "spell_graveyard_dust_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_graveyard_dust_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_grease_injection_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_grease_injection_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "grease injection dropped"
    },
    "spell_grease_injection_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_greenmist_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_greenmist_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_grim_aura_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_grim_aura_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "grim aura dropped"
    },
    "spell_grim_aura_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_guardian_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_guardian_rhythms_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_guardian_spirit_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_guardian_spirit_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_guardian_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "guardian dropped"
    },
    "spell_guardian_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_halo_of_light_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_halo_of_light_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_harmshield_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_harpy_voice_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "harpy voice dropped"
    },
    "spell_harpy_voice_you_on": {
      "alert": {},
      "reaction": "raid",
      "sound": "you have been mesmerized"
    },
    "spell_harvest_leaves_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_harvest_leaves_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_harvest_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_harvest_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_haste_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "haste dropped"
    },
    "spell_health_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_health_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_heart_flutter_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "heart flutter dropped"
    },
    "spell_heart_flutter_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_heat_blood_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_heat_blood_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_holy_shock_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_holy_shock_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_hug_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_hug_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "hug dropped"
    },
    "spell_hug_you_on": {
      "alert": {},
      "reaction": "solo",
      "sound": "hug"
    },
    "spell_ice_breath_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_ice_breath_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "ice breath dropped"
    },
    "spell_ice_breath_you_on": {
      "alert": {},
      "reaction": "solo",
      "sound": "ice breath"
    },
    "spell_ice_rend_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_ice_rend_you_on": {
      "alert": {},
      "reaction": "solo",
      "sound": "ice rend"
    },
    "spell_ice_spear_of_solist_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_ice_spear_of_solist_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_ice_strike_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_ice_strike_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "ice strike dropped"
    },
    "spell_ice_strike_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_icestrike_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_icestrike_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_ignite_bones_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_ignite_bones_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_immolate_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_immolate_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "immolate dropped"
    },
    "spell_immolate_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_immolating_breath_other_cast": {
      "alert": {},
      "reaction": "raid",
      "sound": "immolating breath"
    },
    "spell_immolating_breath_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_immolating_breath_you_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_immolating_breath_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_impart_strength_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "impart strength dropped"
    },
    "spell_incinerate_bones_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_incinerate_bones_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_infectious_cloud_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_infectious_cloud_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_inferno_of_alkabor_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_inferno_of_alkabor_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_infusion_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_infusion_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_inner_fire_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "inner fire dropped"
    },
    "spell_insight_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_insight_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "insight dropped"
    },
    "spell_insight_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_inspire_fear_other_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_invert_gravity_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_invigorate_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_invisibility_cloak_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_invisibility_cloak_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_invoke_fear_other_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_jonthans_inspiration_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "jonthans inspiration dropped"
    },
    "spell_jonthans_inspiration_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_jonthans_provocation_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_jonthans_provocation_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "jonthans provocation dropped"
    },
    "spell_jonthans_provocation_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_jonthans_whistling_warsong_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "jonthans whistling warsong dropped"
    },
    "spell_jonthans_whistling_warsong_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_jylls_static_pulse_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_jylls_static_pulse_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_jylls_wave_of_heat_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_jylls_wave_of_heat_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_jylls_zephyr_of_ice_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_jylls_zephyr_of_ice_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_kazumis_note_of_preservation_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "kazumis note of preservation dropped"
    },
    "spell_kelins_lucid_lullaby_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_kelins_lucid_lullaby_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "kelins lucis lullaby dropped"
    },
    "spell_kelins_lucid_lullaby_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_kelins_lugubrious_lament_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_kelins_lugubrious_lament_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "kelins lugubrious lament dropped"
    },
    "spell_kelins_lugubrious_lament_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_knockback_other_cast": {
      "alert": {},
      "reaction": "solo",
      "sound": "knockback"
    },
    "spell_knockback_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_knockback_you_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_knockback_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_kylies_venom_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_kylies_venom_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_largarns_lamentation_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_largarns_lamentation_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "largarns lamentation dropped"
    },
    "spell_largarns_lamentation_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_largos_absonant_binding_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "largos absonant binding dropped"
    },
    "spell_lava_breath_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_lava_breath_you_on": {
      "alert": {},
      "reaction": "group",
      "sound": "lava breath"
    },
    "spell_lava_storm_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_leach_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_leach_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_leatherskin_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_leatherskin_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_levant_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_levitate_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_levitate_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "levitate dropped"
    },
    "spell_levitate_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_life_leech_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_light_healing_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_lightning_bolt_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_lightning_bolt_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_lightning_breath_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_lightning_breath_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_lightning_shock_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_lightning_storm_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_lightning_storm_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_lightning_strike_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_lightning_strike_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_agility_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_agility_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "agility spell dropped"
    },
    "spell_line_aura_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "aura spell dropped"
    },
    "spell_line_bard_cancel_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_berserk_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_berserk_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "berserk spell dropped"
    },
    "spell_line_berserk_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_berserker_madness_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_berserker_madness_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "berserker madness spell dropped"
    },
    "spell_line_berserker_madness_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_bind_sight_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_blind_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_blind_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "blind spell dropped"
    },
    "spell_line_blind_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_blinding_poison_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_blinding_poison_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_blizzard_blast_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_blizzard_blast_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_boil_blood_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "boil blood spell dropped"
    },
    "spell_line_bolt_of_flame_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_bolt_of_flame_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_bolt_of_karana_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_bolt_of_karana_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_brd_bruscos_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_brd_bruscos_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_brd_cc_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_brd_charm_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "bard charm dropped"
    },
    "spell_line_brd_dd_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_brd_haste_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_brd_resists_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "bard resist dropped"
    },
    "spell_line_brd_slow_other_on": {
      "alert": {},
      "reaction": "solo",
      "sound": "bard slow"
    },
    "spell_line_brd_slow_you_on": {
      "alert": {},
      "reaction": "solo",
      "sound": "bard slow"
    },
    "spell_line_brd_strands_fade_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "lyssas solidarity of vision dropped"
    },
    "spell_line_brd_tuyen_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_brd_tuyen_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "bard tuyen dropped"
    },
    "spell_line_brd_tuyen_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_brittle_haste_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "brittle haste spell dropped"
    },
    "spell_line_brittle_haste_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_cannibalize_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_cat_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_charisma_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_charisma_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "charisma spell dropped"
    },
    "spell_line_charisma_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_charm_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_charm_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "charm spell dropped"
    },
    "spell_line_charm_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_clarity_ii_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_clarity_ii_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "clarity two dropped"
    },
    "spell_line_clarity_ii_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_clarity_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_clarity_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "clarity dropped"
    },
    "spell_line_clarity_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_cold_resist_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_combust_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_combusts_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_debuff_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_debuff_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "debuff spell dropped"
    },
    "spell_line_debuff_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_defoliation_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_dexterity_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_dexterity_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "dexterity spell dropped"
    },
    "spell_line_dexterity_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_disease_resist_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_dizzy_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_dot_disease_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_dot_disease_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "disease dot spell dropped"
    },
    "spell_line_dot_disease_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_dot_enc_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_dot_enc_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "enchanter dot spell dropped"
    },
    "spell_line_dot_enc_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_dru_best_hp_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_dru_best_hp_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_dru_ds_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_dru_ds_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "druid damage shield dropped"
    },
    "spell_line_dru_ds_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_dru_fire_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_dru_fire_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_dru_root_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_dru_root_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "i'm free!"
    },
    "spell_line_dru_root_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_dru_skyfire_or_ej_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_dru_skyfire_or_ej_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_dru_tree_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_dru_tree_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "leaf me out of this"
    },
    "spell_line_dru_tree_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_enc_ac_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_enc_ac_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "enchanter armor spell dropped"
    },
    "spell_line_enc_ac_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_enc_cancel_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_enc_cancel_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_enc_charisma_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "enchanter charisma spell dropped"
    },
    "spell_line_enc_debuff_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_enc_debuff_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_enc_mana_buff_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_enc_mana_buff_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_enc_slow_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_enc_slow_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "enchanter slow spell dropped"
    },
    "spell_line_enc_slow_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_enc_stun_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_enc_stun_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "enchanter stun spell dropped"
    },
    "spell_line_enc_stun_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_endurance_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_endurance_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_enduring_breath_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_enduring_breath_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "you can't breath"
    },
    "spell_line_enduring_breath_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_faction_increase_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_faction_increase_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "faction increase spell dropped"
    },
    "spell_line_faction_increase_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_fade_away_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_fear_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_fear_undead_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_fear_undead_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_fear_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "fear spell dropped"
    },
    "spell_line_fear_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_feeble_mind_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_feel_better_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "that was nice"
    },
    "spell_line_fire_ds_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "fire damage shield dropped"
    },
    "spell_line_fire_flame_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_fire_flame_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_fire_flames_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_fire_flames_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_fire_ignite_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_fire_ignite_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_fire_resist_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_flesh_rot_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_flesh_rot_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "flesh rot spell dropped"
    },
    "spell_line_flesh_rot_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_force_strike_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_force_strike_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_fragile_sow_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_fragile_sow_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_frost_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_frost_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_fury_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "fury spell dropped"
    },
    "spell_line_grav_flux_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_grav_flux_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_group_portal_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_group_portal_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "let's go"
    },
    "spell_line_hammer_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_haste_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_haste_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "haste spell dropped"
    },
    "spell_line_haste_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_haste_stats_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_npc_item_haste_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_healing_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_healing_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_heroic_valor_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_heroic_valor_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "heroic valor spell dropped"
    },
    "spell_line_heroic_valor_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_holy_armor_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_holy_armor_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "holy armor spell dropped"
    },
    "spell_line_holy_armor_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_holy_ds_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "holy damage shield spell dropped"
    },
    "spell_line_holy_guard_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "holy guard spell dropped"
    },
    "spell_line_hot_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_hot_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "heal over time spell dropped"
    },
    "spell_line_hot_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_hungry_earth_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_illusion_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_illusion_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "illusion dropped"
    },
    "spell_line_illusion_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_infravision_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_infravision_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "infravision spell dropped"
    },
    "spell_line_infravision_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_int_caster_shield_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "caster shield spell dropped"
    },
    "spell_line_int_caster_shield_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_int_resists_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_int_resists_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_invis_animal_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_invis_animal_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "invis against animals spell dropped"
    },
    "spell_line_invis_animal_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_invis_undead_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_invis_undead_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "invis against undead spell dropped"
    },
    "spell_line_invis_undead_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_invis_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "invis dropped"
    },
    "spell_line_invis_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_invulnerable_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "invulnerable dropped"
    },
    "spell_line_koi_or_trident_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_lava_storm_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_leach_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_liquid_silver_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_liquid_silver_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_low_nec_mana_regen_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_low_tash_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_lower_resists_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_mag_armor_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "magician armor dropped"
    },
    "spell_line_mag_ds_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_high_mag_ds_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_low_mag_ds_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_mag_shock_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_mag_shock_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_mag_sow_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_magic_resist_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_magic_resist_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_magnify_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_magnify_you_off": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_magnify_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_malo_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_malo_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "malo spell dropped"
    },
    "spell_line_malo_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_memblur_other_on": {
      "alert": {},
      "reaction": "raid",
      "sound": "memblur"
    },
    "spell_line_memblur_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_mez_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_mez_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "mesmerization spell dropped"
    },
    "spell_line_mez_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_mind_clears_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_minor_shielding_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "minor shielding spell dropped"
    },
    "spell_line_muscle_lock_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_nec_charm_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_nec_fire_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_nec_fire_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_nec_haste_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_nec_heal_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_nec_heal_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "necromancer heal spell dropped"
    },
    "spell_line_nec_hp_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "necromancer hp spell dropped"
    },
    "spell_line_nec_hp_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_nec_pet_heal_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_nec_pet_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_nec_regen_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_nec_regen_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "necromancer regeneration spell dropped"
    },
    "spell_line_nec_regen_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_nec_scent_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_nec_snare_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_nec_snare_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "necromancer snare spell dropped"
    },
    "spell_line_nec_snare_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_nec_twitch_other_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_nec_twitch_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_nec_twitch_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_npc_buff_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "how did you do that?"
    },
    "spell_line_npc_disease_other_cast": {
      "alert": {},
      "reaction": "solo",
      "sound": "disease"
    },
    "spell_line_npc_disease_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_npc_disease_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "disease spell dropped"
    },
    "spell_line_npc_disease_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_npc_fire_you_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_npc_fire_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "fire spell dropped"
    },
    "spell_line_npc_item_poison_other_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_npc_port_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_npc_root_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_npc_sick_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_npc_thunder_other_cast": {
      "alert": {},
      "reaction": "solo",
      "sound": "thunder"
    },
    "spell_line_npc_thunder_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_pacify_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_pacify_undead_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_pacify_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_paralyzing_poison_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_paralyzing_poison_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_peace_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_pet_haste_or_rabies_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_poison_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_poison_resist_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_poison_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "poison spell dropped"
    },
    "spell_line_poison_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_portal_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_potion_ds_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_potion_ds_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "potion damage shield dropped"
    },
    "spell_line_potion_ds_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_potion_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_potion_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "potion effect has worn off"
    },
    "spell_line_potion_you_on": {
      "alert": {},
      "reaction": "solo",
      "sound": "cheers"
    },
    "spell_line_protection_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "protection spell dropped"
    },
    "spell_line_protection_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_raid_ae_other_cast": {
      "alert": {},
      "reaction": "raid",
      "sound": "a.e."
    },
    "spell_line_raid_silence_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_raid_silence_you_on": {
      "alert": {},
      "reaction": "raid",
      "sound": "silence"
    },
    "spell_line_regen_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_regen_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "regeneration spell dropped"
    },
    "spell_line_regen_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_rng_aggro_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_rng_aggro_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_root_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_root_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "root spell dropped"
    },
    "spell_line_root_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_rune_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_rune_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "rune spell dropped"
    },
    "spell_line_rune_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_scarab_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_see_invis_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_see_invis_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "see invis dropped"
    },
    "spell_line_see_invis_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_shm_dis_dd_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_shm_dis_dd_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_shm_dr_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "shaman disease resist spell dropped"
    },
    "spell_line_shm_hp_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_shm_hp_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "shaman HP buff spell dropped"
    },
    "spell_line_shm_hp_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_shm_insidious_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_shm_pet_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_shm_poison_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_shm_poison_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_shm_sta_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_shm_sta_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "shaman stamina spell dropped"
    },
    "spell_line_shm_str_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_shrink_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_shrink_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "did i get taller?"
    },
    "spell_line_shrink_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_siphon_strength_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_siphon_strength_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "siphon strength spell dropped"
    },
    "spell_line_siphon_strength_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_skin_freeze_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_skin_freeze_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_skin_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "skin spell dropped"
    },
    "spell_line_slow_other_on": {
      "alert": {},
      "reaction": "solo",
      "sound": "slow"
    },
    "spell_line_slow_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "slow spell dropped"
    },
    "spell_line_slow_you_on": {
      "alert": {},
      "reaction": "solo",
      "sound": "slow"
    },
    "spell_line_snare_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_snare_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_spin_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_spin_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "spin spell dropped"
    },
    "spell_line_spin_you_on": {
      "alert": {},
      "reaction": "solo",
      "sound": "like a record"
    },
    "spell_line_stagger_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_strength_burst_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "strength burst spell dropped"
    },
    "spell_line_strength_debuff_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_strength_debuff_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "strength debuff spell dropped"
    },
    "spell_line_strength_debuff_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_strength_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_strength_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "strength spell dropped"
    },
    "spell_line_strength_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_stun_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_stun_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "stun spell dropped"
    },
    "spell_line_stun_you_on": {
      "alert": {},
      "reaction": "solo",
      "sound": "stunned"
    },
    "spell_line_swarm_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_swarm_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "swarm spell dropped"
    },
    "spell_line_swarms_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_system_shock_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_target_vision_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_target_vision_you_off": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_target_vision_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_tash_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_tash_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "tash spell dropped"
    },
    "spell_line_tash_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_ultravision_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_ultravision_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "ultravision spell dropped"
    },
    "spell_line_wince_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_wiz_alkabor_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_wiz_alkabor_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_wiz_ds_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_wiz_ds_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "wizard damage shield dropped"
    },
    "spell_line_wiz_ds_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_wiz_ice_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_wiz_ice_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_wiz_plane_port_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_wolf_form_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_wolf_form_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "wolf form spell dropped"
    },
    "spell_line_wolf_form_you_on": {
      "alert": {},
      "reaction": "solo_only",
      "sound": "woof"
    },
    "spell_line_word_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_word_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_yaulp_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_line_yaulp_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_locate_corpse_you_off": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_lower_resists_i_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_lull_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_lure_of_flame_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_lure_of_flame_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_lure_of_frost_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_lure_of_frost_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_lure_of_ice_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_lure_of_ice_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_lure_of_lightning_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_lure_of_lightning_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_lyssas_cataloging_libretto_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_lyssas_locating_lyric_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_lyssas_locating_lyric_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_lyssas_solidarity_of_vision_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_lyssas_solidarity_of_vision_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_lyssas_veracious_concord_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "see invis dropped"
    },
    "spell_lyssas_veracious_concord_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_magi_curse_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_magi_curse_you_on": {
      "alert": {},
      "reaction": "solo",
      "sound": "stun more"
    },
    "spell_malevolent_grasp_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_malevolent_grasp_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "malevolent grasp dropped"
    },
    "spell_malevolent_grasp_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_mana_conversion_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_mana_flare_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_mana_flare_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "mana flare dropped"
    },
    "spell_mana_flare_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_mana_sieve_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_mana_sieve_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_mana_sink_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_manasink_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_manasink_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_manaskin_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_manaskin_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_manastorm_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_manastorm_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_maniacal_strength_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_maniacal_strength_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_manifest_elements_other_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_manifest_elements_you_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_manticore_poison_other_cast": {
      "alert": {},
      "reaction": "solo",
      "sound": "manticore poison"
    },
    "spell_mark_of_karn_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_mark_of_karn_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_mask_of_the_hunter_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_mask_of_the_hunter_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "mask of the hunter dropped"
    },
    "spell_mask_of_the_hunter_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_mcvaxius_berserker_crescendo_you_off": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_mcvaxius_rousing_rondo_you_off": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_mcvaxius_rousing_rondo_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_melanies_mellifluous_motion_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_melanies_mellifluous_motion_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "melanies mellifluous motion dropped"
    },
    "spell_melanies_mellifluous_motion_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_melody_of_ervaj_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "melody of ervaj dropped"
    },
    "spell_mesmerizing_breath_other_cast": {
      "alert": {},
      "reaction": "raid",
      "sound": "silence"
    },
    "spell_mesmerizing_breath_you_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_mind_cloud_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_mind_cloud_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "mind cloud dropped"
    },
    "spell_mind_cloud_you_on": {
      "alert": {},
      "reaction": "solo",
      "sound": "mind cloud"
    },
    "spell_minor_healing_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_minor_healing_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_minor_shielding_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_mistwalker_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_mistwalker_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_modulation_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_modulation_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_mortal_deftness_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_mortal_deftness_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "mortal deftness"
    },
    "spell_mortal_deftness_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_mystic_precision_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_mystic_precision_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "mystic precision dropped"
    },
    "spell_mystic_precision_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_naltrons_mark_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_naltrons_mark_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "naltrons mark dropped"
    },
    "spell_naltrons_mark_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_nature_walkers_behest_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_nature_walkers_behest_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_natures_holy_wrath_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_natures_holy_wrath_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_natures_melody_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_natures_melody_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_natures_wrath_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_natures_wrath_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_nillipus_march_of_the_wee_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_nillipus_march_of_the_wee_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_nimble_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_nimble_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_nivs_harmonic_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "nivs harmonic dropped"
    },
    "spell_nivs_harmonic_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_nivs_melody_of_preservation_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_nullify_magic_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_nullify_magic_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_numbing_cold_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_numbing_cold_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_obscure_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_obscure_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_occlusion_of_sound_other_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_occlusion_of_sound_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_occlusion_of_sound_you_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_one_hundred_blows_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_one_hundred_blows_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "one hundred blows dropped"
    },
    "spell_one_hundred_blows_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_open_black_box_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_open_black_box_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_overwhelming_splendor_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_overwhelming_splendor_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_panic_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_panic_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_phantom_armor_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_phantom_armor_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_phantom_chain_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_phantom_chain_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_phantom_leather_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_phantom_leather_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_phantom_plate_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_phantom_plate_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_pillar_of_frost_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_pillar_of_frost_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_pillar_of_lightning_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_pillar_of_lightning_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_plagueratdisease_other_cast": {
      "alert": {},
      "reaction": "solo",
      "sound": "rat disease"
    },
    "spell_plainsight_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "plainsight dropped"
    },
    "spell_pogonip_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_pogonip_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_poison_breath_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_poisonous_chill_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_poisonous_chill_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_porlos_fury_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_porlos_fury_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_power_of_the_forests_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_power_of_the_forests_you_on": {
      "alert": {},
      "reaction": "raid",
      "sound": "tunare nuked you"
    },
    "spell_pox_of_bertoxxulous_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_pox_of_bertoxxulous_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "pox of bertoxxulous dropped"
    },
    "spell_pox_of_bertoxxulous_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_primal_essence_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_primal_essence_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "primal essence dropped"
    },
    "spell_primal_essence_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_prime_healers_blessing_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_prime_healers_blessing_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "prime healers blessing dropped"
    },
    "spell_prime_healers_blessing_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_project_lightning_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_project_lightning_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_protect_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_protect_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_purifying_rhythms_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_putrefy_flesh_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_putrefy_flesh_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_putrid_breath_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_quivering_veil_of_xarn_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_quivering_veil_of_xarn_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_radiant_visage_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_radiant_visage_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "radiant visage dropped"
    },
    "spell_radiant_visage_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_rage_of_tallon_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_rage_of_tallon_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "rage of tallon dropped"
    },
    "spell_rage_of_tallon_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_rage_of_vallon_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_rage_of_vallon_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "rage of vallon dropped"
    },
    "spell_rage_of_vallon_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_rage_of_zek_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_rage_of_zek_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "rage of zek dropped"
    },
    "spell_rage_of_zek_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_rage_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_rage_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "rage dropped"
    },
    "spell_rage_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_rain_of_molten_lava_you_on": {
      "alert": {},
      "reaction": "raid",
      "sound": "rain of molten lava"
    },
    "spell_rapture_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_rapture_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "rapture dropped"
    },
    "spell_rapture_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_recant_magic_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_recant_magic_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_reckless_health_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_reckless_health_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "reckless health dropped"
    },
    "spell_reckless_health_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_reckless_strength_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_reckless_strength_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_reckoning_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_reckoning_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_reclaim_energy_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_reclaim_energy_you_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_remedy_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_remedy_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_rend_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_rend_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_renew_elements_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_renew_summoning_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_resist_cold_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_resist_cold_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "resist cold dropped"
    },
    "spell_resist_cold_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_resist_disease_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_resist_disease_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "resist disease dropped"
    },
    "spell_resist_disease_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_resist_fire_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_resist_fire_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "resist fire dropped"
    },
    "spell_resist_fire_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_resist_magic_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "resist magic dropped"
    },
    "spell_resist_magic_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_resist_poison_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_resist_poison_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "resist poison dropped"
    },
    "spell_resist_poison_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_resistant_skin_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_resistant_skin_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "resistant skin dropped"
    },
    "spell_resistant_skin_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_resolution_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_resolution_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "resolution dropped"
    },
    "spell_resolution_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_resurrection_effects_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_retribution_of_alkabor_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_retribution_of_alkabor_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_retribution_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_retribution_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_riotous_health_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_riotous_health_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_rotting_flesh_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_rubicite_aura_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_rubicite_aura_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "rubicite aura dropped"
    },
    "spell_rubicite_aura_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_rune_i_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_rune_ii_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_rune_iii_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_savage_spirit_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_savage_spirit_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "savage spirit dropped"
    },
    "spell_savage_spirit_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_scale_of_wolf_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "scale of wolf dropped"
    },
    "spell_scale_skin_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_scale_skin_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "scale skin dropped"
    },
    "spell_scale_skin_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_scarab_storm_other_cast": {
      "alert": {},
      "reaction": "solo",
      "sound": "scarab storm"
    },
    "spell_scarab_storm_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "scarab storm dropped"
    },
    "spell_scarab_storm_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_scars_of_sigil_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_scars_of_sigil_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_scent_of_darkness_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "scent of darkness dropped"
    },
    "spell_scent_of_darkness_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_scent_of_dusk_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_scent_of_dusk_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "scent of dusk dropped"
    },
    "spell_scent_of_dusk_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_scent_of_shadow_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_scent_of_shadow_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "scent of shadow dropped"
    },
    "spell_scent_of_shadow_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_scent_of_terris_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "scent of terris dropped"
    },
    "spell_scent_of_terris_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_scintillation_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_scintillation_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_scoriae_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_scoriae_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_screaming_mace_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_screaming_terror_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_screaming_terror_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "screaming terror dropped"
    },
    "spell_screaming_terror_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_sear_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "sear dropped"
    },
    "spell_sear_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_seeking_flame_of_seukor_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_seeking_flame_of_seukor_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_seething_fury_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_seething_fury_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "seething fury dropped"
    },
    "spell_seething_fury_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_selos_accelerando_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_selos_assonant_strane_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_selos_assonant_strane_you_off": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_selos_assonant_strane_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_selos_chords_of_cessation_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_selos_chords_of_cessation_you_off": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_selos_chords_of_cessation_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_selos_consonant_chain_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_selos_consonant_chain_you_off": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_selos_consonant_chain_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_selos_song_of_travel_you_off": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_selos_song_of_travel_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_sentinel_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shade_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shade_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shadow_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shadow_sight_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "shadow sight dropped"
    },
    "spell_shadow_sight_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shadow_vortex_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shadow_vortex_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "shadow vortex dropped"
    },
    "spell_shadow_vortex_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shadow_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shadowbond_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "shadowbond dropped"
    },
    "spell_shards_of_sorrow_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shards_of_sorrow_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shauris_sonorous_clouding_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "shauris sonorous clouding dropped"
    },
    "spell_shauris_sonorous_clouding_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shield_of_blades_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shield_of_blades_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "shield of blades dropped"
    },
    "spell_shield_of_blades_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shield_of_song_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shield_of_song_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shield_of_the_magi_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "shield of the magi dropped"
    },
    "spell_shieldskin_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shieldskin_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shifting_shield_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shifting_shield_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "shifting shield dropped"
    },
    "spell_shifting_shield_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shifting_sight_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "shifting sight dropped"
    },
    "spell_shifting_sight_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shock_of_lightning_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shock_of_lightning_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shock_of_poison_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shock_of_poison_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shock_of_steel_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shock_of_steel_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shock_spiral_of_alkabor_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shock_spiral_of_alkabor_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shrieking_howl_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shrieking_howl_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shroud_of_death_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shroud_of_death_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shroud_of_hate_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shroud_of_hate_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "shroud of hate dropped"
    },
    "spell_shroud_of_hate_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shroud_of_pain_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shroud_of_pain_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "shroud of pain dropped"
    },
    "spell_shroud_of_pain_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shroud_of_the_spirits_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shroud_of_the_spirits_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "shroud of the spirits dropped"
    },
    "spell_shroud_of_the_spirits_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shroud_of_undeath_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_shroud_of_undeath_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_silver_skin_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_silver_skin_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "silver skin dropped"
    },
    "spell_silver_skin_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_sirocco_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_sirocco_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_skin_like_diamond_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_skin_like_diamond_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_skin_like_nature_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_skin_like_nature_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_skin_like_rock_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_skin_like_rock_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_skin_like_steel_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_skin_like_steel_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_skin_like_wood_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_skin_like_wood_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_skin_of_the_shadow_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_skin_of_the_shadow_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_skunkspray_other_cast": {
      "alert": {},
      "reaction": "solo",
      "sound": "skunk spray"
    },
    "spell_skunkspray_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_skunkspray_you_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_skunkspray_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "you smell a bit better now"
    },
    "spell_skunkspray_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_slime_mist_other_cast": {
      "alert": {},
      "reaction": "solo",
      "sound": "slime mist"
    },
    "spell_slime_mist_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_smite_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_smite_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_smolder_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_smolder_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_snakeelefireburst_other_cast": {
      "alert": {},
      "reaction": "solo",
      "sound": "snake fire"
    },
    "spell_solons_bewitching_bravura_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_solons_song_of_the_sirens_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_song_of_dawn_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_song_of_dawn_you_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_song_of_midnight_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_song_of_midnight_you_off": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_song_of_midnight_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_song_of_the_deep_seas_you_off": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_song_of_the_deep_seas_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_song_of_twilight_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_song_of_twilight_you_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_song_of_twilight_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_soul_devour_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_soul_devour_you_on": {
      "alert": {},
      "reaction": "solo",
      "sound": "soul devour"
    },
    "spell_soul_leech_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_speed_of_the_shissar_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_speed_of_the_shissar_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "speed of the shissar dropped"
    },
    "spell_speed_of_the_shissar_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_spikecoat_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_spikecoat_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_spin_the_bottle_other_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_spirit_armor_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_spirit_armor_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "spirit armor dropped"
    },
    "spell_spirit_armor_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_spirit_of_bear_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_spirit_of_bear_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "spirit of bear dropped"
    },
    "spell_spirit_of_bear_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_spirit_of_cat_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "spirit of cat dropped"
    },
    "spell_spirit_of_cat_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_spirit_of_cheetah_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "spirit of cheetah dropped"
    },
    "spell_spirit_of_cheetah_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_spirit_of_monkey_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_spirit_of_monkey_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "spirit of monkey dropped"
    },
    "spell_spirit_of_monkey_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_spirit_of_ox_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_spirit_of_ox_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "spirit of ox dropped"
    },
    "spell_spirit_of_ox_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_spirit_of_scale_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "spirit of scale dropped"
    },
    "spell_spirit_of_snake_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_spirit_of_snake_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "spirit of snake dropped"
    },
    "spell_spirit_of_snake_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_spirit_of_the_howler_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_spirit_of_the_howler_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_spirit_of_wolf_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_spirit_of_wolf_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "spirit of wolf dropped"
    },
    "spell_spirit_of_wolf_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_splurt_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_splurt_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "splurt dropped"
    },
    "spell_splurt_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_stalking_probe_you_off": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_stalwart_regeneration_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_stalwart_regeneration_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_stamina_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "stamina dropped"
    },
    "spell_stamina_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_starfire_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_starfire_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_starshine_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_starshine_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_static_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_static_strike_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_static_strike_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_static_you_on": {
      "alert": {},
      "reaction": "group",
      "sound": "static"
    },
    "spell_steam_overload_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_steam_overload_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "steam overload dropped"
    },
    "spell_steam_overload_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_steelskin_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_steelskin_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_stone_breath_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_stone_breath_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_stream_of_acid_other_cast": {
      "alert": {},
      "reaction": "raid",
      "sound": "stream of acid"
    },
    "spell_stream_of_acid_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_stream_of_acid_you_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_stream_of_acid_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_strength_of_nature_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_strength_of_nature_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "strength of nature dropped"
    },
    "spell_strength_of_nature_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_strength_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_strike_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_strike_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_stun_breath_other_cast": {
      "alert": {},
      "reaction": "raid",
      "sound": "stun breath"
    },
    "spell_stun_breath_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_stun_breath_you_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_stun_breath_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_stunning_blow_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_stunning_blow_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_suffocating_sphere_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_suffocating_sphere_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "suffocating sphere dropped"
    },
    "spell_suffocating_sphere_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_summon_companion_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_summon_companion_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_summon_orb_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_summon_orb_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_summon_wisp_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_summon_wisp_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_sunbeam_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_sunbeam_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_sunstrike_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_sunstrike_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_swarm_of_retribution_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_swarm_of_retribution_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_swarming_pain_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_swarming_pain_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_sympathetic_aura_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_sympathetic_aura_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "sympathetic aura dropped"
    },
    "spell_sympathetic_aura_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_symphonic_harmony_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_system_shock_i_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_system_shock_v_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_syvelians_antimagic_aria_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_tainted_breath_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "tainted breath dropped"
    },
    "spell_talisman_of_jasinth_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_talisman_of_jasinth_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_talisman_of_shadoo_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_talisman_of_shadoo_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_talisman_of_the_brute_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "talisman of the brute dropped"
    },
    "spell_talisman_of_the_brute_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_talisman_of_the_cat_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "meow"
    },
    "spell_talisman_of_the_cat_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_talisman_of_the_raptor_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "talisman of the raptor dropped"
    },
    "spell_talisman_of_the_raptor_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_talisman_of_the_rhino_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "talisman of the rhino dropped"
    },
    "spell_talisman_of_the_rhino_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_talisman_of_the_serpent_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "talisman of the serpent dropped"
    },
    "spell_talisman_of_the_serpent_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_taper_enchantment_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_taper_enchantment_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_tarews_aquatic_ayre_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "tarews aquatic ayre dropped"
    },
    "spell_tarews_aquatic_ayre_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_tashan_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_tears_of_druzzil_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_tears_of_druzzil_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_tears_of_solusek_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_tears_of_solusek_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_telescope_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_telescope_you_off": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_telescope_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_the_dains_justice_other_on": {
      "alert": {},
      "reaction": "raid",
      "sound": "teleport"
    },
    "spell_the_dains_justice_you_on": {
      "alert": {},
      "reaction": "raid",
      "sound": "teleport"
    },
    "spell_the_unspoken_word_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_the_unspoken_word_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "the unspoken word dropped"
    },
    "spell_the_unspoken_word_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_theft_of_thought_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_thistlecoat_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_thistlecoat_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_thorncoat_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_thorncoat_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_thunder_strike_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_thunder_strike_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_thunderbold_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_thunderbold_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_thunderclap_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_thunderclap_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_torbas_acid_blast_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_torbas_acid_blast_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_torment_of_argli_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_torment_of_argli_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_torment_of_shadows_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_torment_of_shadows_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "torment of shadows dropped"
    },
    "spell_torment_of_shadows_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_torment_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_torment_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "torment dropped"
    },
    "spell_torment_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_torpor_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_torpor_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "torpor dropped"
    },
    "spell_torpor_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_torrent_of_poison_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_torrent_of_poison_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_touch_of_night_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_track_corpse_you_off": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_travelerboots_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_travelerboots_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "journeyman boots dropped"
    },
    "spell_travelerboots_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_tremor_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_trepidation_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_trepidation_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "trepidation dropped"
    },
    "spell_trepidation_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_true_north_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_tsunami_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_turning_of_the_unnatural_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_turning_of_the_unnatural_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "turning of the unnatural dropped"
    },
    "spell_turning_of_the_unnatural_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_umbra_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_umbra_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_unfailing_reverence_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_unfailing_reverence_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_upheaval_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_upheaval_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_valiant_companion_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_valor_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_valor_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "valor dropped"
    },
    "spell_valor_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_vengeance_of_alkabor_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_vengeance_of_alkabor_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_vengeance_of_the_glades_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_verlekarnorms_disaster_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_verlekarnorms_disaster_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_vexing_mordinia_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_vexing_mordinia_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "vexing mordinia dropped"
    },
    "spell_vexing_mordinia_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_vigilant_spirit_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_visions_of_grandeur_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_visions_of_grandeur_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "visions of the grandeur dropped"
    },
    "spell_visions_of_grandeur_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_voice_graft_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_voice_of_the_berserker_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_wake_of_karana_other_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_wake_of_karana_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_wandering_mind_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_wandering_mind_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "wandering mind dropped"
    },
    "spell_wandering_mind_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_wave_of_cold_you_on": {
      "alert": {},
      "reaction": "raid",
      "sound": "wave of cold"
    },
    "spell_wave_of_fire_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_wave_of_fire_you_on": {
      "alert": {},
      "reaction": "raid",
      "sound": "wave of fire"
    },
    "spell_wave_of_flame_other_cast": {
      "alert": {},
      "reaction": "raid",
      "sound": "wave of flame"
    },
    "spell_wave_of_flame_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_wave_of_healing_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_wave_of_healing_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_wave_of_heat_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_wave_of_heat_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_waves_of_the_deep_sea_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_whirlwind_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_whirlwind_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_wildfire_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_wildfire_you_on": {
      "alert": {},
      "reaction": "solo",
      "sound": "the druids are clearly upset"
    },
    "spell_winds_of_gelid_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_winds_of_gelid_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_winged_death_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_winged_death_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_wonderous_rapidity_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_wonderous_rapidity_you_on": {
      "alert": {},
      "reaction": "solo",
      "sound": "gotta go fast"
    },
    "spell_word_of_redemption:_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_word_of_redemption:_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_word_of_restoration_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_word_of_restoration_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_word_of_vigor_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_word_of_vigor_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_wrath_of_nature_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_wrath_of_nature_you_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "wrath of nature dropped"
    },
    "spell_wrath_of_nature_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_wrath_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_wrath_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_ykesha_other_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_ykesha_you_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
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
    },
    "tell_npc_bank_closed": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "tell_npc_bank_open": {
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
    "auction_unknown_tongue": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "broadcast": {
      "alert": {},
      "reaction": "solo",
      "sound": "true"
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
        "bump": "raid",
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
    "say_unknown_tongue": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "shout": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "shout_unknown_tongue": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "tell": {
      "alert": {},
      "reaction": "solo",
      "sound": "true"
    },
    "tell_unknown_tongue": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
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
    "petition_you": {
      "alert": {},
      "reaction": "solo",
      "sound": "fingers crossed"
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
    "account_subscription": {
      "alert": {},
      "reaction": "solo",
      "sound": "the secret ingredient is crime"
    },
    "birthdate": {
      "alert": {},
      "reaction": "solo",
      "sound": "ah, the memories"
    },
    "client_ui_load": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "corpse_consent": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
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
    "command_block_moving": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "command_block_spellbook": {
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
    "drink_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "drink_you_finish": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "eat_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "eat_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "eat_you_finish": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "eat_you_full": {
      "alert": {},
      "reaction": "solo",
      "sound": "I'm stuffed!"
    },
    "friend_add": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "friend_empty": {
      "alert": {},
      "reaction": "solo",
      "sound": "It's OK! I'll be your friend!"
    },
    "friend_list_header": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "friend_list_line": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "friend_list_total": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "friend_remove": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "forage_attacking": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "forage_cursor_empty": {
      "alert": {},
      "reaction": "solo",
      "sound": "remove items from cursor"
    },
    "forage_edible": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "forage_fail": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "forage_not_edible": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "forage_standing": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "help_command_chat": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "help_command_emote": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "help_command_format": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "help_command_guild": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "help_command_header": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "help_command_line": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "help_command_normal": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "help_command_output": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "help_command_voice": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "hide_corpse_all": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "hide_corpse_looted": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "hide_corpse_none": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "ignore_add": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "ignore_list_header": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "inspect_toggle_off": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "inspect_toggle_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "list_added": {
      "alert": {},
      "reaction": "solo",
      "sound": "good luck"
    },
    "list_leaving": {
      "alert": {},
      "reaction": "solo",
      "sound": "leaving list area"
    },
    "list_leaving_zone": {
      "alert": {},
      "reaction": "solo",
      "sound": "Toto, I have a feeling we're not in Kansas anymore."
    },
    "list_none": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "list_out_of_range": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "list_position": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "list_removed_range": {
      "alert": {},
      "reaction": "solo",
      "sound": "removed from list"
    },
    "list_re_entered": {
      "alert": {},
      "reaction": "solo",
      "sound": "back in list area"
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
    "played_session": {
      "alert": {},
      "reaction": "solo",
      "sound": "false"
    },
    "played_total": {
      "alert": {},
      "reaction": "solo",
      "sound": "false"
    },
    "random": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "reply_empty": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "server_message": {
      "alert": {},
      "reaction": "all",
      "sound": "true"
    },
    "skill_max": {
      "alert": {},
      "reaction": "solo",
      "sound": "the power!"
    },
    "skill_max_tradeskill": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "skill_up": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "summon_corpse": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "summon_corpse_no_consent": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "summon_corpse_none": {
      "alert": {},
      "reaction": "solo",
      "sound": "well thats a good thing, right?"
    },
    "summon_corpse_too_far": {
      "alert": {},
      "reaction": "solo",
      "sound": "too far"
    },
    "target": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "target_command_format": {
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
    "you_camping_standing": {
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
    "achievement_first": {
      "alert": {},
      "reaction": "solo",
      "sound": "true"
    },
    "anon_off": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "anon_on": {
      "alert": {},
      "reaction": "raid",
      "sound": "you must be up to no good!"
    },
    "assist_self": {
      "alert": {},
      "reaction": "solo",
      "sound": "wrong target"
    },
    "assist_no_target": {
      "alert": {},
      "reaction": "solo",
      "sound": "no target"
    },
    "attack_self": {
      "alert": {},
      "reaction": "solo",
      "sound": "stop hitting yourself"
    },
    "auto_inventory_full": {
      "alert": {},
      "reaction": "solo",
      "sound": "inventory full"
    },
    "autofollow_advice": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "autofollow_no_target": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "autofollow_off": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "autofollow_on": {
      "alert": {},
      "reaction": "solo",
      "sound": "onward my steed"
    },
    "bandage_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "bandage_cap": {
      "alert": {},
      "reaction": "solo",
      "sound": "bandage cap"
    },
    "boat_operator": {
      "alert": {},
      "reaction": "solo",
      "sound": "aye, aye, captain!"
    },
    "cast_animal_only": {
      "alert": {},
      "reaction": "solo",
      "sound": "true"
    },
    "cast_change_form_block": {
      "alert": {},
      "reaction": "solo",
      "sound": "I can't do that here"
    },
    "cast_night_only": {
      "alert": {},
      "reaction": "solo",
      "sound": "true"
    },
    "cast_outdoors_only": {
      "alert": {},
      "reaction": "solo",
      "sound": "true"
    },
    "chat_disconnected": {
      "alert": {},
      "reaction": "solo",
      "sound": "chat disconnected"
    },
    "command_error": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "command_usage": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "concious_you": {
      "alert": {},
      "reaction": "solo",
      "sound": "you got this!"
    },
    "consider": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "consider_dead": {
      "alert": {},
      "reaction": "solo",
      "sound": "she's dead, jim"
    },
    "consider_no_target": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "container_container": {
      "alert": {},
      "reaction": "solo",
      "sound": "It's bigger on the inside"
    },
    "corpse_decay_timer": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "corpse_res_timer": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "corpse_too_old": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "dead_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "dead_you": {
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
    "drag_permission_received": {
      "alert": {},
      "reaction": "solo",
      "sound": "true"
    },
    "duel_accept_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "duel_challenge": {
      "alert": {},
      "reaction": "solo",
      "sound": "Now witness the firepower of this fully ARMED and OPERATIONAL battle station!"
    },
    "duel_end_fled": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "earthquake": {
      "alert": {},
      "reaction": "solo",
      "sound": "earthquake!"
    },
    "effect_removal_block": {
      "alert": {},
      "reaction": "solo",
      "sound": "I'm sorry, Dave. I'm afraid I can't do that."
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
    "equip_block": {
      "alert": {},
      "reaction": "solo",
      "sound": "I can't wear that"
    },
    "faction_line": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "fall_damage_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "fall_damage_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "feign_failure_other": {
      "alert": {},
      "reaction": "solo",
      "sound": "true"
    },
    "fishing_cast": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "fishing_caught_nothing": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "fishing_caught_something": {
      "alert": {},
      "reaction": "solo",
      "sound": "yay"
    },
    "fishing_creatively": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "fishing_holding": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "fishing_lost_bait": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "fishing_no_pole": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "fishing_no_water": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "fishing_pole_broke": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "fishing_spill_beer": {
      "alert": {},
      "reaction": "solo",
      "sound": "not again!"
    },
    "gm_reset_ability": {
      "alert": {},
      "reaction": "solo",
      "sound": "Abilities reset"
    },
    "gm_reset_discipline": {
      "alert": {},
      "reaction": "solo",
      "sound": "Disciplines reset"
    },
    "hide_attacking": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "hide_disabled": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "hide_drop": {
      "alert": {},
      "reaction": "solo",
      "sound": "hide drop"
    },
    "hide_enabled": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "hide_moving": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "item_too_big": {
      "alert": {},
      "reaction": "solo",
      "sound": "thats too big"
    },
    "inspect_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "inspect_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "item_dropped": {
      "alert": {},
      "reaction": "solo",
      "sound": "item dropped"
    },
    "item_dropped_no_room": {
      "alert": {},
      "reaction": "solo",
      "sound": "item dropped"
    },
    "item_must_equip": {
      "alert": {},
      "reaction": "solo",
      "sound": "must equip"
    },
    "item_no_drop": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "jump_fatigue": {
      "alert": {},
      "reaction": "solo",
      "sound": "no stamina"
    },
    "lore_pickup": {
      "alert": {},
      "reaction": "solo",
      "sound": "I already have this"
    },
    "npc_guild_wrong": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "motd_welcome": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "required_pick": {
      "alert": {},
      "reaction": "solo",
      "sound": "let me in!"
    },
    "rewind_output": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "rewind_output_wait": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "roleplay_off": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "roleplay_on": {
      "alert": {},
      "reaction": "solo",
      "sound": "bravo six, going dark"
    },
    "target_attack_sitting": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "target_attack_too_far": {
      "alert": {},
      "reaction": "solo",
      "sound": "too far"
    },
    "target_cannot_see": {
      "alert": {},
      "reaction": "solo",
      "sound": "can't see"
    },
    "target_group_member": {
      "alert": {},
      "reaction": "solo",
      "sound": "target group member"
    },
    "target_lost": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "tell_offline": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "tell_yourself": {
      "alert": {},
      "reaction": "solo",
      "sound": "true"
    },
    "tell_queued_offline": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "titanium_client_help_message": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "too_many_pets": {
      "alert": {},
      "reaction": "solo",
      "sound": "You already have a pet"
    },
    "tracking": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "tracking_begin": {
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
    "tracking_target_lost": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "use_block": {
      "alert": {},
      "reaction": "solo",
      "sound": "I can't use that"
    },
    "walk_of_shame": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "warrior_berserk_off": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "warrior_berserk_on": {
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
    "yell_help": {
      "alert": {},
      "reaction": "solo",
      "sound": "help"
    },
    "yell_help_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
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
    "you_lowdrink": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_lowfood": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_lowfoodlowdrink": {
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
    "group_alone": {
      "alert": {},
      "reaction": "solo",
      "sound": "is anyone there?"
    },
    "group_already": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "group_considering": {
      "alert": {},
      "reaction": "solo",
      "sound": "considering"
    },
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
    "group_invite_already": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "group_invite_instruction": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "group_invite_not_lead": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "group_invite_npc": {
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
    "group_invite_yourself": {
      "alert": {},
      "reaction": "solo",
      "sound": "true"
    },
    "group_invite_you_cancel": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "group_join_notify": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "group_join_reject": {
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
    },
    "group_removed_other": {
      "alert": {},
      "reaction": "solo",
      "sound": "true"
    },
    "guild_invite_instructions": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "guild_invite_other_decline": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "guild_member_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "guild_member_other_accept": {
      "alert": {},
      "reaction": "solo",
      "sound": "welcome"
    },
    "guild_member_other_invite": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "guild_member_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "guild_member_you_accept": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "guild_motd_wrong_command": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "guild_officer_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "guild_officer_you": {
      "alert": {},
      "reaction": "solo",
      "sound": "movin on up"
    },
    "guild_remove_fail": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "guild_remove_you": {
      "alert": {},
      "reaction": "solo",
      "sound": "not like this"
    },
    "guild_remove_you_attempt": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "guild_status_instructions": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "guild_status_none": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "guild_status_officer": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "invite_no_target": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    }
  },
  "version": "%s"
}
"""

    new_line_loot_trade_config = """
{
  "line": {
    "loot_corpse_locked": {
      "alert": {},
      "reaction": "solo",
      "sound": "locked"
    },
    "loot_error_corpse": {
      "alert": {},
      "reaction": "solo",
      "sound": "loot error"
    },
    "loot_error_item": {
      "alert": {},
      "reaction": "solo",
      "sound": "loot error"
    },
    "loot_lore": {
      "alert": {},
      "reaction": "solo",
      "sound": "you already have one of those"
    },
    "loot_too_far": {
      "alert": {},
      "reaction": "solo",
      "sound": "too far"
    },
    "loot_wait": {
      "alert": {},
      "reaction": "solo",
      "sound": "can't loot"
    },
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
    "looted_money_you_split": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "split_format": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "split_format_example": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "split_invalid": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "split_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "helping the monks"
    },
    "split_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "split_shared": {
      "alert": {},
      "reaction": "solo",
      "sound": "ka-ching"
    },
    "trade_error": {
      "alert": {},
      "reaction": "solo",
      "sound": "oh no"
    },
    "trade_lore_item": {
      "alert": {},
      "reaction": "solo",
      "sound": "lore item in trade"
    },
    "tradeskill_create_other": {
      "alert": {},
      "reaction": "solo_group_only",
      "sound": "false"
    },
    "tradeskill_create_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "tradeskill_fail_other": {
      "alert": {},
      "reaction": "solo_group_only",
      "sound": "false"
    },
    "tradeskill_fail_you": {
      "alert": {},
      "reaction": "solo_group_only",
      "sound": "womp"
    },
    "tradeskill_hands_full": {
      "alert": {},
      "reaction": "solo",
      "sound": "empty cursor"
    },
    "tradeskill_skill_cap": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "tradeskill_wrong_container": {
      "alert": {},
      "reaction": "solo",
      "sound": "wrong container"
    },
    "trade_cancel_other": {
      "alert": {},
      "reaction": "solo",
      "sound": "nevermind"
    },
    "trade_cancel_you": {
      "alert": {},
      "reaction": "solo",
      "sound": "I am altering the deal"
    },
    "trade_interest": {
      "alert": {},
      "reaction": "solo",
      "sound": "let's trade"
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
    "trade_money_add": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "trade_npc_item_price": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "trade_npc_item_sold": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "trade_npc_payment": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "trade_too_far": {
      "alert": {},
      "reaction": "solo",
      "sound": "too far"
    }
  },
  "version": "%s"
}
"""

    new_line_emotes_config = """
{
  "line": {
    "emote_agree_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
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
    "emote_bird_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_bird_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_bite_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_bite_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_bleed_other": {
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
    "emote_blush_other": {
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
    "emote_burp_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_burp_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_bye_other": {
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
    "emote_chuckle_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_chuckle_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_clap_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_clap_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_comfort_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_comfort_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_congratulate_other": {
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
    "emote_cry_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_cry_you": {
      "alert": {},
      "reaction": "solo",
      "sound": "there there"
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
    "emote_flex_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_flex_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_frown_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_frown_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_gasp_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_gasp_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_giggle_other": {
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
    "emote_grin_other": {
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
    "emote_hug_other": {
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
    "emote_introduce_other": {
      "alert": {},
      "reaction": "all",
      "sound": "why, hello there"
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
    "emote_kiss_other": {
      "alert": {},
      "reaction": "solo",
      "sound": "love is in the air"
    },
    "emote_kiss_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_kneel_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_kneel_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_laugh_other": {
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
    "emote_mourn_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_mourn_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_nod_other": {
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
    "emote_pat_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_pat_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_peer_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_peer_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_plead_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_plead_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_point_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_point_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_poke_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_poke_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_ponder_other": {
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
    "emote_roar_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_roar_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_rofl_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_rofl_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_salute_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_salute_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_shiver_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_shiver_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_shrug_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_shrug_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_sigh_other": {
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
    "emote_smirk_other": {
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
    "emote_tap_other": {
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
    "emote_veto_other": {
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
    "emote_yawn_other": {
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
    "who_etc": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
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
        generated_settings = write_config(
            base_path, "settings", version, new_settings_config
        )
        if generated_settings:
            generated = True

        ## Zones
        generated_zones = write_config(base_path, "zones", version, new_zones_config)
        if generated_zones:
            generated = True

        ## Line Alerts
        ### Combat
        generated_combat = write_config(
            base_path, "line-alerts/combat", version, new_line_combat_config
        )
        if generated_combat:
            generated = True

        ### Spell General
        generated_spells = write_config(
            base_path,
            "line-alerts/spell-general",
            version,
            new_line_spell_general_config,
        )
        if generated_spells:
            generated = True

        ### Spell Specific
        generated_spell = write_config(
            base_path,
            "line-alerts/spell-specific",
            version,
            new_line_spell_specific_config,
        )
        if generated_spell:
            generated = True

        ### Pets
        generated_pets = write_config(
            base_path, "line-alerts/pets", version, new_line_pets_config
        )
        if generated_pets:
            generated = True

        ### Chat Received NPC
        generated_received_npc = write_config(
            base_path,
            "line-alerts/chat-received-npc",
            version,
            new_line_chat_recieved_npc_config,
        )
        if generated_received_npc:
            generated = True

        ### Chat Received
        generated_received = write_config(
            base_path,
            "line-alerts/chat-received",
            version,
            new_line_chat_recieved_config,
        )
        if generated_received:
            generated = True

        ### Chat Sent
        generated_sent = write_config(
            base_path, "line-alerts/chat-sent", version, new_line_chat_sent_config
        )
        if generated_sent:
            generated = True

        ### Command Output
        generated_command = write_config(
            base_path,
            "line-alerts/command-output",
            version,
            new_line_command_output_config,
        )
        if generated_command:
            generated = True

        ### System Messages
        generated_system = write_config(
            base_path,
            "line-alerts/system-messages",
            version,
            new_line_system_messages_config,
        )
        if generated_system:
            generated = True

        ### Group System Messages
        generated_group_system = write_config(
            base_path,
            "line-alerts/group-system-messages",
            version,
            new_line_group_system_messages_config,
        )
        if generated_group_system:
            generated = True

        ### Loot Trade
        generated_loot_trade = write_config(
            base_path, "line-alerts/loot-trade", version, new_line_loot_trade_config
        )
        if generated_loot_trade:
            generated = True

        ### Emotes
        generated_emotes = write_config(
            base_path, "line-alerts/emotes", version, new_line_emotes_config
        )
        if generated_emotes:
            generated = True

        ### Who
        generated_who = write_config(
            base_path, "line-alerts/who", version, new_line_who_config
        )
        if generated_who:
            generated = True

        ### Other
        generated_other = write_config(
            base_path, "line-alerts/other", version, new_line_other_config
        )
        if generated_other:
            generated = True

        return generated

    except Exception as e:
        print(
            "build config: Error on line"
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def write_config(base_path, config_name, version, new_config):
    """Create any missing config files"""
    try:
        # Determine Config Path
        generated = False
        generate_config = False
        line_json_path = base_path + "config/" + config_name + ".json"
        home = os.path.expanduser("~")

        ## If the config does not exist
        if not os.path.isfile(line_json_path):
            f = open(line_json_path, "w", encoding="utf-8")
            if config_name == "settings":
                f.write(
                    new_config
                    % (base_path, base_path, base_path, home, home, base_path, version)
                )
            else:
                f.write(new_config % (version))
            f.close()
            generated = True
        ## If the config exists
        elif os.path.isfile(line_json_path):
            ### Validate file is readable

            old_version = "unknown/"
            generate_config = False
            try:
                json_data = open(line_json_path, "r", encoding="utf-8")
                line_json = json.load(json_data)
                json_data.close()
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
                f = open(line_json_path, "w", encoding="utf-8")
                if config_name == "settings":
                    f.write(
                        new_config
                        % (
                            base_path,
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
                f.close()
                generated = True

        return generated

    except Exception as e:
        print(
            "write config line alert: Error on line"
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


if __name__ == "__main__":
    main()
