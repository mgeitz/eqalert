"""
eqalert key processor
"""

import curses

import eqa_settings
import eqa_struct

def process(exit_flag, spell_parse, heal_parse, raid, display_q, sound_q, keyboard_q, heal_q, damage_q, message_q):
  """Process Key press events"""

  key = ''
  while key != ord('q') and key != 27:

    try:
      # Get key
      if not keyboard_q.empty():
        key = keyboard_q.get()
        keyboard_q.task_done()

        # Handle key
        if key == curses.KEY_RESIZE:
          display_q.put(eqa_struct.display('draw', 'all', 'null'))
        if key == curses.KEY_F1:
          display_q.put(eqa_struct.display('draw', 'help', 'null'))
        if key == curses.KEY_F2:
          display_q.put(eqa_struct.display('draw', 'char_menu', 'null'))
        if key == curses.KEY_F3:
          if heal_parse.is_set() or spell_parse.is_set():
            heal_q.put(eqa_struct.heal('null', 'save', 'null', 'null', 'null'))
            damage_q.put(eqa_struct.heal('null', 'save', 'null', 'null', 'null'))
            heal_q.clear()
            damage_q.clear()
            eqa_settings.log('Parse history saved and cleared')
            sound_q.put(eqa_struct.sound('espeak', 'Parse history saved and cleared'))
          else:
            eqa_settings.log('No history to clear')
          display_q.put(eqa_struct.display('draw', 'all', 'null'))
        if key == curses.KEY_F4:
          heal_q.clear()
          eqa_settings.log("Heal parse cleared")
          sound_q.put(eqa_struct.sound('espeak', "Heal parse cleared"))
          display_q.put(eqa_struct.display('draw', 'all', 'null'))
        if key == curses.KEY_F5:
          damage_q.cleared()
          eqa_settings.log("Spell parse cleared")
          sound_q.put(eqa_struct.sound('espeak', "Spell parse cleared"))
          display_q.put(eqa_struct.display('draw', 'all', 'null'))
        if key == curses.KEY_F12:
          message_q.put(eqa_struct.message('system', eqa_settings.timestamp(), 'reload_config', 'null', 'null'))

        # Alphanumeric keys
        if key == ord('h'):
          if heal_parse.is_set():
            heal_parse.clear()
            eqa_settings.log('Heal parse disbled')
            sound_q.put(eqa_struct.sound('espeak', 'Heal parse disbled'))
          elif not heal_parse.is_set():
            heal_parse.set()
            eqa_settings.log('Heal parse enabled')
            sound_q.put(eqa_struct.sound('espeak', 'Heal parse enabled'))
          display_q.put(eqa_struct.display('draw', 'all', 'null'))
        if key == curses.KEY_F12:
          display_q.put(eqa_struct.display('draw', 'all', 'null'))
        if key == ord('s'):
          if spell_parse.is_set():
            spell_parse.clear()
            eqa_settings.log('Spell parse disabled')
            sound_q.put(eqa_struct.sound('espeak', 'Spell parse disabled'))
          elif not spell_parse.is_set():
            spell_parse.set()
            eqa_settings.log('Spell parse enabled')
            sound_q.put(eqa_struct.sound('espeak', 'Spell parse enabled'))
          display_q.put(eqa_struct.display('draw', 'all', 'null'))
        if key == ord('p'):
          if spell_parse.is_set():
            spell_parse.clear()
            eqa_settings.log('Spell parse disabled')
            sound_q.put(eqa_struct.sound('espeak', 'Spell parse disabled'))
          elif not spell_parse.is_set():
            spell_parse.set()
            eqa_settings.log('Spell parse enabled')
            sound_q.put(eqa_struct.sound('espeak', 'Spell parse enabled'))
          if heal_parse.is_set():
            heal_parse.clear()
            eqa_settings.log('Heal parse disbled')
            sound_q.put(eqa_struct.sound('espeak', 'Heal parse disbled'))
          elif not heal_parse.is_set():
            heal_parse.set()
            eqa_settings.log('Heal parse enabled')
            sound_q.put(eqa_struct.sound('espeak', 'Heal parse enabled'))
          display_q.put(eqa_struct.display('draw', 'all', 'null'))
        if key == ord('c'):
          eqa_settings.log("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
          display_q.put(eqa_struct.display('draw', 'all', 'null'))
        if key == ord('r'):
          if not raid.is_set():
            raid.set()
            eqa_settings.log("Raid mode enabled")
            sound_q.put(eqa_struct.sound('espeak', 'Raid mode enabled'))
          elif raid.is_set():
            raid.clear()
            eqa_settings.log("Raid mode disabled")
            sound_q.put(eqa_struct.sound('espeak', 'Raid mode disabled'))
          display_q.put(eqa_struct.display('draw', 'all', 'null'))

    except Exception as e:
      eqa_settings.log(e)
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
