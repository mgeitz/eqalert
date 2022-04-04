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
                "afk": "false",
                "raid": "false",
                "debug": "false",
                "mute": "false",
                "group": "false",
                "leader": "false",
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
                "server": str(state.server),
                "character": str(state.char),
                "afk": str(state.afk),
                "raid": str(state.raid),
                "debug": str(state.debug),
                "mute": str(state.mute),
                "group": str(state.group),
                "leader": str(state.leader),
            }
        )
        data["char_logs"][state.char + "_" + state.server].update(
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


def get_last_state(base_path, char_name, char_server):
    """Load state from config"""

    try:
        # Read config
        json_data = open(base_path + "config.json", "r", encoding="utf-8")
        data = json.load(json_data)
        json_data.close()

        # Populate State
        server = data["last_state"]["server"]
        char = data["last_state"]["character"]
        zone = data["char_logs"][char_name + "_" + char_server]["char_state"]["zone"]
        location = [
            float(
                data["char_logs"][char_name + "_" + char_server]["char_state"][
                    "location"
                ]["y"]
            ),
            float(
                data["char_logs"][char_name + "_" + char_server]["char_state"][
                    "location"
                ]["x"]
            ),
            float(
                data["char_logs"][char_name + "_" + char_server]["char_state"][
                    "location"
                ]["z"]
            ),
        ]
        direction = data["char_logs"][char_name + "_" + char_server]["char_state"][
            "direction"
        ]
        encumbered = data["char_logs"][char_name + "_" + char_server]["char_state"][
            "encumbered"
        ]
        bind = data["char_logs"][char_name + "_" + char_server]["char_state"]["bind"]
        char_level = data["char_logs"][char_name + "_" + char_server]["char_state"][
            "level"
        ]
        char_class = data["char_logs"][char_name + "_" + char_server]["char_state"][
            "class"
        ]
        char_guild = data["char_logs"][char_name + "_" + char_server]["char_state"][
            "guild"
        ]
        afk = data["last_state"]["afk"]
        raid = data["last_state"]["raid"]
        debug = data["last_state"]["debug"]
        mute = data["last_state"]["mute"]
        group = data["last_state"]["group"]
        leader = data["last_state"]["leader"]

        # Get chars
        chars = get_config_chars(data)

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
        data["zones"].update({str(zone): "false"})
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
      "sound": "false"
    },
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
    "combat_you_stun_off": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "combat_you_stun_on": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "command_block": {
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
    "emote_bonk_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_bow_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_cheer_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_dance_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "emote_smile_other": {
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
    "emote_wave_other": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
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
    "faction_line": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "group": {
      "alert": {
        "invite": "raid",
        "drop": "raid",
        "help": "raid",
        "invis": "raid",
        "inc": "true",
        "oom": "true"
      },
      "reaction": "alert",
      "sound": "look at group"
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
    "group_join_notify": {
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
    "guild": {
      "alert": {
        "help": "true",
        "quake": "group_only",
        "assist": "raid",
        "fixated": "raid",
        "fixation": "raid",
        "incoming": "raid",
        "malo": "raid",
        "malosini": "raid",
        "occlusion": "raid",
        "off-tanking": "raid",
        "rampage": "raid",
        "rune": "raid",
        "slow": "raid",
        "sunder": "raid",
        "tash": "raid"
      },
      "reaction": "alert",
      "sound": "look at guild"
    },
    "location": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
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
      "sound": "out of range"
    },
    "mob_rampage_on": {
      "alert": {},
      "reaction": "group",
      "sound": "rampage"
    },
    "mob_slain_other": {
      "alert": {},
      "reaction": "solo",
      "sound": "true"
    },
    "mob_slain_you": {
      "alert": {},
      "reaction": "solo",
      "sound": "true"
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
    "motd_welcome": {
      "alert": {},
      "reaction": "all",
      "sound": "true"
    },
    "ooc": {
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
    "say": {
      "alert": {
        "help": "true"
      },
      "reaction": "alert",
      "sound": "look at say"
    },
    "say_npc": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "shout": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "skill_up": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "spell_bind_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
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
    "spell_cured_other": {
      "alert": {},
      "reaction": "all",
      "sound": "cured"
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
    "spell_slow_on": {
      "alert": {},
      "reaction": "solo",
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
    },
    "spell_worn_off": {
      "alert": {},
      "reaction": "solo",
      "sound": "true"
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
    "tell": {
      "alert": {},
      "reaction": "solo",
      "sound": "true"
    },
    "tell_npc": {
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
    "undetermined": {
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
    "you_auction": {
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
    "you_group": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_guild": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_hungry": {
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
    },
    "you_new_zone": {
      "alert": {},
      "reaction": "all",
      "sound": "true"
    },
    "you_ooc": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
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
    "you_say": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_shout": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_tell": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "you_thirsty": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "zoning": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    }
  },
  "settings": {
    "paths": {
      "alert_log": "%slog/",
      "char_log": "%s/.wine/drive_c/Program Files/Sony/EverQuest/Logs/",
      "sound": "%ssound/",
      "tmp_sound": "/tmp/eqa/sound/"
    },
    "version": "2.8.19"
  },
  "zones": {
    "An Arena (PVP) Area": "false",
    "Befallen": "false",
    "Blackburrow": "false",
    "Butcherblock Mountains": "false",
    "Castle Mistmoore": "false",
    "Chardok": "false",
    "City of Thurgadin": "false",
    "Cobalt Scar": "false",
    "Crushbone": "false",
    "Crystal Caverns": "false",
    "Dagnor's Cauldron": "false",
    "Dragon Necropolis": "false",
    "Dreadlands": "false",
    "East Commonlands": "false",
    "East Freeport": "false",
    "Eastern Plains of Karana": "false",
    "Eastern Wastelands": "false",
    "Erudin": "false",
    "Erudin Palace": "false",
    "Estate of Unrest": "false",
    "Everfrost": "false",
    "Field of Bone": "false",
    "Firiona Vie": "false",
    "Frontier Mountains": "false",
    "Gorge of King Xorbb": "false",
    "Great Divide": "false",
    "Greater Faydark": "false",
    "Guk": "false",
    "High Keep": "false",
    "Highpass Hold": "false",
    "Howling Stones": "false",
    "Iceclad Ocean": "false",
    "Icewell Keep": "raid",
    "Infected Paw": "false",
    "Innothule Swamp": "false",
    "Kael Drakkel": "raid",
    "Karnor's Castle": "false",
    "Kedge Keep": "false",
    "Kithicor Woods": "false",
    "Kurn's Tower": "false",
    "Lake Rathetear": "false",
    "Lake of Ill Omen": "false",
    "Lavastorm Mountains": "false",
    "Lesser Faydark": "false",
    "Lost Temple of Cazic-Thule": "false",
    "Mines of Nurga": "false",
    "Misty Thicket": "false",
    "Nagafen's Lair": "false",
    "Najena": "false",
    "North Freeport": "false",
    "Northern Desert of Ro": "false",
    "Northern Felwithe": "false",
    "Northern Plains of Karana": "false",
    "Oasis of Marr": "false",
    "Ocean of Tears": "false",
    "Old Sebilis": "false",
    "Paineel": "false",
    "Permafrost Caverns": "false",
    "Plane of Air": "raid",
    "Plane of Fear": "raid",
    "Plane of Growth": "false",
    "Plane of Hate": "raid",
    "Plane of Mischief": "false",
    "Qeynos Hills": "false",
    "Rathe Mountains": "false",
    "Rivervale": "false",
    "Ruins of Old Guk": "false",
    "Sirens Grotto": "false",
    "Skyfire Mountains": "false",
    "Skyshrine": "false",
    "Sleepers Tomb": "raid",
    "South Kaladim": "false",
    "Southern Desert of Ro": "false",
    "Southern Felwithe": "false",
    "Southern Plains of Karana": "false",
    "Steamfont Mountains": "false",
    "Surefall Glade": "false",
    "Temple of Droga": "false",
    "Temple of Solusek Ro": "false",
    "Temple of Veeshan": "raid",
    "The Arena": "false",
    "The Burning Wood": "false",
    "The City of Mist": "false",
    "The Emerald Jungle": "false",
    "The Feerrott": "false",
    "The Hole": "false",
    "The Nektulos Forest": "false",
    "The Overthere": "false",
    "The Wakening Lands": "false",
    "Timorous Deep": "false",
    "Toxxulia Forest": "false",
    "Trakanon's Teeth": "false",
    "Veeshan's Peak": "raid",
    "Velketor's Labyrinth": "false",
    "Warrens": "false",
    "West Commonlands": "false",
    "West Freeport": "false",
    "Western Plains of Karana": "false",
    "Western Wastelands": "false",
    "Western Wastes": "raid"
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
