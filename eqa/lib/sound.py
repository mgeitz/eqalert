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
import re
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
                    speak(configs, sound_event.payload, "true", tmp_sound_file_path)
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


def eq_lingo(line):
    """Substitute Common EQ Abbreviations"""

    line = re.sub(r"(?<=[^A-z])ac(?=[^A-z])", "armor class", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])agi(?=[^A-z])", "agility", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])aow(?=[^A-z])", "avatar of war", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])atm(?=[^A-z])", "at the moment", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])bb(?=[^A-z])", "butcherblock", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])cb(?=[^A-z])", "crushbone", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])ce(?=[^A-z])", "castle entrance", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])cha(?=[^A-z])", "charisma", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])ch(?=[^A-z])", "complete heal", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])com(?=[^A-z])", "city of mist", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])con(?=[^A-z])", "consider", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])cov(?=[^A-z])", "claws of veeshan", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])cs(?=[^A-z])", "cobalt scar", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])ct(?=[^A-z])", "cazic thule", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])dd(?=[^A-z])", "direct damage", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])dex(?=[^A-z])", "dexterity", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])dkp(?=[^A-z])", "dragon kill points", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])dl(?=[^A-z])", "dreadlands", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])dmf(?=[^A-z])", "dead man floating", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])dot(?=[^A-z])", "damage over time", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])dps(?=[^A-z])", "damage per second", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])ds(?=[^A-z])", "damage shield", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])eb(?=[^A-z])", "enduring breath", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])ec(?=[^A-z])", "east commonlands", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])ej(?=[^A-z])", "emerald jungle", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])ek(?=[^A-z])", "east karana", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])enc(?=[^A-z])", "enchanter", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])fd(?=[^A-z])", "feign death", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])fm(?=[^A-z])", "full mana", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])fr(?=[^A-z])", "fire resist", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])fte(?=[^A-z])", "first to engage", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])gd(?=[^A-z])", "great divide", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])gfay(?=[^A-z])", "greater faydark", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])gmr(?=[^A-z])", "group resist magic", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])grm(?=[^A-z])", "group resist magic", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])gtg(?=[^A-z])", "good to go", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])hh(?=[^A-z])", "hammer hill", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])hp(?=[^A-z])", "hit points", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])hs(?=[^A-z])", "howling stones", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])ic(?=[^A-z])", "iceclad ocean", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])imo(?=[^A-z])", "in my opinion", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])inc(?=[^A-z])", "incoming", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])irl(?=[^A-z])", "in real life", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])ld(?=[^A-z])", "link dead", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])lev(?=[^A-z])", "levitate", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])levi(?=[^A-z])", "levitate", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])lf(?=[^A-z])", "looking for", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])lfg(?=[^A-z])", "looking for group", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])lguk(?=[^A-z])", "lower guck", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])ls(?=[^A-z])", "lavastorm", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])ma(?=[^A-z])", "main assist", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])med(?=[^A-z])", "meditate", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])mt(?=[^A-z])", "mistell", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])nk(?=[^A-z])", "north karana", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])np(?=[^A-z])", "no problem", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])ooc(?=[^A-z])", "out of character", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])oom(?=[^A-z])", "out of mana", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])omw(?=[^A-z])", "on my way", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])otw(?=[^A-z])", "on the way", line, flags=re.I)
    line = re.sub(
        r"(?<=[^A-z])pbaoe(?=[^A-z])", "point blank area of effect", line, flags=re.I
    )
    line = re.sub(r"(?<=[^A-z])ph(?=[^A-z])", "place holder", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])pls(?=[^A-z])", "please", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])pof(?=[^A-z])", "plane of fear", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])poh(?=[^A-z])", "plane of hate", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])pom(?=[^A-z])", "plane of mischief", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])rl(?=[^A-z])", "real life", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])sf(?=[^A-z])", "steamfont", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])sow(?=[^A-z])", "spirit of wolf", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])sro(?=[^A-z])", "south ro", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])tl(?=[^A-z])", "translocate", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])tov(?=[^A-z])", "temple of veeshan", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])tox(?=[^A-z])", "toxxulia forrest", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])ty(?=[^A-z])", "thank you", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])uguk(?=[^A-z])", "upper guck", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])vp(?=[^A-z])", "veeshans peak", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])vs(?=[^A-z])", "venril sathir", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])wc(?=[^A-z])", "west commonlands", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])wl(?=[^A-z])", "wakening lands", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])wmp(?=[^A-z])", "when mana permits", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])wtb(?=[^A-z])", "want to buy", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])wts(?=[^A-z])", "want to sell", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])wtt(?=[^A-z])", "want to trade", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])xfer(?=[^A-z])", "transfer", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])yw(?=[^A-z])", "you're welcome", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])<3(?=[^A-z])", "heart", line, flags=re.I)
    line = re.sub(r"(\d)p(?![A-z])", " platinum", line, flags=re.I)

    return line


def speak(configs, line, play, sound_file_path):
    """Play a spoken phrase"""
    try:
        phrase = eq_lingo(line)
        phrase_hash = hashlib.md5(phrase.encode())
        if not os.path.exists(sound_file_path + phrase_hash.hexdigest() + ".wav"):
            gtts_tld = configs.settings.config["settings"]["speech"]["tld"]
            gtts_lang = configs.settings.config["settings"]["speech"]["lang"]
            tts = gtts.gTTS(text=phrase, lang=gtts_lang, tld=gtts_tld)
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
                gtts_tld = configs.settings.config["settings"]["speech"]["tld"]
                gtts_lang = configs.settings.config["settings"]["speech"]["lang"]
                tts = gtts.gTTS(text=phrase, lang=gtts_lang, tld=gtts_tld)
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
