# Project 1999 EQALERT

A Project 1999 log parser with NCurses interface for Linux

![img](https://i.imgur.com/Pgo1eMk.png)
![img](https://i.imgur.com/oj9Nv25.png)
![img](https://i.imgur.com/TCLJ7v4.png)
![img](https://i.imgur.com/a9GNMV3.png)

> Best used with the [Linux EQ Launch Manager](https://gist.github.com/mgeitz/aa295061c51b26d53dd818d0ebb3e37a) to maintain reasonable log file size
![img](https://i.imgur.com/rGL2sY7.png)


## Install

```sh
$ pip install eqalert
```

## Manual Install

```sh
$ git clone git@github.com:mgeitz/eqalert.git
$ cd eqalert
$ pip3 setup.py install
```

## Getting Started

At the moment, the only thing you _must_ do after first start is manually update your default log character in ~/.eqa/config

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
