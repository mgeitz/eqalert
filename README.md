# EQAlert

A Configurable and Context Driven Project 1999 Log Parser with NCurses Interface for Linux

![img](https://i.imgur.com/TtUwq12.png)

> Best used with the [Linux EQ Launch Manager](https://gist.github.com/mgeitz/aa295061c51b26d53dd818d0ebb3e37a) to maintain reasonable log file size


## Install

Install from pypi
```sh
$ pip3 install eqalert
```

_or_ install manually from github
```sh
$ git clone git@github.com:mgeitz/eqalert.git
$ cd eqalert
$ python3 setup.py install --user
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
        ⎿ data/
        ⎿ encounters/
        ⎿ log/
          ⎿ debug/
        ⎿ sound/
```

Spot check these default paths generated in `config.json`
```
    "settings": {
        "paths": {
            "alert_log": "[$HOME/.eqa/]log/",
            "data": "[$HOME/.eqa/]data/",
            "encounter": "[$HOME/.eqa/]encounters/",
            "char_log": "[$HOME]/.wine/drive_c/Program Files/Sony/EverQuest/Logs/",
            "sound": "[$HOME/.eqa/]sound/",
            "tmp_sound": "/tmp/eqa/sound/"
        },
```

> Press `0` to reload your config or restart the program if any changes were made to the config


## Controls

### Keyboard Controls

#### Global
  - 1       : Events
  - 2       : State
  - 3       : Parse
  - 4       : Settings
  - 0       : Reload config
  - q / esc : Quit
  - h       : Help

#### Events
  - c       : Clear event box
  - r       : Toggle raid mode
  - d       : Toggle debug mode
  - e       : Toggle encounter parsing
  - m       : Toggle global audio mute

#### Settings
  - up      : Up in selection
  - down    : Down in selection
  - right   : Selection options
  - left    : Selection options
  - space   : Select
  - enter   : Select
  - tab     : Cycle category

> Note: WASD or arrow keys will work

### Say Controls

You can control some parser settings using `/say` in-game.  This is better suited for one monitor setups.

`/say parser raid` - Toggle raid mode

`/say parser debug` - Toggle debug mode

`/say parser mute/unmute` - Toggle global mute/unmute

`/say parser mute/unmute speak` - Toggle mute/unmute on all `speak` alerts.

`/say parser mute/unmute alert` - Toggle mute/unmute on all `alert` alerts.

`/say parser mute/unmute line` - Mute all sound alerts from a type of line

> example: /say parser mute engage

`/say parser mute/unmute line player` - Mute all sound alerts of a given line type from a specific source

> example: /say parser mute tell indef

`/say parser mute clear` - Clear all muted line types and players

> Does not effect global mute

`/say parser encounter` - Toggle encounter parsing

`/say parser encounter clear` - Clear the encounter stack

`/say parser encounter end` - Sometimes, your logs don't catch an encounter end.  Use this command to fix that!

`/say parser hello`

`/say parser who`

`/say parser where`

`/say parser what state`

`/say parser metronome [seconds]`

`/say parser metronome stop`

`/say parser timer [seconds]`

`/say parser timer clear`


## Custom Alerting

Modify `~/.eqa/config.json` to customize alerts.

### Line Types

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

##### General
- `false`: Disable alerting for this line type
- `alert`: Alert for matching strings in `alert` for the line type using the set sound
- `all`: Alert for all lines of a given line type using the set sound

##### Context Driven
- `solo`: Alert when solo, grouped, and raiding
- `solo_only`: Alert only when solo
- `group`: Alert when in a group and raiding
- `group_only`: Alert only when grouped
- `solo_group_only`: Alert only when not raiding
- `raid`: Alert when in a raid
- `afk`: Alert only when afk

#### Alert Keys

`alert` can be populated with key value pairs.  The key here is any string you would like an alert for within that line type.

##### Examples

###### Example 1
Alert for the word `hey` when someone else `/says` it:

```
    "say": {
      "alert": {
        "hey": "true"
      },
      "reaction": "alert",
      "sound": "hey"
    },
```

###### Example 2
Alert for the word `run` when someone else `/says` it and you are grouped or in a raid:

```
    "say": {
      "alert": {
        "run": "group"
      },
      "reaction": "alert",
      "sound": "oh god run"
    },
```

###### Example 4
Alert for a spell not taking hold only when grouped:

```
    "spell_not_hold": {
      "alert": {},
      "reaction": "group_only",
      "sound": "true"
    },
```

###### Example 4
Alert for the item `Hand Made Backpack` when someone else `/auctions` it and is selling:

```
    "auction_wts": {
      "alert": {
        "Hand Made Backpack": "true"
      },
      "reaction": "alert",
      "sound": "wow buy that"
    },
```

> More examples can be referenced in the default config

#### Alert Values

##### General
- `false`: Disable alerting for the string (does not negate line type reactions)
- `true`: Alert for the string

##### Context Driven
- `solo`: Alert when solo, grouped, and raiding
- `solo_only`: Alert only when solo
- `group`: Alert when in a group and raiding
- `group_only`: Alert only when grouped
- `solo_group_only`: Alert only when not raiding
- `raid`: Alert when in a raid
- `afk`: Alert only when afk

#### Sound Values
- `true`: When an alert is raised speak the entire line
- `false`: Play no sound when an alert is raised

> Any other sound value will be spoken as the audio trigger for that line type

#### The all Line Type

This line type behaves the same as any specific line type configuration, but configuration here will be used against all log lines.

For example, the below configuration will alert if the word `help` is found in any line while in a raid context, even if that line isn't matched to a type by the parser.

```
    "all": {
      "alert": {
        "help": raid
      },
      "reaction": "alert",
      "sound": "help is needed"
    },
```

This can be helpful if you would like to alert for something not yet matched by the parser, though your [contribution](CONTRIBUTING.md#pull-requests) to a new line type match in the parser would also be welcome!

### Zones

- `false`: Considered a non-raid zone
- `raid`: Parser raid mode will auto-enable in this zone
