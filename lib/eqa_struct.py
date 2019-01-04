"""
eqalert structs
"""

from collections import namedtuple

global display
global sound
global message

message = namedtuple('data', ['timestamp', 'type', 'tx', 'rx', 'payload'])
display = namedtuple('data', ['timestamp', 'type', 'screen', 'payload'])
sound = namedtuple('data', ['sound', 'payload'])
