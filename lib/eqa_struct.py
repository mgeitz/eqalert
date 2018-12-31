"""
eqalert structs
"""

from collections import namedtuple

global display
global sound
global message
global action

display = namedtuple('data', ['type', 'screen', 'payload'])
sound = namedtuple('data', ['sound', 'payload'])
message = namedtuple('data', ['type', 'timestamp', 'tx', 'rx', 'payload'])
heal = namedtuple('data', ['timestamp', 'type', 'tx', 'rx', 'amount'])
damage = namedtuple('data', ['timestamp', 'type', 'tx', 'rx', 'amount'])
