# EQAlert

An everquest eqmulator log parser with NCurses interface for Linux

![img](https://i.imgur.com/Pgo1eMk.png)
![img](https://i.imgur.com/SkPvD9j.png)
![img](https://i.imgur.com/TCLJ7v4.png)
![img](https://i.imgur.com/a9GNMV3.png)

> Best used with the [Linux EQ Launch Manager](https://gist.github.com/mgeitz/aa295061c51b26d53dd818d0ebb3e37a) to maintain reasonable log file size


## Install

Install from pypi
```sh
$ # Install Stable
$ pip3 install eqalert=1.5.0
$
$ # Install whatever I just pushed to pypi
$ pip3 install eqalert
```

_or_ install manually from github
```sh
$ git clone git@github.com:mgeitz/eqalert.git
$ cd eqalert
$ pip3 setup.py install
```


## Getting Started

Start things up
```sh
$ eqalert
```

You should now see `~/.eqa/` with the following structure
```
$HOME/.eqa
        ⎿ config.json
        ⎿ log/
        ⎿ sound/
```

Update your default character in `config.json` if needed
```
    "characters": {
        "default": "indefinite",
        "indefinite": "true",
        "indef": "true"
    },
```

Update your default server in `config.json` if needed
```
    "servers": {
        "default": "project1999",
        "project1999": "true"
    },
```

Spot check these paths in `config.json`
```
    "settings": {
        "paths": {
            "sound": "%ssound/",
            "alert_log": "%slog/",
            "char_log": "%s/.wine/drive_c/Program Files/Sony/EverQuest/Logs/"
        },
```

Press `F12` to reload your config or restart the program, you're good to go!


## Upgrading Versions

- Upgrades via pip may require you regenerate your config by removing or deleting ~/.eqa/ before starting.
- This is only 10% due to laziness and 90% due not knowing how to migrate old configs over to new ones yet


## Controls

Global:
  - F1      : Events
  - F2      : State
  - F3      : Settings
  - F4      : Help
  - F12     : Reload config
  - q / esc : Quit

Events:
  - c     : Clear event box
  - r     : Toggle raid mode

Settings:
  - up    : Cycle up in selection
  - down  : Cycle down in selection
  - right : Toggle selection on
  - left  : Toggle selection off
  - space : Cycle selection
