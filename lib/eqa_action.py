"""
eqalert action
"""

import subprocess
import json
import os
import time

def raid_alert(key, line):
    """Speak raid triggerable phrases"""
    if key == "assist" or key == "rampage":
        espeak(key + " on " + line[0])
    else:
        espeak(key)


def play_sound(sound):
    """Plays sound from path passed in"""
    command = ["play", sound]
    try:
        with open(os.devnull, "w") as fnull:
            subprocess.call(command, stdout=fnull, stderr = fnull)
    except KeyboardInterrupt:
        pass
    time.sleep(0.2)


def sound_alert(config, line_type):
    if not config["settings"]["sound_settings"][line_type] == "0":
        play_sound(config["settings"]["paths"]["sound"] + \
        config["settings"]["sounds"][config["settings"]["sound_settings"][line_type]])


def espeak(phrase):
    """Plays phrase using espeak"""
    command = ["espeak", "-v", "mb-en1", "-s", "140", phrase]
    try:
        with open(os.devnull, "w") as fnull:
            subprocess.call(command, stdout=fnull, stderr = fnull)
    except KeyboardInterrupt:
        pass
    time.sleep(0.2)
