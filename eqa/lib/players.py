#! /usr/bin/env python

"""
   Program:   EQ Alert
   File Name: eqa/lib/players.py
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
import re

import eqa.lib.settings as eqa_settings
import eqa.lib.struct as eqa_struct


def process(state, configs, player_list, player_q, exit_flag, cfg_reload):
    """
    Process: player_q
    Produce: player_list
    """

    try:
        # Read in players.json
        base_path = configs.settings.config["settings"]["paths"]["data"]
        player_data_file = base_path + "players.json"
        json_data = open(player_data_file, "r", encoding="utf-8")
        player_json_data = json.load(json_data)
        json_data.close()

        if state.server not in player_json_data["servers"].keys():
            player_json_data["servers"][state.server] = {"players": {}}

        player_list = player_json_data["servers"][state.server]["players"]

        # Watch player_q
        while not exit_flag.is_set() and not cfg_reload.is_set():
            # Sleep between empty checks
            queue_size = player_q.qsize()
            if queue_size < 1:
                time.sleep(0.01)

            # Check queue for message
            if not player_q.empty():
                ## Read new message
                new_message = player_q.get()
                who_player = new_message.payload

                char_level = "0"
                char_class = "unknown"
                char_guild = "none"

                # Parse who_player to determine name, level, guild
                if re.findall(r"\d+ [a-zA-Z\s]+", line) is not None:
                    char_level, char_class = re.findall(r"\d+ [a-zA-Z\s]+", line)[
                        0
                    ].split(" ", 1)

                if re.fullmatch(r".+\<[a-zA-Z\s]+\>(.+|)", line) is not None:
                    char_guild = re.findall(r"(?<=\<)[a-zA-Z\s]+", line)[0].lower()

                char_name = re.findall(r"(?<=\]\ )[a-zA-Z]+(?=[\ \(])", line)[0].lower()

                if char_name in player_list.keys():
                    if (
                        char_guild != "none"
                        and char_guild != player_list[char_name]["guild"]
                    ):
                        player_list[char_name]["guild"] = char_guild
                    if (
                        char_level != "0"
                        and char_level != player_list[char_name]["level"]
                    ):
                        player_list[char_name]["level"] = char_level
                    if (
                        char_class != "unknown"
                        and char_class.lower() != player_list[char_name]["class"]
                    ):
                        player_list[char_name]["class"] = char_class.lower()
                else:
                    player_list[char_name] = {
                        "class": char_class.lower(),
                        "level": char_level,
                        "guild": char_guild,
                    }

                player_q.task_done()

        player_json_data["servers"][state.server]["players"] = player_list
        json_data = open(player_data_file, "w", encoding="utf-8")
        json.dump(player_json_data, json_data, sort_keys=True, indent=2)
        json_data.close()

    except Exception as e:
        eqa_settings.log(
            "players_process: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )

    sys.exit()
