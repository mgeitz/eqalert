#! /usr/bin/env python

"""
   Program:   EQ Alert
   File Name: eqa/lib/sound.py
   Copyright (C) 2024 M Geitz

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
import threading
import io
import sys
import contextlib
import hashlib
import gtts
from playsound import playsound

import eqa.lib.struct as eqa_struct
import eqa.lib.settings as eqa_settings


def process(configs, sound_q, exit_flag, cfg_reload, state, local_tts):
    """
    Process: sound_q
    Produce: sound event
    """

    try:
        # Initial defaults
        sound_file_path = configs.settings.config["settings"]["paths"]["sound"]
        tmp_sound_file_path = configs.settings.config["settings"]["paths"]["tmp_sound"]
        mute_speak = False
        mute_alert = False

        # Create tmp sound directory if missing
        if not os.path.exists(tmp_sound_file_path):
            os.makedirs(tmp_sound_file_path)

        while not exit_flag.is_set() and not cfg_reload.is_set():
            # Sleep between empty checks
            if sound_q.qsize() < 1:
                time.sleep(0.01)

            # Check queue for message
            if not sound_q.empty():
                ## Read new message
                sound_event = sound_q.get()

                if sound_event.sound == "speak" and not mute_speak and not state.mute:
                    speak(
                        configs,
                        sound_event.payload,
                        True,
                        tmp_sound_file_path,
                        local_tts,
                    )
                elif sound_event.sound == "alert" and not mute_alert and not state.mute:
                    alert(configs, sound_event.payload, local_tts)
                elif sound_event.sound == "mute_speak":
                    if sound_event.payload == "toggle":
                        if mute_speak:
                            mute_speak = False
                        else:
                            mute_speak = True
                    else:
                        mute_speak = sound_event.payload
                elif sound_event.sound == "mute_alert":
                    if sound_event.payload == "toggle":
                        if mute_alert:
                            mute_alert = False
                        else:
                            mute_alert = True
                    else:
                        mute_alert = sound_event.payload
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
    line = re.sub(r"(?<=[^A-z])afaik(?=[^A-z])", "as far as I know", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])agi(?=[^A-z])", "agility", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])aow(?=[^A-z])", "avatar of war", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])atm(?=[^A-z])", "at the moment", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])bb(?=[^A-z])", "butcherblock", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])bbl(?=[^A-z])", "be back later", line, flags=re.I)
    line = re.sub(
        r"(?<=[^A-z])bbm(?=[^A-z])", "butcherblock mountains", line, flags=re.I
    )
    line = re.sub(r"(?<=[^A-z])brb(?=[^A-z])", "be right back", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])brt(?=[^A-z])", "be right there", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])bc(?=[^A-z])", "because", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])bp(?=[^A-z])", "bat phone", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])cb(?=[^A-z])", "crushbone", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])ce(?=[^A-z])", "castle entrance", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])cha(?=[^A-z])", "charisma", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])c(?=[^A-z])", "clarity", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])ch(?=[^A-z])", "complete heal", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])clr(?=[^A-z])", "cleric", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])com(?=[^A-z])", "city of mist", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])con(?=[^A-z])", "consider", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])cov(?=[^A-z])", "claws of veeshan", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])cs(?=[^A-z])", "cobalt scar", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])ct(?=[^A-z])", "cazic thule", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])da(?=[^A-z])", "divine aura", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])dd(?=[^A-z])", "direct damage", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])dex(?=[^A-z])", "dexterity", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])dkp(?=[^A-z])", "dragon kill points", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])dl(?=[^A-z])", "dreadlands", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])dmf(?=[^A-z])", "dead man floating", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])dot(?=[^A-z])", "damage over time", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])dps(?=[^A-z])", "damage per second", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])dru(?=[^A-z])", "druid", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])ds(?=[^A-z])", "damage shield", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])eb(?=[^A-z])", "enduring breath", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])ec(?=[^A-z])", "east commonlands", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])ej(?=[^A-z])", "emerald jungle", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])ek(?=[^A-z])", "east karana", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])enc(?=[^A-z])", "enchanter", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])ent(?=[^A-z])", "entrance", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])fd(?=[^A-z])", "feign death", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])fm(?=[^A-z])", "full mana", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])fte(?=[^A-z])", "first to engage", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])gd(?=[^A-z])", "great divide", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])gfay(?=[^A-z])", "greater faydark", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])gl(?=[^A-z])", "good luck", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])gmr(?=[^A-z])", "group resist magic", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])grm(?=[^A-z])", "group resist magic", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])gtg(?=[^A-z])", "good to go", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])guk(?=[^A-z])", "guck", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])hh(?=[^A-z])", "hammer hill", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])hmu(?=[^A-z])", "hit me up", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])hp(?=[^A-z])", "hit points", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])hs(?=[^A-z])", "howling stones", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])ic(?=[^A-z])", "iceclad ocean", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])idc(?=[^A-z])", "I don't care", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])ii(?=[^A-z])", "two", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])imo(?=[^A-z])", "in my opinion", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])inc(?=[^A-z])", "incoming", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])inv(?=[^A-z])", "invite", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])irl(?=[^A-z])", "in real life", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])kc(?=[^A-z])", "karnors castle", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])ld(?=[^A-z])", "link dead", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])lev(?=[^A-z])", "levitate", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])levi(?=[^A-z])", "levitate", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])lf(?=[^A-z])", "looking for", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])lfg(?=[^A-z])", "looking for group", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])lguk(?=[^A-z])", "lower guck", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])ls(?=[^A-z])", "lavastorm", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])lvl(?=[^A-z])", "level", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])ma(?=[^A-z])", "main assist", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])med(?=[^A-z])", "meditate", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])mt(?=[^A-z])", "mistell", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])nec(?=[^A-z])", "necromancer", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])nfp(?=[^A-z])", "north freeport", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])nk(?=[^A-z])", "north karana", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])np(?=[^A-z])", "no problem", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])nvm(?=[^A-z])", "nevermind", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])obo(?=[^A-z])", "or best offer", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])ooc(?=[^A-z])", "out of character", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])oom(?=[^A-z])", "out of mana", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])oot(?=[^A-z])", "ocean of tears", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])omg(?=[^A-z])", "oh my god", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])omw(?=[^A-z])", "on my way", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])otw(?=[^A-z])", "on the way", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])pbaoe(?=[^A-z])", "big badda boom", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])ph(?=[^A-z])", "place holder", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])pl(?=[^A-z])", "power level", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])pls(?=[^A-z])", "please", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])plz(?=[^A-z])", "please", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])pof(?=[^A-z])", "plane of fear", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])poh(?=[^A-z])", "plane of hate", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])pom(?=[^A-z])", "plane of mischief", line, flags=re.I)
    line = re.sub(
        r"(?<=[^A-z])potg(?=[^A-z])", "protection of the glades", line, flags=re.I
    )
    line = re.sub(r"(?<=[^A-z])pov(?=[^A-z])", "point of view", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])pst(?=[^A-z])", "please send tell", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])rh(?=[^A-z])", "right here", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])rl(?=[^A-z])", "real life", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])rn(?=[^A-z])", "right now", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])rog(?=[^A-z])", "rogue", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])rw(?=[^A-z])", "ring war", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])shm(?=[^A-z])", "shaman", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])sow(?=[^A-z])", "spirit of wolf", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])sro(?=[^A-z])", "south ro", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])tba(?=[^A-z])", "to be announced", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])thx(?=[^A-z])", "thanks", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])tl(?=[^A-z])", "translocate", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])tmi(?=[^A-z])", "too much information", line, flags=re.I)
    line = re.sub(
        r"(?<=[^A-z])tofs(?=[^A-z])", "tower of frozen shadow", line, flags=re.I
    )
    line = re.sub(r"(?<=[^A-z])tov(?=[^A-z])", "temple of veeshan", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])tox(?=[^A-z])", "toxxulia forrest", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])ttyl(?=[^A-z])", "talk to you later", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])ty(?=[^A-z])", "thank you", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])tysm(?=[^A-z])", "thank you so much", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])tyvm(?=[^A-z])", "thank you very much", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])uguk(?=[^A-z])", "upper guck", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])vp(?=[^A-z])", "veeshans peak", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])wc(?=[^A-z])", "west commonlands", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])wl(?=[^A-z])", "wakening lands", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])wmp(?=[^A-z])", "when mana permits", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])wru(?=[^A-z])", "where are you", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])wtb(?=[^A-z])", "want to buy", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])wtf(?=[^A-z])", "what the f", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])wts(?=[^A-z])", "want to sell", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])wtt(?=[^A-z])", "want to trade", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])xfer(?=[^A-z])", "transfer", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])yw(?=[^A-z])", "you're welcome", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])\=D(?=[^A-z])", "smiley face", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])<3(?=[^A-z])", "heart", line, flags=re.I)
    line = re.sub(r"(?<=[^A-z])>\.<(?=[^A-z])", "squinting face", line, flags=re.I)
    line = re.sub(
        r"(?<=[^A-z])>\_<(?=[^A-z])", "serious squinting face", line, flags=re.I
    )
    line = re.sub(r"(\d+)p(?![A-z])", r"\1 platinum", line, flags=re.I)
    line = re.sub(r"(\d+)m(?![A-z])", r"\1 mana", line, flags=re.I)

    return line


def speak(configs, line, play, sound_file_path, local_tts):
    """Play a spoken phrase"""
    try:
        # Optionally expand lingo
        if configs.settings.config["settings"]["speech"]["expand_lingo"]:
            phrase = eq_lingo(line)
        else:
            phrase = line
        # Check if line has been generated
        phrase_hash = hashlib.md5(phrase.encode())
        sound_file_name = sound_file_path + phrase_hash.hexdigest() + ".wav"
        if not os.path.exists(sound_file_name):
            # If local TTS is disabled use Google TTS
            if (
                not configs.settings.config["settings"]["speech"]["local_tts"][
                    "enabled"
                ]
                or local_tts is None
            ):
                gtts_tld = configs.settings.config["settings"]["speech"]["gtts_tld"]
                gtts_lang = configs.settings.config["settings"]["speech"]["gtts_lang"]
                google_tts = gtts.gTTS(text=phrase, lang=gtts_lang, tld=gtts_tld)
                google_tts.save(sound_file_name)
            # Otherwise use local TTS
            else:
                with nostdout():
                    local_tts.tts_to_file(text=phrase, file_path=sound_file_name)
        if play:
            play_sound(sound_file_name)

    except Exception as e:
        eqa_settings.log(
            "sound_speak: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def alert(configs, line_type, local_tts):
    """Play configured sounds"""
    try:
        if not configs.alerts.config["line"][line_type]["sound"] == False:
            phrase = configs.alerts.config["line"][line_type]["sound"]
            sound_file_path = configs.settings.config["settings"]["paths"]["sound"]
            sound_file_name = sound_file_path + phrase + ".wav"
            if not os.path.exists(sound_file_name):
                # If local TTS is disabled use gTTS
                if (
                    not configs.settings.config["settings"]["speech"]["local_tts"][
                        "enabled"
                    ]
                    or local_tts is None
                ):
                    gtts_tld = configs.settings.config["settings"]["speech"]["gtts_tld"]
                    gtts_lang = configs.settings.config["settings"]["speech"][
                        "gtts_lang"
                    ]
                    google_tts = gtts.gTTS(text=phrase, lang=gtts_lang, tld=gtts_tld)
                    google_tts.save(sound_file_name)
                # Otherwise use local TTS
                else:
                    with nostdout():
                        local_tts.tts_to_file(text=phrase, file_path=sound_file_name)

            play_sound(sound_file_name)

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
        threading.Thread(target=playsound, args=(sound,), daemon=True).start()
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


@contextlib.contextmanager
def nostdout():
    save_stdout = sys.stdout
    sys.stdout = io.StringIO()
    yield
    sys.stdout = save_stdout


if __name__ == "__main__":
    print("Test Here")
