#! /usr/bin/env python

"""
   Program:   EQ Alert
   File Name: eqa/lib/log.py
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

   Parse and react to eqemu logs
"""

import time
import sys

import eqa.lib.settings as eqa_settings


def process(log_reload, exit_flag, char_log, log_q):
    """
    Process: char_log
    Produce: log_q
    """

    try:
        log_file = open(char_log, "r")
        log_file.seek(0, 2)
        while not exit_flag.is_set() and not log_reload.is_set():
            line = log_file.readline()
            if not line:
                time.sleep(0.01)
                continue
            log_q.put(line)
    except Exception as e:
        eqa_settings.log(
            "log_generator: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )

    log_file.close()
    sys.exit()
