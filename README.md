# EQAlert

An Everquest Emulator Log Parser with NCurses Interface for Linux

![img](https://i.imgur.com/wMs0RcV.png)

> Best used with the [Linux EQ Launch Manager](https://gist.github.com/mgeitz/aa295061c51b26d53dd818d0ebb3e37a) to maintain reasonable log file size


## Install

Install from pypi
```sh
$ # Install Stable
$ pip3 install eqalert==2.2.5
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

Spot check these default paths generated in `config.json`
```
    "settings": {
        "paths": {
            "alert_log": "[$HOME/.eqa/]log/",
            "char_log": "[$HOME]/.wine/drive_c/Program Files/Sony/EverQuest/Logs/",
            "sound": "[$HOME/.eqa/]sound/"
        },
```
> Press `F12` to reload your config or restart the program if any changes were made to the config


## Controls

#### Global
  - F1      : Events
  - F2      : State
  - F3      : Settings
  - F4      : Help
  - F12     : Reload config
  - q / esc : Quit

#### Events
  - c     : Clear event box
  - r     : Toggle raid mode
  - d     : Toggle debug mode

#### Settings
  - up    : Cycle up in selection
  - down  : Cycle down in selection
  - right : Toggle selection on
  - left  : Toggle selection off
  - space : Cycle selection

## Custom Alerting

Modify `~/.eqa/config.json` to customize alerts.

Here is a an example configuration for a given line type in the config:
```
    "line_type": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
```

There is a configuration entry for all lines matched by the parser.  If a new one is discovered, it is automatically added to the config with the values in the example above.

`line_type` here is whatever semi-arbitrary name I've given for a certain line match.  For each given line type you can configure alerts, a reaction, and a sound.

#### Reaction Values

- `false`: Disable alerting for this line type
- `true`: Alert for matching strings under `alert` for the line type, using the set sound
- `speak`: Full text-to-speech for the entire line (probably don't enable this for `combat_other_melee`
- `all`: Alert for all lines of a given line type, using the set sound

#### Alert Keys

`Alert` can be populated with key, values pairs.  The key here is any arbitrary string you would like an alert for within that line type.

For instance, the following example will alert for the word `hey` when someone else `/says` it:

```
    "say": {
      "alert": {
        "hey": "true"
      },
      "reaction": "true",
      "sound": "hey"
    },
```

#### Alert Values

- `false`: Disable alerting for the given string of a line type
- `true`: Alert for the given string of a line type
- `raid`: Alert for the given string of a line type when raid mode is enabled

#### Sound Values

- You can type anything you want as the value here and it will be the text-to-speech alert you hear when an enabled alert is found in the line type and reaction is set to true.

> One exception to this, `false` cannot be used as a text-to-speech alert, it indicates you don't want a sound alert.  This is useful if you only want something to show as an event on the display and make no sound.
