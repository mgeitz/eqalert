"""
eqalert structs
"""

from collections import namedtuple

global display
global sound
global message
global action

display = namedtuple('display', ['type', 'screen', 'payload'])
sound = namedtuple('sound', ['type', 'payload'])
message = namedtuple('incoming', ['type', 'timestamp', 'tx', 'rx', 'payload'])
action = namedtuple('action', ['type', 'incoming'])
