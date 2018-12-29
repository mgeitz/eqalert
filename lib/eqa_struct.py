"""
eqalert structs
"""

from collections import namedtuple

display = namedtuple('display', ['type', 'screen', 'payload'])
sound = namedtuple('sound', ['type', 'payload'])

incoming = namedtuple('incoming', ['type', 'tx', 'rx', 'payload'])
action = namedtuple('action', ['type', 'incoming'])
