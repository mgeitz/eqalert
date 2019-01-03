"""
eqalert key processor
"""

import curses
import time

import eqa_settings
import eqa_struct

def process(display_q, sound_q, keyboard_q, heal_q, damage_q, message_q, exit_flag, heal_parse, spell_parse, raid):
  """Process Key press events"""

  key = ''
  page = 'events'

  while key != ord('q') and key != 27 and not exit_flag.is_set():

    try:
      # Get key
      time.sleep(0.001)
      if not keyboard_q.empty():
        key = keyboard_q.get()
        keyboard_q.task_done()

        # Handle key
        if key == curses.KEY_RESIZE:
          display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'draw', 'redraw', 'null'))
        if key == curses.KEY_F1:
          if page != 'events':
            display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'draw', 'events', 'null'))
            page = 'events'
        if key == curses.KEY_F2:
          if page != 'state':
            display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'draw', 'state', 'null'))
            page = 'state'
        if key == curses.KEY_F3:
          if page != 'settings':
            display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'draw', 'settings', 'null'))
            page = 'settings'
        if key == curses.KEY_F4:
          if page != 'help':
            display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'draw', 'help', 'null'))
            page = 'help'

        # Alphanumeric keys
        if key == ord('h'):
          if page == 'events':
            if heal_parse.is_set():
              heal_parse.clear()
              display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'event', 'events', 'Heal parse disbled'))
              sound_q.put(eqa_struct.sound('espeak', 'Heal parse disbled'))
            elif not heal_parse.is_set():
              heal_parse.set()
              display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'event', 'events', 'Heal parse enabled'))
              sound_q.put(eqa_struct.sound('espeak', 'Heal parse enabled'))
            display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'draw', 'events', 'null'))
        if key == ord('s'):
          if page == 'events':
            if spell_parse.is_set():
              spell_parse.clear()
              display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'event', 'events', 'Spell parse disabled'))
              sound_q.put(eqa_struct.sound('espeak', 'Spell parse disabled'))
            elif not spell_parse.is_set():
              spell_parse.set()
              display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'event', 'events', 'Spell parse enabled'))
              sound_q.put(eqa_struct.sound('espeak', 'Spell parse enabled'))
            display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'draw', 'events', 'null'))
        if key == ord('p'):
          if page == 'events':
            if spell_parse.is_set():
              spell_parse.clear()
              display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'event', 'events', 'Spell parse disabled'))
              sound_q.put(eqa_struct.sound('espeak', 'Spell parse disabled'))
            elif not spell_parse.is_set():
              spell_parse.set()
              display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'event', 'events', 'Spell parse enabled'))
              sound_q.put(eqa_struct.sound('espeak', 'Spell parse enabled'))
            if heal_parse.is_set():
              heal_parse.clear()
              display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'event', 'events', 'Heal parse disabled'))
              sound_q.put(eqa_struct.sound('espeak', 'Heal parse disbled'))
            elif not heal_parse.is_set():
              heal_parse.set()
              display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'event', 'events', 'Heal parse enabled'))
              sound_q.put(eqa_struct.sound('espeak', 'Heal parse enabled'))
            display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'draw', 'events', 'null'))
        if key == ord('c'):
          if page == 'events':
            display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'event', 'clear', 'null'))
        if key == ord('r'):
          if page == 'events':
            if not raid.is_set():
              raid.set()
              display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'event', 'events', 'Raid mode enabled'))
              sound_q.put(eqa_struct.sound('espeak', 'Raid mode enabled'))
            elif raid.is_set():
              raid.clear()
              display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'event', 'events', 'Raid mode disabled'))
              sound_q.put(eqa_struct.sound('espeak', 'Raid mode disabled'))
            display_q.put(eqa_struct.display(eqa_settings.eqa_time(), 'draw', 'events', 'null'))

    except Exception as e:
      eqa_settings.log('process keys: ' + str(e))
      exit_flag.set()
      pass

  exit_flag.set()


def read(exit_flag, keyboard_q, screen_obj):
  """Check dem keys"""
  key = ''
  while key != ord('q') and key != 27:
    key = screen_obj.getch()
    keyboard_q.put(key)
  exit_flag.set()
