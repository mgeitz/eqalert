NEW_SETTINGS_CONFIG = """
{
  "last_state": {},
  "settings": {
    "character_mention_alert": {
      "enabled": true
    },
    "consider_eval": {
      "enabled": true
    },
    "debug_mode": {
      "enabled": false
    },
    "detect_character": {
      "enabled": true
    },
    "encounter_parsing": {
      "auto_save": false,
      "allow_player_target": false,
      "enabled": true
    },
    "mute": {
      "enabled": false
    },
    "paths": {
      "eqalert_log": "%slog/",
      "data": "%sdata/",
      "everquest_logs": "%s/.wine/drive_c/Program Files/Sony/EverQuest/Logs/",
      "everquest_files": "%s/.wine/drive_c/Program Files/Sony/EverQuest/",
      "sound": "%ssound/",
      "tmp_sound": "/tmp/eqa/sound/"
    },
    "player_data": {
      "persist": true
    },
    "raid_mode": {
      "auto_set": true
    },
    "speech": {
      "expand_lingo": true,
      "gtts_tld": "com",
      "gtts_lang": "en",
      "local_tts": {
        "enabled": false,
        "model": "tts_models/en/ljspeech/tacotron2-DDC_ph"
      }
    },
    "timers": {
      "mob": {
        "auto": false,
        "auto_delay": 10
      },
      "spell": {
        "filter": {
          "by_list": false,
          "filter_list": {
            "spirit_of_wolf": false
          },
          "guild_only": false,
          "yours_only": false
        },
        "consolidate": true,
        "delay": 24,
        "guess": false,
        "other": true,
        "self": true,
        "zone_drift": true
      }
    }
  },
  "version": "%s"
}
"""