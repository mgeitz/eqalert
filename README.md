# Project 1999 EQALERT

A Project 1999 log parser with NCurses interface for Linux

## Dependencies
    - pyinotify
    - espeak
    - mbrola
    - sox
    - python 2.7

### Install Mbrola

```
$ mkdir tmp_mbrola
$ cd tmp_mbrola
$ wget http://www.tcts.fpms.ac.be/synthesis/mbrola/bin/pclinux/mbr301h.zip
$ unzip mbr301h.zip
$ sudo cp mbrola-linux-i386 /usr/bin/mbrola
$ wget http://www.tcts.fpms.ac.be/synthesis/mbrola/dba/en1/en1-980910.zip
$ unzip en1-980910.zip
$ sudo mkdir /usr/share/mbrola
$ sudo cp en1/en1 /usr/share/mbrola/en1
$ cd ..
$ rm -rf ./tmp_mbrola/

$ espeak -v mb-en1 -s 140 "Hello world"
```

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
