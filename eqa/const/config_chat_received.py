NEW_LINE_CHAT_RECEIVED_CONFIG = """
{
  "line": {
    "auction": {
      "alert": {},
      "reaction": false,
      "sound": false
    },
    "auction_wtb": {
      "alert": {},
      "reaction": false,
      "sound": false
    },
    "auction_wts": {
      "alert": {
        "shiny brass idol": true
      },
      "reaction": "alert",
      "sound": "look at auction"
    },
    "auction_unknown_tongue": {
      "alert": {},
      "reaction": false,
      "sound": false
    },
    "broadcast": {
      "alert": {},
      "reaction": "solo",
      "sound": true
    },
    "group": {
      "alert": {
        "drop": "raid",
        "help": "raid",
        "inc": true,
        "invis": "raid",
        "invite": "raid",
        "oom": true
      },
      "reaction": "alert",
      "sound": "look at group"
    },
    "guild": {
      "alert": {
        "assist": "raid",
        "bump": "raid",
        "crippled": "raid",
        "dispelled": "raid",
        "feared": "raid",
        "fixated": "raid",
        "fixation": "raid",
        "harmony": "raid",
        "help": true,
        "incoming": "raid",
        "logs": "raid",
        "malo": "raid",
        "malosini": "raid",
        "occlusion": "raid",
        "off-tanking": "raid",
        "pop": "raid",
        "rampage": "raid",
        "rune": "raid",
        "sieve": "raid",
        "slow": "raid",
        "snare": "raid",
        "stand": "raid",
        "sunder": "raid",
        "tash": "raid"
      },
      "reaction": "alert",
      "sound": "look at guild"
    },
    "ooc": {
      "alert": {
        "train": "solo_group_only"
      },
      "reaction": "alert",
      "sound": "watch out"
    },
    "say": {
      "alert": {
        "help": true,
        "spot": "raid"
      },
      "reaction": "alert",
      "sound": "look at say"
    },
    "say_unknown_tongue": {
      "alert": {},
      "reaction": false,
      "sound": false
    },
    "shout": {
      "alert": {
        "train": "solo_group_only"
      },
      "reaction": "alert",
      "sound": "watch out"
    },
    "shout_unknown_tongue": {
      "alert": {},
      "reaction": false,
      "sound": false
    },
    "tell": {
      "alert": {},
      "reaction": "solo",
      "sound": true
    },
    "tell_unknown_tongue": {
      "alert": {},
      "reaction": false,
      "sound": false
    }
  },
  "version": "%s"
}
"""