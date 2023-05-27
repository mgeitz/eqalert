# EQAlert

A Configurable and Context Driven Project 1999 Log Parser with NCurses Interface for Linux

![img](https://i.imgur.com/TtUwq12.png)

> Best used with the [Linux EQ Launch Manager](https://gist.github.com/mgeitz/aa295061c51b26d53dd818d0ebb3e37a) to maintain reasonable log file size


## Install

Install from pypi
```sh
$ pip3 install eqalert
```

_or_ install manually to your host machine
```sh
$ git clone git@github.com:mgeitz/eqalert.git
$ cd eqalert
$ python3 -m pip install -e .
```

_or_ install and run through docker
```sh
$ git clone git@github.com:mgeitz/eqalert.git
$ cd eqalert
$ docker compose build
$ docker compose run eqalert
```

> Note: If running through docker after installing and running on your host, update or regenerate `~/.eqa/config/settings.json` to reflect local container paths in `/home/eqalert`

## Getting Started

Start things up
```sh
$ eqalert
```

You should now see `~/.eqa/` with the following structure
```
$HOME/.eqa
        ⎿ config/
          ⎿ line-alerts/
        ⎿ data/
        ⎿ encounters/
        ⎿ log/
          ⎿ debug/
        ⎿ sound/
```

Spot check these default paths generated in `config/settings.json`
```
  "settings": {
    "paths": {
      "eqalert_log": "[$HOME/.eqa/]log/",
      "data": "[$HOME/.eqa/]data/",
      "encounter": "[$HOME/.eqa/]encounters/",
      "everquest_logs": "[$HOME]/.wine/drive_c/Program Files/Sony/EverQuest/Logs/",
      "everquest_files": "[$HOME]/.wine/drive_c/Program Files/Sony/EverQuest/",
      "sound": "[$HOME/.eqa/]sound/",
      "tmp_sound": "/tmp/eqa/sound/"
    },
```
> Press `0` to reload your configs or restart the program if any changes were made.  Though generally, it's a good idea to stop eqalert before manually editing your config files.

## Data

### Spell Timers

EQ Alert will generate a file for spell timers in `data/spell-timers.json` by default by parsing `spells_us.txt` in your EverQuest directory.

This file will only regenerate if it is missing, malformed, or a newer `spells_us.txt` file is present.

### Spell Casters

EQ Alert will generate/overwrite `data/spell-casters.json` each version.  This file contains which classes can cast a given buff which timers should be made for.

### Spell Lines

Many spells cast in EverQuest share the same log output lines.  EQ Alert will generate/overwrite `data/spell-lines.json` each version as a mapping of which possible spells a given output line could be associated to.

### Players

EQ Alert uses in-game `/who` output to keep an up-to-date list of each seen players class, level, and guild organized by server in `data/players.json` for alerting spell duration.


## Controls

### Keyboard Controls

#### Global
  - 0       : Reload config
  - 1       : Events
  - 2       : State
  - 3       : Parse
  - 4       : Settings
  - q / esc : Quit
  - h       : Help

#### Events
  - c       : Clear event box
  - d       : Toggle debug mode
  - e       : Toggle encounter parsing
  - m       : Toggle global audio mute
  - p       : Toggle encounter parse save
  - r       : Toggle raid mode
  - t       : Toggle automatic mob respawn timers

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

#### Settings

`/say parser raid` - Toggle raid mode

`/say parser debug` - Toggle debug mode

#### Mute

`/say parser mute/unmute` - Toggle global mute/unmute

`/say parser mute/unmute speak` - Toggle mute/unmute on all `speak` alerts.

`/say parser mute/unmute alert` - Toggle mute/unmute on all `alert` alerts.

`/say parser mute/unmute line` - Mute all sound alerts from a type of line

> example: /say parser mute engage

`/say parser mute/unmute line player` - Mute all sound alerts of a given line type from a specific source

> example: /say parser mute tell indef

`/say parser mute clear` - Clear all muted line types and players

> Does not effect global mute

#### Encounters

`/say parser encounter` - Toggle encounter parsing

`/say parser encounter clear` - Clear the encounter stack

`/say parser encounter end` - Sometimes, your logs don't catch an encounter end.  Use this command to fix that!

#### Timers

`/say parser metronome [seconds]` - Set a tick/tock metronome with interval of [seconds]

`/say parser metronome stop` - Stop the metronome

`/say parser timer [seconds]` - Set a timer for [seconds], says "times up" when done

`/say parser timer clear` - Clear all timers

`/say parser timer respawn` - Create timers for the default current zone time after seeing an experience message. Timer response is "pop [zone name]"

`/say parser timer respawn stop` - Stop creating mob respawn timers automatically

#### Misc

`/say parser consider` - Toggle consider evaluation

`/say parser what context` - Speak context state

`/say parser what state` - Speak *everything* in the state object

`/say parser hello` - Hello

`/say parser who [player_name]` - Speaks player level, class, and guild if known

`/say parser where` - Where am I?


## Settings & Options

Settings and options can be modified in `config/settings.json`

- `consider eval`: Speak "safe" or "danger" based on consider output
- `debug mode`: Slows down parser performance and produces lots of file output
- `detect character`: Automatically set parser to listen to the most recently active eqlog
- `encounter parsing`: Parse encounter damage
- `encounter parsing auto save`: Save verbose encounter parse results to a file
- `mute`: Disable all text-to-speech output
- `speech expand lingo`: When speaking a line, replace common EQ abbreviations with complete words
- `speech tld`: Top-level domain for the Google Translate host - [gTTS documentation reference](https://gtts.readthedocs.io/en/latest/module.html)
- `speech lang`: The language (IETF language tag) to read the text in - [gTTS documentation reference](https://gtts.readthedocs.io/en/latest/module.html)
- `auto mob timer`: Create timer events after gaining experience for a duration based on the zone you are in
- `auto mob timer delay`: Set a delay for the auto mob timer notification n seconds before the actual event
- `spell timer delay`: Set a delay for all spell timer notifications n seconds before the actual event
- `spell timer guess`: If there is moderate uncertainty in guessing a spell, go for it
- `spell timer other`: Set spell timers for spells that land on other players
- `spell timer guild only`: Filter all spell timer events so they are only for yourself or guild members
- `spell timer self`: Set spell timers for spells that land on yourself
- `persist player data`: Save /who player output for spell timers
- `spell timer yours only`: Filter all spell timer events to be only spells you cast
- `spell timer zone drift`: If enabled add time between zoning to spell timers targetting yourself


## Custom Alerting

Modify `~/.eqa/config/line-alerts/*.json` to customize alerts.

Due to how many line matches there are, the configuration for their reactions have been split into several json files under `[$HOME/.eqa]/config/line-alerts/*.json`

Anything matched by the parser not found in configuration is automatically added to `[$HOME/.eqa]/config/line-alerts/other.json`

Modify `line_type` values to customize alerts accordingly.

### Line Types

Example configuration for a line type:
```
    "line_type_name": {
      "alert": {},
      "reaction": "false",
      "sound": "false"
    },
```

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
Zone data is stored in `config/zones.json`

#### raid_mode
- `false`: If enabled, auto-disable raid mode in this zone
- `true`: If enabled, auto-enable raid mode in this zone

#### timer
- `#`: The value in seconds to associate to a default timer in a given zone

> Note: No support for zones with multiple default timers, stick with the manual timer command for those for now.  For zones with tiered default timers, the shortest timer was set as the default.  You can change this value to be any number in seconds you prefer.
