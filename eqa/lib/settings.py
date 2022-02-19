#! /usr/bin/env python

"""
   Program:   EQ Alert
   File Name: eqa/lib/settings.py
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

from collections import namedtuple
import datetime
import logging
import sys
import time


def usage():
    """Print some helpful things"""
    print("Something awful happened and we may never know what")
    sys.exit(1)


def timestamp():
    """Returns a neat little timestamp for things"""
    unixstamp = int(time.time())
    timestamp = datetime.datetime.fromtimestamp(int(unixstamp)).strftime(
        "%Y-%m-%d_%H:%M:%S"
    )
    return str(timestamp)


def eqa_time():
    """Returns message timestamp HH:MM:SS.ff"""
    return datetime.datetime.now().strftime("%H:%M:%S.%f")[:-4]


def log(message):
    """Effectively just for timestamping all log messages"""
    logging.info("[" + timestamp() + "]: " + str(message))


if __name__ == "__main__":
    main()
