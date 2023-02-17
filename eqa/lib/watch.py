#! /usr/bin/env python

"""
   Program:   EQ Alert
   File Name: eqa/lib/watch.py
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

import sys
import os
import time

import eqa.lib.settings as eqa_settings
import eqa.lib.struct as eqa_struct


def process(state, configs, system_q, exit_flag):
    """
    Process: Watch log directory for most recently modified log file
    Produce: Auto-Swap Characters
    """

    try:
        most_recent = 0.00
        logs_directory = configs.settings.config["settings"]["paths"]["everquest_logs"]

        # Watch log directory
        while not exit_flag.is_set():
            time.sleep(1)

            ## Only check when enabled
            if state.detect_char == "true":
                ### Find newest eqlog_ prefixed file
                for log_file in os.listdir(logs_directory):
                    if log_file.startswith("eqlog_"):
                        modified_time = os.stat(logs_directory + log_file).st_mtime
                        if modified_time > most_recent:
                            most_recent = modified_time
                            game, char, server_dirty = log_file.split("_")
                            server, extension = server_dirty.split(".")

                ### If newest file is a different character, change characters
                if char != state.char or server != state.server:
                    char_server = char + "_" + server
                    system_q.put(
                        eqa_struct.message(
                            eqa_settings.eqa_time(),
                            "system",
                            "new_character",
                            "null",
                            char_server,
                        )
                    )

    except Exception as e:
        eqa_settings.log(
            "watch_process: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )

    sys.exit()
