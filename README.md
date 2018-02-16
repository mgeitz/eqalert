# Project 1999 EQALERT

A Project 1999 log parser with NCurses interface for Linux

## Dependencies
    - espeak
    - alsa
    - python 2.7

## Getting Started

  - Populate settings/paths, settings/sounds, characters/default
  - Add sounds added in settings/sounds to sounds directory


## Controls

  - q  : Quit/Back
  - h  : Toggle heal parse
  - s  : Toggle spell damage parse
  - p  : Toggle all parses
  - c  : Clear event box
  - r  : Toggle raid mode
  - F1 : Display help menu
  - F2 : Open char menu
  - F3 : Save and reset parses
  - F4 : Clear heal parse history
  - F5 : Clear spell parse history
  - F12: Reload config file


## Modes

  - Raid Mode
    > espeaks all raid values in alert/guild in config
    > toggle with 'r'
    > auto-enables when zoning into 'raid' zone

  - Heal Parse
    > tallies all heals on targets
    > 'h' to toggle heal parse
    > F3 to save heal parse to file
    > F4 to clear the heal parse

  - Spell Parse
    > tallies spell damage done to a target
    > 's' to toggle spell parse
    > F3 to save spell parse to file
    > F5 to clear spell parse


## Adding new sounds, triggers

  - Add new sounds to the sound directory, their paths manually in settings/sounds
  - Add new triggers to alert in the config file

## Adding new characters

  - All log files seen at start up in log root path are automatically added to the config as a character


## Adding new line_type to be parsed

  - Add to if/elif structure in eqparser.py, minding existing control flow
  - Default values are generated in config in settings/sound_settings, settings/check_line_type, and alert
    for added line_types once encountered in-game
