#! /usr/bin/env python

"""
   Program:   EQ Alert
   File Name: eqa/lib/timer.py
   Copyright (C) 2022 Michael Geitz

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

import eqa.lib.struct as eqa_struct
import eqa.lib.settings as eqa_settings


def process(timer_q, sound_q, display_q, exit_flag):
    """
    Process: timer_q
    Produce: display_q, sound_q
    """

    timers = []
    tock = False
    metronome_stop = False

    try:
        while not exit_flag.is_set():

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
                elif timer_event.type == "metronome_stop":
                    if len(timers) == 0:
                        metronome_stop = False
                    elif metronome_stop == False:
                        metronome_stop = True
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

    except Exception as e:
        eqa_settings.log(
            "timer_process: Error on line "
            + str(sys.exc_info()[-1].tb_lineno)
            + ": "
            + str(e)
        )

    sys.exit()


if __name__ == "__main__":
    main()
