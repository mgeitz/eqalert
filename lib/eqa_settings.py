"""
eqalert settings
"""

import sys
import os
import logging
import time
import datetime
import yaml
import pwd
import grp
from collections import namedtuple

def usage():
  """Print some helpful things"""
  print 'ya done goofed'
  sys.exit(2)


def timestamp():
  """Returns a neat little timestamp for things"""
  unixstamp = int(time.time())
  timestamp = datetime.datetime.fromtimestamp(int(unixstamp))\
      .strftime('%Y-%m-%d_%H:%M:%S')
  return str(timestamp)


def log(message):
  """Effectively just for timestamping all log messages"""
  logging.info('[' + timestamp() + ']: ' + str(message))
