"""
eqalert config
"""

import json
import datetime

__author__ = "Michael Geitz"
__version__ = "0.2.2"

def init():
    """Updates _HEADER data in config file"""
    json_data = open('eqa_conf.json', 'r+')
    data = json.load(json_data)
    data["_HEADER"]["version"] = __version__
#    data["_HEADER"]["parser_version"] = eqa_parser.__version__
    data["_HEADER"]["modified"] = str(datetime.datetime.now())
    data["_HEADER"]["author"] = __author__
    json_data.seek(0)
    json.dump(data, json_data, indent = 4)
    json_data.close()


def add_type(line_type):
    """Adds default setting values for new line_type"""
    json_data = open('eqa_conf.json', 'r+')
    data = json.load(json_data)
    data["settings"]["sound_settings"].update({line_type:"0"})
    data["settings"]["check_line_type"].update({line_type:"true"})
    data["alert"].update({line_type:dict()})
    data["_HEADER"]["modified"] = str(datetime.datetime.now())
    json_data.seek(0)
    json.dump(data, json_data, indent = 4)
    json_data.close()


def add_zone(zone):
    """Adds default setting values for new zones"""
    json_data = open('eqa_conf.json', 'r+')
    data = json.load(json_data)
    data["zones"].update({zone:"false"})
    data["_HEADER"]["modified"] = str(datetime.datetime.now())
    json_data.seek(0)
    json.dump(data, json_data, indent = 4)
    json_data.close()


def read():
    """Returns JSON objects in config file"""
    json_data = open('eqa_conf.json', 'r')
    config = json.load(json_data)
    json_data.close()
    return config
