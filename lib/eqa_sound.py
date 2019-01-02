"""
eqalert action
"""

import subprocess
import os
import time

import eqa_struct
import eqa_settings


def process(config, sound_q, exit_flag):
  """Process sound events"""
  while not exit_flag.is_set():
    time.sleep(0.001)
    if not sound_q.empty():
      sound_event = sound_q.get()
      sound_q.task_done()

      if sound_event.sound == "espeak":
        espeak(sound_event.payload)
      elif sound_event.sound == "alert":
        alert(config, sound_event.payload)
      else:
        espeak(sound_event.payload)
        display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'event', 'events', "[Malformed sound event] " + sound_event.sound))


def raid_alert(key, line):
    """Speak raid triggerable phrases"""
    if key == "assist" or key == "rampage":
        espeak(key + " on " + line[0])
    else:
        espeak(key)


def espeak(phrase):
    """Plays phrase using espeak"""
    command = ["espeak", "-v", "mb-en1", "-s", "140", phrase]
    try:
        with open(os.devnull, "w") as fnull:
            subprocess.call(command, stdout=fnull, stderr = fnull)
    except KeyboardInterrupt:
        pass


def alert(config, line_type):
    if not config["settings"]["sound_settings"][line_type] == "0":
        play_sound(config["settings"]["paths"]["sound"] + \
        config["settings"]["sounds"][config["settings"]["sound_settings"][line_type]])


def play_sound(sound):
    """Plays sound from path passed in"""
    command = ["play", sound]
    try:
        with open(os.devnull, "w") as fnull:
            subprocess.call(command, stdout=fnull, stderr = fnull)
    except KeyboardInterrupt:
        pass
