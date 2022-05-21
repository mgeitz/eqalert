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
                "group": "false",
                "leader": "false",
                "raid": "false",
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
                "group": str(state.group),
                "leader": str(state.leader),
                "raid": str(state.raid),
            }
        )
        data["settings"]["encounter_parsing"].update(
            {"auto_save": str(state.save_parse), "enabled": str(state.encounter_parse)}
        )
        data["settings"]["raid_mode"].update(
            {
                "auto_set": str(state.auto_raid),
            }
        )
        data["settings"]["timers"].update(
            {
                "auto_mob_timer": str(state.auto_mob_timer),
            }
        )
        data["settings"]["debug_mode"].update({"enabled": str(state.debug)})
        data["settings"]["mute"].update({"enabled": str(state.mute)})
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
        group = data["last_state"]["group"]
        leader = data["last_state"]["leader"]
        raid = data["last_state"]["raid"]

        encounter_parse = data["settings"]["encounter_parsing"]["enabled"]
        debug = data["settings"]["debug_mode"]["enabled"]
        mute = data["settings"]["mute"]["enabled"]
        save_parse = data["settings"]["encounter_parsing"]["auto_save"]
        auto_raid = data["settings"]["raid_mode"]["auto_set"]
        auto_mob_timer = data["settings"]["timers"]["auto_mob_timer"]
        mute = data["settings"]["mute"]["enabled"]

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
        data["zones"].update({str(zone): {"raid_mode": "false", "timer": "0"}})
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
    "auction_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "autofollow_advice": {
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
    "earthquake": {
      "alert": {},
      "reaction": "solo",
      "sound": "earthquake!"
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
    "group_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "guild": {
      "alert": {
        "help": "true",
        "assist": "raid",
        "crippled": "raid",
        "dispelled": "raid",
        "feared": "raid",
        "harmony": "raid",
        "fixated": "raid",
        "fixation": "raid",
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
    "guild_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
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
      "reaction": "false",
      "sound": "false"
    },
    "ooc": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "ooc_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
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
        "help": "true",
        "spot": "raid"
      },
      "reaction": "alert",
      "sound": "look at say"
    },
    "say_npc": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "say_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "server_message": {
      "alert": {},
      "reaction": "all",
      "sound": "true"
    },
    "shout": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "shout_npc": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "shout_you": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
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
    "tell_offline": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
    "tell_you": {
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
    "trade_npc_payment": {
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
    "wrong_key": {
      "alert": {},
      "reaction": "all",
      "sound": "wrong key or place"
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
    "you_thirsty": {
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
    },
    "version": "3.1.3"
  },
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
      "raid_mode": "false",
      "timer": "4320"
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
  }
}
"""

    try:
        f = open(base_path + "config.json", "w", encoding="utf-8")
        f.write(new_config % (base_path, base_path, base_path, home, base_path))
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
