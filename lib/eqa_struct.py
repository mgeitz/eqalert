#! /usr/bin/env python

"""
   Program:   EQ Alert
   File Name: eqa_struct.py
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
"""

from collections import namedtuple

global display
global sound
global message

message = namedtuple('data', ['timestamp', 'type', 'tx', 'rx', 'payload'])
display = namedtuple('data', ['timestamp', 'type', 'screen', 'payload'])
sound = namedtuple('data', ['sound', 'payload'])
