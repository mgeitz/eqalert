#! /usr/bin/env python

"""
   Program:   EQ Alert
   File Name: eqa_sound.py
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

import os
import time
import sys
import gtts
from playsound import playsound

import eqa.lib.eqa_struct as eqa_struct
import eqa.lib.eqa_settings as eqa_settings


def process(config, sound_q, exit_flag, cfg_reload):
  """
    Process: sound_q
    Produce: sound event
  """

  tmp_sound_file_path='/tmp/eqa/sound/'

  if not os.path.exists(tmp_sound_file_path):
    os.makedirs(tmp_sound_file_path)

  try:
    while not exit_flag.is_set() and not cfg_reload.is_set():
      time.sleep(0.001)
      if not sound_q.empty():
        sound_event = sound_q.get()
        sound_q.task_done()

        if sound_event.sound == "espeak":
          espeak(sound_event.payload, tmp_sound_file_path)
        elif sound_event.sound == "alert":
          alert(config, sound_event.payload)
        else:
          espeak(sound_event.payload, tmp_sound_file_path)
          display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'event', 'events', "[Malformed sound event] " + sound_event.sound))
  except Exception as e:
    eqa_settings.log('process_sound: ' + str(e))
    sys.exit()

  sys.exit()


def espeak(phrase, tmp_sound_file_path):
    """Playa spoken phrase"""
    try:
      if not os.path.exists(tmp_sound_file_path + phrase):
        tts = gtts.gTTS(text=phrase, lang='en')
        tts.save(tmp_sound_file_path + phrase)
      play_sound(tmp_sound_file_path + phrase)
    except Exception as e:
      eqa_settings.log('process_sound: Error on line ' +
                        str(sys.exc_info()[-1].tb_lineno) + ': ' + str(e))


def alert(config, line_type):
    if not config["settings"]["sound_settings"][line_type] == "0":
        play_sound(config["settings"]["paths"]["sound"] + \
        config["settings"]["sounds"][config["settings"]["sound_settings"][line_type]])


def play_sound(sound):
    """Play the sound given"""
    try:
      playsound(sound)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
  main()
