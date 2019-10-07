#! /usr/bin/env python

"""
   Program:   EQ Alert
   File Name: eqa_state.py
   Copyright (C) 2019 Michael Geitz

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
  def __init__(self, char, chars, zone, loc, afk):
    self.char = char
    self.chars = chars
    self.zone = zone
    self.loc = loc
    self.afk = afk

  def set_char(self, char):
    self.char = char

  def set_chars(self, chars):
    self.chars = chars

  def set_zone(self, zone):
    self.zone = zone

  def set_loc(self, loc):
    self.loc = loc

  def set_afk(self, afk):
    self.afk = afk
