#! /usr/bin/env python

"""
   Program:   EQ Alert
   File Name: eqa/lib/sound.py
   Copyright (C) 2023 M Geitz

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
import hashlib
import gtts
from playsound import playsound

import eqa.lib.struct as eqa_struct
import eqa.lib.settings as eqa_settings


def process(configs, sound_q, exit_flag, cfg_reload, state):
    """
    Process: sound_q
    Produce: sound event
    """

    sound_file_path = configs.settings.config["settings"]["paths"]["sound"]
    tmp_sound_file_path = configs.settings.config["settings"]["paths"]["tmp_sound"]
    mute_speak = "false"
    mute_alert = "false"

    if not os.path.exists(tmp_sound_file_path):
        os.makedirs(tmp_sound_file_path)

    try:
        while not exit_flag.is_set() and not cfg_reload.is_set():

            # Sleep between empty checks
            if sound_q.qsize() < 1:
                time.sleep(0.01)

            # Check queue for message
            if not sound_q.empty():
                ## Read new message
                sound_event = sound_q.get()

                if sound_event.sound == "mute_speak":
                    mute_speak = sound_event.payload
                elif sound_event.sound == "mute_alert":
                    mute_alert = sound_event.payload
                elif (
                    sound_event.sound == "speak"
                    and not mute_speak == "true"
                    and not state.mute == "true"
                ):
                    speak(sound_event.payload, "true", tmp_sound_file_path)
                elif (
                    sound_event.sound == "alert"
                    and not mute_alert == "true"
                    and not state.mute == "true"
                ):
                    alert(configs, sound_event.payload)
                elif sound_event.sound == "tick":
                    sound_tick(sound_file_path, sound_event)
                elif sound_event.sound == "tock":
                    sound_tock(sound_file_path, sound_event)

                sound_q.task_done()

    except Exception as e:
        eqa_settings.log(
            "sound_process: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )

    sys.exit()


def speak(phrase, play, sound_file_path):
    """Play a spoken phrase"""
    try:
        phrase_hash = hashlib.md5(phrase.encode())
        if not os.path.exists(sound_file_path + phrase_hash.hexdigest() + ".wav"):
            tts = gtts.gTTS(text=phrase, lang="en")
            tts.save(sound_file_path + phrase_hash.hexdigest() + ".wav")
        if play == "true":
            play_sound(sound_file_path + phrase_hash.hexdigest() + ".wav")

    except Exception as e:
        eqa_settings.log(
            "sound_speak: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def alert(configs, line_type):
    """Play configured sounds"""
    try:
        if not configs.alerts.config["line"][line_type]["sound"] == "false":
            phrase = configs.alerts.config["line"][line_type]["sound"]
            sound_file_path = configs.settings.config["settings"]["paths"]["sound"]
            if not os.path.exists(sound_file_path + phrase + ".wav"):
                tts = gtts.gTTS(text=phrase, lang="en")
                tts.save(sound_file_path + phrase + ".wav")
            play_sound(sound_file_path + phrase + ".wav")

    except Exception as e:
        eqa_settings.log(
            "sound_alert: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def play_sound(sound):
    """Play the sound given"""
    try:
        playsound(sound)
    except Exception as e:
        eqa_settings.log(
            "sound_play_sound: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def sound_tock(sound_file_path, sound_event):
    """Tock!"""
    try:
        if not os.path.exists(sound_file_path + "tock.wav"):
            tts = gtts.gTTS(text="tock", lang="en")
            tts.save(sound_file_path + "tock.wav")

        play_sound(sound_file_path + "tock.wav")

    except Exception as e:
        eqa_settings.log(
            "sound_tock: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def sound_tick(sound_file_path, sound_event):
    """Tick!"""
    try:
        if not os.path.exists(sound_file_path + "tick.wav"):
            tts = gtts.gTTS(text="tick", lang="en")
            tts.save(sound_file_path + "tick.wav")

        play_sound(sound_file_path + "tick.wav")

    except Exception as e:
        eqa_settings.log(
            "sound_tick: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


if __name__ == "__main__":
    main()
