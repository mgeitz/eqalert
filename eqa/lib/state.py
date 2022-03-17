#! /usr/bin/env python

"""
   Program:   EQ Alert
   File Name: eqa/lib/state.py
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


class EQA_State:
    """Track State"""

    def __init__(
        self, char, chars, zone, loc, direction, afk, server, raid, debug, mute
    ):
        """All States"""
        self.char = char
        self.chars = chars
        self.zone = zone
        self.loc = loc
        self.direction = direction
        self.afk = afk
        self.server = server
        self.raid = raid
        self.debug = debug
        self.mute = mute

    def set_char(self, char):
        """Set Character"""
        self.char = char

    def set_chars(self, chars):
        """Set Characters"""
        self.chars = chars

    def set_zone(self, zone):
        """Set Zone"""
        self.zone = zone

    def set_loc(self, loc):
        """Set Location"""
        self.loc = loc

    def set_direction(self, direction):
        """Set Direction"""
        self.direction = direction

    def set_afk(self, afk):
        """Set AFK"""
        self.afk = afk

    def set_server(self, server):
        """Set Server"""
        self.server = server

    def set_raid(self, raid):
        """Set Raid"""
        self.raid = raid

    def set_debug(self, debug):
        """Set Debug"""
        self.debug = debug

    def set_mute(self, mute):
        """Set Mute"""
        self.mute = mute
