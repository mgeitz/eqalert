#! /usr/bin/env python

"""
   Program:   EQ Alert
   File Name: eqa/lib/timer.py
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

import heapq
import datetime
import time
import sys
import json
import os

import eqa.lib.struct as eqa_struct
import eqa.lib.settings as eqa_settings


def process(
    configs, state, timer_q, sound_q, display_q, exit_flag, cfg_reload, change_char
):
    """
    Process: timer_q
    Produce: display_q, sound_q
    """

    try:
        timers = []
        zoning_start_time = None
        tock = False
        metronome_stop = False
        saved_timers_path = (
            configs.settings.config["settings"]["paths"]["data"]
            + "timers/"
            + state.char.lower()
            + "_"
            + state.server.lower()
            + "-timers.json"
        )

        # Load timers
        if os.path.isfile(saved_timers_path):
            json_data = open(saved_timers_path, "r", encoding="utf-8")
            saved_timers = json.load(json_data)
            json_data.close()

            now = datetime.datetime.now()
            file_saved = datetime.datetime.strptime(
                saved_timers["time"], "%Y-%m-%d %H:%M:%S.%f"
            )
            for item in saved_timers["timers"].keys():
                item_type = saved_timers["timers"][item]["type"]
                if item_type == "timer":
                    item_time = datetime.datetime.strptime(
                        saved_timers["timers"][item]["time"], "%Y-%m-%d %H:%M:%S.%f"
                    )
                    item_seconds = saved_timers["timers"][item]["seconds"]
                    item_payload = saved_timers["timers"][item]["payload"]
                    if not item_time <= now:
                        heapq.heappush(
                            timers,
                            eqa_struct.timer(
                                item_time,
                                item_type,
                                item_seconds,
                                item_payload,
                            ),
                        )
                elif item_type == "spell":
                    item_target = saved_timers["timers"][item]["target"]
                    item_type = saved_timers["timers"][item]["type"]
                    item_caster = saved_timers["timers"][item]["caster"]
                    item_spell = saved_timers["timers"][item]["spell"]
                    item_duration = saved_timers["timers"][item]["duration"]
                    item_landed = datetime.datetime.strptime(
                        saved_timers["timers"][item]["landed"], "%Y-%m-%d %H:%M:%S.%f"
                    )
                    item_payload = saved_timers["timers"][item]["payload"]
                    if item_target == state.char.lower():
                        item_time = datetime.datetime.now() + datetime.timedelta(
                            seconds=int(item_duration)
                        )
                        item_landed = datetime.datetime.now()
                    else:
                        item_time = datetime.datetime.strptime(
                            saved_timers["timers"][item]["time"], "%Y-%m-%d %H:%M:%S.%f"
                        )
                        item_landed = datetime.datetime.strptime(
                            saved_timers["timers"][item]["landed"],
                            "%Y-%m-%d %H:%M:%S.%f",
                        )
                    if not item_time <= now:
                        heapq.heappush(
                            timers,
                            eqa_struct.spell_timer(
                                item_time,
                                item_type,
                                item_caster,
                                item_target,
                                item_spell,
                                item_duration,
                                item_landed,
                                item_payload,
                            ),
                        )

            # Remove saved timer file
            os.remove(saved_timers_path)

        # Consume timer_q
        while (
            not exit_flag.is_set()
            and not cfg_reload.is_set()
            and not change_char.is_set()
        ):
            # Sleep between empty checks
            if timer_q.qsize() < 1:
                time.sleep(0.01)

            # Check queue for message
            if not timer_q.empty():
                ## Read new message
                timer_event = timer_q.get()

                if timer_event.type == "metronome":
                    if tock == False:
                        heapq.heappush(
                            timers,
                            eqa_struct.timer(
                                timer_event.time,
                                "tick",
                                timer_event.seconds,
                                timer_event.payload,
                            ),
                        )
                        tock = True
                    else:
                        heapq.heappush(
                            timers,
                            eqa_struct.timer(
                                timer_event.time,
                                "tock",
                                timer_event.seconds,
                                timer_event.payload,
                            ),
                        )
                        tock = False
                elif timer_event.type == "timer":
                    heapq.heappush(timers, timer_event)
                elif timer_event.type == "spell":
                    timers = add_spell_timer(state, timers, timer_event)
                elif timer_event.type == "remove_spell_timer":
                    timers = remove_spell_timer(state, timers, timer_event)
                elif timer_event.type == "metronome_stop":
                    if len(timers) == 0:
                        metronome_stop = False
                    elif metronome_stop == False:
                        metronome_stop = True
                elif timer_event.type == "new_zone":
                    if configs.settings.config["settings"]["timers"]["spell"][
                        "zone_drift"
                    ]:
                        if zoning_start_time is not None:
                            adjustment = (
                                timer_event.time - zoning_start_time
                            ).total_seconds()
                            # If the zone duration is more than a minute, give up something is wrong
                            if adjustment <= 45:
                                timers = self_spell_timer_drift(
                                    state, timers, adjustment
                                )
                elif timer_event.type == "zoning":
                    zoning_start_time = timer_event.time
                elif timer_event.type == "draw_timers":
                    draw_timers = timers.copy()
                    display_q.put(
                        eqa_struct.display(
                            eqa_settings.eqa_time(), "draw", "timers", draw_timers
                        )
                    )
                elif timer_event.type == "clear":
                    timers = []

                timer_q.task_done()

            # Check timers
            if len(timers) > 0:
                timer = heapq.heappop(timers)
                now = datetime.datetime.now()
                if timer.time <= now:
                    if timer.type == "tick":
                        if metronome_stop == True:
                            metronome_stop = False
                        else:
                            sound_q.put(eqa_struct.sound("tick", "tock"))
                            timer_q.put(
                                eqa_struct.timer(
                                    (
                                        datetime.datetime.now()
                                        + datetime.timedelta(seconds=int(timer.seconds))
                                    ),
                                    "metronome",
                                    timer.seconds,
                                    timer.payload,
                                )
                            )
                    elif timer.type == "tock":
                        if metronome_stop == True:
                            metronome_stop = False
                        else:
                            sound_q.put(eqa_struct.sound("tock", "tick"))
                            timer_q.put(
                                eqa_struct.timer(
                                    (
                                        datetime.datetime.now()
                                        + datetime.timedelta(seconds=int(timer.seconds))
                                    ),
                                    "metronome",
                                    timer.seconds,
                                    timer.payload,
                                )
                            )
                    elif timer.type == "spell":
                        if configs.settings.config["settings"]["timers"]["spell"][
                            "consolidate"
                        ]:
                            timers = consolidate_spell_timers(
                                timer, timers, sound_q, display_q
                            )
                    else:
                        sound_q.put(eqa_struct.sound("speak", str(timer.payload)))
                        display_q.put(
                            eqa_struct.display(
                                eqa_settings.eqa_time(),
                                "event",
                                "events",
                                "Timer: " + str(timer.payload),
                            )
                        )
                else:
                    heapq.heappush(timers, timer)

        # Save timers
        if len(timers) > 0:
            saved_timers_json = {
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                "timers": {},
            }
            count = 1
            while len(timers) > 0:
                timer = heapq.heappop(timers)
                timer_name = "timer_" + str(count)
                count += 1
                if timer.type == "timer":
                    saved_timers_json["timers"].update(
                        {
                            timer_name: {
                                "time": str(timer.time),
                                "type": str(timer.type),
                                "seconds": str(timer.seconds),
                                "payload": str(timer.payload),
                            }
                        }
                    )
                elif timer.type == "spell":
                    if timer.target == state.char.lower():
                        duration = int(
                            timer.duration
                            - (datetime.datetime.now() - timer.landed).total_seconds()
                        )
                    else:
                        duration = timer.duration
                    saved_timers_json["timers"].update(
                        {
                            timer_name: {
                                "time": str(timer.time),
                                "type": str(timer.type),
                                "caster": str(timer.caster),
                                "target": str(timer.target),
                                "spell": str(timer.spell),
                                "duration": duration,
                                "landed": str(timer.landed),
                                "payload": str(timer.payload),
                            }
                        }
                    )

            json_data = open(saved_timers_path, "w")
            json.dump(saved_timers_json, json_data, sort_keys=True, indent=2)
            json_data.close()

    except Exception as e:
        eqa_settings.log(
            "timer_process: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )

    sys.exit()


def remove_spell_timer(state, timers, remove_timer):
    """Remove some timers"""

    try:
        new_timers = []
        for timer_event in timers:
            if timer_event.type == "spell":
                if (
                    remove_timer.target == timer_event.target
                    and remove_timer.spell == timer_event.spell
                ):
                    if state.debug:
                        eqa_settings.log(
                            "Removing timer: "
                            + timer_event.spell
                            + " on "
                            + timer_event.target
                        )
                elif (
                    remove_timer.target == timer_event.target
                    and remove_timer.spell == "all"
                ):
                    if state.debug:
                        eqa_settings.log(
                            "Removing timer: "
                            + timer_event.spell
                            + " on "
                            + timer_event.target
                        )
                else:
                    heapq.heappush(new_timers, timer_event)
            else:
                heapq.heappush(new_timers, timer_event)

        return new_timers

    except Exception as e:
        eqa_settings.log(
            "Remove spell timer: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def consolidate_spell_timers(expired_timer, timers, sound_q, display_q):
    """Consolidate like spell timers"""

    try:
        new_timers = []
        payload = expired_timer.payload
        for timer_event in timers:
            if timer_event.type == "spell":
                if expired_timer.spell == timer_event.spell:
                    if int((timer_event.time - expired_timer.time).total_seconds()) < 3:
                        if expired_timer.payload.endswith(" has worn off"):
                            payload = (
                                expired_timer.spell.replace("_", " ")
                                + " on "
                                + expired_timer.target
                                + " and others has worn off"
                            )
                        else:
                            payload = (
                                expired_timer.spell.replace("_", " ")
                                + " on "
                                + expired_timer.target
                                + " and others is wearing off"
                            )
                    else:
                        heapq.heappush(new_timers, timer_event)
                else:
                    heapq.heappush(new_timers, timer_event)
            else:
                heapq.heappush(new_timers, timer_event)

        sound_q.put(eqa_struct.sound("speak", payload))
        display_q.put(
            eqa_struct.display(
                eqa_settings.eqa_time(),
                "event",
                "events",
                "Timer: " + str(payload),
            )
        )

        return new_timers

    except Exception as e:
        eqa_settings.log(
            "Consolidate spell timer: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def add_spell_timer(state, timers, new_timer_event):
    """Add a timer"""

    try:
        new_timers = []
        for timer_event in timers:
            if timer_event.type == "spell":
                if (
                    new_timer_event.target == timer_event.target
                    and new_timer_event.spell == timer_event.spell
                ):
                    if state.debug:
                        eqa_settings.log(
                            "Removing old timer: "
                            + timer_event.spell
                            + " on "
                            + timer_event.target
                        )
                else:
                    heapq.heappush(new_timers, timer_event)
            else:
                heapq.heappush(new_timers, timer_event)

        heapq.heappush(new_timers, new_timer_event)

        return new_timers

    except Exception as e:
        eqa_settings.log(
            "Add spell timer: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


def self_spell_timer_drift(state, timers, adjustment):
    """Adjust timers on self for zoning times"""

    try:
        new_timers = []
        for timer_event in timers:
            if timer_event.type == "spell":
                if timer_event.target == state.char.lower():
                    new_time = timer_event.time + datetime.timedelta(seconds=adjustment)
                    heapq.heappush(
                        new_timers,
                        eqa_struct.spell_timer(
                            new_time,
                            timer_event.type,
                            timer_event.caster,
                            timer_event.target,
                            timer_event.spell,
                            timer_event.duration,
                            timer_event.landed,
                            timer_event.payload,
                        ),
                    )
                else:
                    heapq.heappush(new_timers, timer_event)
            else:
                heapq.heappush(new_timers, timer_event)

        return new_timers

    except Exception as e:
        eqa_settings.log(
            "Self spell timer drift: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )


if __name__ == "__main__":
    print("Test Here")
