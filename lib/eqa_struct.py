"""
eqalert structs
"""

from collections import namedtuple

global display
global sound
global message

display = namedtuple('data', ['timestamp', 'type', 'screen', 'payload'])
message = namedtuple('data', ['timestamp', 'type', 'tx', 'rx', 'payload'])
sound = namedtuple('data', ['sound', 'payload'])
