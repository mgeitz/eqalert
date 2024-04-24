from pathlib import Path

import pytest
from eqa.lib.config import (
    add_char_log,
    combine_config_files,
    convert_character_config_to_legacy_config,
    create_character_config,
    generate_spell_timer_json,
    SpellTimerJSON,
    SpellTimer,
    read_config_files,
    read_line_alert_files,
)
from eqa.lib.struct import config_file, configs
from eqa.lib.util import JSONFileHandler
from eqa.const.validspells import VALID_SPELLS
from eqa.models.config import CharacterLog, CharacterState

sample_spell_lines = [
    "0^^BLUE_TRAIL^^^^^^^0^0^0^0^0^0^0^7^65^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^-1^-1^-1^-1^1^1^1^1^-1^-1^-1^-1^100^100^100^100^100^100^100^100^100^100^100^100^0^0^0^0^254^254^254^254^254^254^254^254^254^254^254^254^2^0^52^-1^0^0^255^255^255^255^255^255^255^255^255^255^255^255^255^255^255^255^44^13^0^-1^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^100^0^161^0^0^-150^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^100^0^0^0^0^0^0^0^0^0^0^0^0^0^-150^100^-150^-99^7^65^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^1^0^0^0^0^0^0^-1^0^0^0^1^0^0^1^1^^0",
    "3^Summon Corpse^PLAYER_1^^^^^^^10000^0^0^0^5000^2250^12000^0^0^0^700^70^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^2512^2106^17355^-1^-1^-1^1^1^1^1^-1^-1^-1^-1^100^100^100^100^100^100^100^100^100^100^100^100^0^1^0^0^91^254^254^254^254^254^254^254^254^254^254^254^6^20^14^-1^0^0^255^255^255^255^255^255^255^255^255^255^39^255^255^255^255^255^43^0^0^4^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^100^0^35^83^0^0^0^0^0^0^0^0^0^0^0^64^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^5^101^49^52^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^1^0^0^0^0^0^-1^0^0^0^1^0^0^1^1^!Expansion:Jan2001^8478",
    "4^Summon Waterstone^PLAYER_1^^^^^^^0^0^0^0^4000^2250^2250^0^0^0^40^10342^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^2512^2106^-1^-1^-1^-1^1^1^1^1^-1^-1^-1^-1^109^100^100^100^100^100^100^100^100^100^100^100^0^1^0^0^32^254^254^254^254^254^254^254^254^254^254^254^6^25^14^-1^0^0^255^255^255^255^255^255^255^255^255^255^255^255^20^255^255^255^43^0^0^4^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^100^0^35^83^0^0^0^0^0^0^0^0^0^0^0^109^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^5^101^20^61^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^1^0^0^0^0^0^-1^0^0^0^1^0^0^1^1^^0",
    "5^Cloak^PLAYER_1^^^^^ shimmers.^^100^0^0^0^5000^2250^0^3^200^0^50^1^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^2502^2115^-1^-1^-1^-1^1^1^1^1^-1^-1^-1^-1^100^100^100^100^100^100^100^100^100^100^100^100^0^1^0^0^90^254^254^254^254^254^254^254^254^254^254^254^14^25^18^-1^0^0^255^255^255^255^255^255^255^255^255^255^255^255^255^255^255^255^42^0^0^9^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^100^0^138^95^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^100^0^-99^3^200^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^1^1^0^0^0^0^0^-1^0^0^0^1^0^0^1^1^^0",
    "6^Ignite Blood^PLAYER_1^^^^Your blood ignites.^'s blood ignites.^Your blood cools.^200^0^0^0^4000^2500^2250^1^21^0^250^-56^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^2503^2119^-1^-1^-1^-1^1^1^1^1^-1^-1^-1^-1^100^100^100^100^100^100^100^100^100^100^100^100^0^0^0^2^0^254^254^254^254^254^254^254^254^254^254^254^5^25^5^-1^0^0^255^255^255^255^255^255^255^255^255^255^49^255^255^255^255^255^44^13^0^20^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^100^0^142^89^0^-100^0^0^0^0^0^0^0^0^0^38^0^0^-1^-1^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^-12^133^-157^129^1^21^0^0^0^0^2^106^0^0^0^0^0^0^0^0^0^0^1^0^0^0^0^0^0^-1^0^0^0^1^0^0^1^1^^0",
    "7^Hymn of Restoration^PLAYER_1^^^^Your wounds begin to heal.^^^0^30^0^0^3000^0^0^5^3^0^0^1^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^2510^2007^-1^-1^-1^-1^1^1^1^1^-1^-1^-1^-1^110^100^100^100^100^100^100^100^100^100^100^100^0^1^0^0^0^254^254^254^254^254^254^254^254^254^254^254^41^15^49^-1^0^0^255^255^255^255^255^255^255^6^255^255^255^255^255^255^255^255^40^0^0^6^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^67^1^0^0^0^0^0^0^0^0^0^0^0^43^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^5^101^13^25^5^3^0^0^1^0^0^0^0^0^0^0^0^0^0^0^0^0^0^1^0^0^0^0^0^-1^0^0^0^1^0^0^1^1^^0",
    "8^Cleanse^PLAYER_1^^^^You feel cleansed.^^^0^0^0^0^0^0^0^0^0^0^0^-1^-1^5^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^2510^2051^-1^-1^-1^-1^1^1^1^1^-1^-1^-1^-1^100^100^100^100^100^100^100^100^100^100^100^100^0^1^0^0^36^35^0^254^254^254^254^254^254^254^254^254^6^0^5^-1^0^0^255^255^255^255^255^255^255^255^255^255^255^255^255^255^255^255^43^0^0^50^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^100^0^25^97^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^100^0^-99^0^0^0^0^0^1^0^0^0^0^0^0^0^0^0^0^0^0^0^1^0^0^0^0^0^-1^0^0^0^1^0^0^1^1^^0",
    "9^Superior Healing^PLAYER_1^^^^You feel much better.^ feels much better.^^100^0^0^0^4500^2500^2250^0^0^0^250^463^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^583^0^0^0^0^0^0^0^0^0^0^0^2510^2051^-1^-1^-1^-1^1^1^1^1^-1^-1^-1^-1^104^100^100^100^100^100^100^100^100^100^100^100^0^1^0^0^0^254^254^254^254^254^254^254^254^254^254^254^5^25^5^-1^0^0^255^34^57^255^255^53^255^255^255^53^255^255^255^255^255^255^43^0^0^1^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^100^0^131^73^0^0^0^0^0^0^0^0^0^0^0^42^0^0^0^0^0^100^0^0^0^0^0^0^0^0^0^0^0^0^0^5^101^47^20^0^0^0^0^0^0^5^583^0^0^0^0^0^0^0^0^0^0^0^1^0^0^0^0^0^-1^0^0^0^1^0^0^1^1^!Expansion:Feb2001^8631",
    "10^Augmentation^PLAYER_1^^^^You feel your body pulse with energy.^'s body pulses with energy.^The pulsing energy fades.^100^0^0^0^5000^2250^2250^3^270^0^90^115^5^5^-2^1^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^128^30^30^0^100^0^0^0^0^0^0^0^2518^2124^-1^-1^-1^-1^1^1^1^1^-1^-1^-1^-1^109^101^101^100^203^100^100^100^100^100^100^100^0^1^0^0^11^6^1^24^148^254^254^254^254^254^254^254^5^25^5^-1^0^0^255^255^255^255^255^255^255^255^255^255^255^255^255^29^255^255^43^0^0^7^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^100^0^132^88^0^0^0^0^0^0^0^0^0^0^0^41^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^0^5^101^24^202^3^270^0^0^0^0^3^230^0^0^0^0^0^0^0^0^0^0^1^1^0^0^0^0^0^-1^0^0^0^1^0^0^1^1^^0",
]


def test_generate_spell_timer_json():
    sample_hash = "abcd1234"
    valid_spells = VALID_SPELLS
    version = "1.0"
    spells = {
        "augmentation": SpellTimer("5.0", "270", "3"),
        "hymn_of_restoration": SpellTimer("3.0", "3", "5"),
        "ignite_blood": SpellTimer("4.0", "21", "1"),
    }
    expected = SpellTimerJSON(hash=sample_hash, version=version, spells=spells)

    actual = generate_spell_timer_json(
        sample_hash, sample_spell_lines, valid_spells, version
    )

    # Compare the parent classes (does not check the spells)
    assert expected == actual

    # Compare that all the expected spells are present
    assert sorted(expected.spells.keys()) == sorted(actual.spells.keys())


def test_read_config_files():

    read_result = {"foo": {"bar": "baz"}}

    class TestJSONFileHandler(JSONFileHandler):
        def read(self):
            # Short circuiting the file read operation
            return read_result

    test_file_path = Path("whatever")
    test_config_files = ["test_valid"]

    expected = {
        "test_valid": config_file(
            "test_valid", "whatever/test_valid.json", {"foo": {"bar": "baz"}}
        )
    }
    actual = read_config_files(test_file_path, test_config_files, TestJSONFileHandler)

    assert actual == expected


@pytest.mark.parametrize(
    "file_handler_result, expected",
    [
        (
            {"line": {"foo": {"bar": "baz"}}},
            {"line": {"foo": {"bar": "baz"}}, "version": None},
        ),
        (
            {"line": {"foo": {"bar": "baz"}}, "version": "1.2.3"},
            {"line": {"foo": {"bar": "baz"}}, "version": "1.2.3"},
        ),
    ],
)
def test_read_line_alert_files(file_handler_result, expected):

    class TestJSONFileHandler(JSONFileHandler):
        def read(self):
            # Short circuiting the file read operation
            return file_handler_result

    test_file_path = Path("whatever")
    test_config_files = ["test_valid"]

    actual = read_line_alert_files(
        test_file_path, test_config_files, TestJSONFileHandler
    )

    assert actual == expected


def test_combine_config_files():

    configs_data = {
        "characters": config_file(
            "characters", "whatever/characters.json", {"foo": {"bar": "baz"}}
        ),
        "settings": config_file(
            "settings", "whatever/characters.json", {"foo": {"bar": "baz"}}
        ),
        "zones": config_file(
            "zones", "whatever/characters.json", {"foo": {"bar": "baz"}}
        ),
    }

    line_alerts = {"line": {"foo": {"bar": "baz"}}, "version": "1.2.3"}
    line_alerts_config = config_file(
        "line-alerts",
        None,
        line_alerts,
    )

    expected = configs(
        configs_data["characters"],
        configs_data["settings"],
        configs_data["zones"],
        line_alerts_config,
    )

    actual = combine_config_files(configs_data, line_alerts)

    assert actual == expected


sample_character = {
    "WTF_P1999Green": {
        "character": "WTF",
        "server": "P1999Green",
        "file_name": "eqlog_Wtf_P1999Green.txt",
        "disabled": False,
        "char_state": {
            "location": {"x": "0.00", "y": "0.00", "z": "0.00"},
            "direction": None,
            "zone": None,
            "encumbered": False,
            "bind": None,
            "level": None,
            "class": None,
            "guild": None,
        },
    }
}


@pytest.mark.parametrize(
    "existing_character",
    [
        {},
        sample_character,
    ],
)
def test_add_char_log(existing_character):
    char = "test_char"
    server = "test_server"

    config_characters = config_file(
        name="test_char_config",
        path="whatever",
        config={"char_logs": existing_character},
    )

    config = configs(characters=config_characters, settings={}, zones={}, alerts={})
    char_log = add_char_log(char, server, config)
    assert type(char_log) is CharacterLog

    actual = config.characters.config

    expected = {
        "char_logs": {
            "test_char_test_server": {
                "character": "test_char",
                "server": "test_server",
                "file_name": "eqlog_Test_Char_test_server.txt",
                "disabled": False,
                "char_state": {
                    "location": {"x": "0.00", "y": "0.00", "z": "0.00"},
                    "direction": None,
                    "zone": None,
                    "encumbered": False,
                    "bind": None,
                    "level": None,
                    "class": None,
                    "guild": None,
                },
            },
        }
    }

    expected["char_logs"].update(existing_character)

    assert actual == expected


def test_add_char_log_does_not_create_if_character_exists():
    char = "test_char"
    server = "test_server"

    # Note: disabled is set to non-default "True"
    # If the config is somwhow overwritten with new character, this test will fail
    existing_character = {
        "test_char_test_server": {
            "character": "test_char",
            "server": "test_server",
            "file_name": "eqlog_Test_Char_test_server.txt",
            "disabled": True,
            "char_state": {
                "location": {"x": "0.00", "y": "0.00", "z": "0.00"},
                "direction": None,
                "zone": None,
                "encumbered": False,
                "bind": None,
                "level": None,
                "class": None,
                "guild": None,
            },
        },
    }

    config_characters = config_file(
        name="test_char_config",
        path="whatever",
        config={"char_logs": existing_character},
    )

    config = configs(characters=config_characters, settings={}, zones={}, alerts={})
    char_log = add_char_log(char, server, config)
    assert char_log is None

    actual = config.characters.config

    expected = {
        "char_logs": {
            "test_char_test_server": {
                "character": "test_char",
                "server": "test_server",
                "file_name": "eqlog_Test_Char_test_server.txt",
                "disabled": True,
                "char_state": {
                    "location": {"x": "0.00", "y": "0.00", "z": "0.00"},
                    "direction": None,
                    "zone": None,
                    "encumbered": False,
                    "bind": None,
                    "level": None,
                    "class": None,
                    "guild": None,
                },
            },
        }
    }

    assert actual == expected


def test_create_character_config():
    character = "test_char"
    server = "test_server"

    expected = CharacterLog(
        char_state=CharacterState(),
        character=character,
        file_name="eqlog_" + character.title() + "_" + server + ".txt",
        server=server,
    )

    actual = create_character_config(char=character, server=server)

    assert actual == expected


def test_convert_character_dataclass_to_legacy_config():
    character = "test_char"
    server = "test_server"

    character_config = create_character_config(char=character, server=server)

    actual = convert_character_config_to_legacy_config(character_config)

    expected = {
        f"{character}_{server}": {
            "character": character,
            "server": server,
            "file_name": f"eqlog_{character.title()}_{server}.txt",
            "disabled": False,
            "char_state": {
                "location": {"x": "0.00", "y": "0.00", "z": "0.00"},
                "direction": None,
                "zone": None,
                "encumbered": False,
                "bind": None,
                "level": None,
                "class": None,
                "guild": None,
            },
        }
    }

    assert actual == expected
