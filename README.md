# Project 1999 EQALERT

A Project 1999 log parser with NCurses interface for Linux

![img](https://i.imgur.com/Pgo1eMk.png)
![img](https://i.imgur.com/oj9Nv25.png)
![img](https://i.imgur.com/TCLJ7v4.png)
![img](https://i.imgur.com/a9GNMV3.png)

> Best used with the [Linux EQ Launch Manager](https://gist.github.com/mgeitz/aa295061c51b26d53dd818d0ebb3e37a) to maintain reasonable log file size
![img](https://i.imgur.com/rGL2sY7.png)


## Dependencies
    - pyinotify
    - espeak
    - mbrola
    - sox
    - python 3.7

### Install dependencies

#### Debian
```
$ sudo apt-get update && \
  sudo apt-get install \
    python3 \
    python3-pip \
    espeak && \
  sudo pip3 install pyinotify
```

### Install Mbrola

```
$ mkdir /tmp/tmp_mbrola
$ cd /tmp/tmp_mbrola
$ wget http://www.tcts.fpms.ac.be/synthesis/mbrola/bin/pclinux/mbr301h.zip
$ unzip mbr301h.zip
$ sudo cp mbrola-linux-i386 /usr/bin/mbrola
$ wget http://www.tcts.fpms.ac.be/synthesis/mbrola/dba/en1/en1-980910.zip
$ unzip en1-980910.zip
$ sudo mkdir /usr/share/mbrola
$ sudo cp en1/en1 /usr/share/mbrola/en1
$ cd ..
$ rm -rf /tmp/tmp_mbrola/
```

## Getting Started

  - Populate settings/paths, settings/sounds, characters/default
  - Add sounds added in settings/sounds to sounds directory


## Controls

Global:
  - F1    : Display events
  - F2    : Display state
  - F3    : Display settings
  - F4    : Display help
  - q     : Quit/Back

Events:
  - c     : Clear event box
  - r     : Toggle raid mode

Settings:
  - up    : Cycle up in selection
  - down  : Cycle down in selection
  - right : Toggle selection on
  - left  : Toggle selection off
  - space : Cycle selection


## Modes

  - Raid Mode
    > espeaks all raid values in alert/guild in config
    > toggle with 'r'
    > auto-enables when zoning into 'raid' zone


## Adding new sounds, triggers

  - Add new sounds to the sound directory, their paths manually in settings/sounds
  - Add new triggers to alert in the config file

## Adding new characters

  - All log files seen at start up in log root path are automatically added to the config as a character


## Adding new line_type to be parsed

  - Add to if/elif structure in eqparser.py, minding existing control flow
  - Default values are generated in config in settings/sound_settings, settings/check_line_type, and alert
    for added line_types once encountered in-game
