from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict

from eqa.models.util import BaseFlag, Location


@dataclass
class CharacterState:
    bind: str | None
    char_class: str | None
    direction: str | None
    encumbered: bool
    guild: str | None
    level: int | None
    location: Location
    zone: str | None


@dataclass
class CharacterLog:
    char: str
    char_state: CharacterState
    character: str
    disabled: bool
    filename: str
    server: str


@dataclass
class Character:
    character_logs: Dict[str, CharacterLog] = field(
        default_factory=lambda: {}, compare=False
    )


@dataclass
class LastState:
    afk: bool
    character: str
    group: bool
    leader: bool
    raid: bool
    server: str


@dataclass
class EncounterParsing(BaseFlag):
    allow_player_target: bool
    auto_save: bool


@dataclass
class SystemPaths:
    data: str | Path
    eqalert_log: str | Path
    everquest_files: str | Path
    everquest_logs: str | Path
    sound: str | Path
    tmp_sound: str | Path


@dataclass
class PlayerData:
    persist: bool


@dataclass
class RaidMode:
    auto_set: bool


@dataclass
class LocalTTS(BaseFlag):
    model: str


@dataclass
class Speech:
    expand_lingo: bool
    gtts_lang: str
    gtts_tld: str
    local_tts: LocalTTS


@dataclass
class MobTimer:
    auto: bool
    auto_delay: int


@dataclass
class SpellTimerFilter:
    by_list: bool
    guild_only: bool
    yours_only: bool
    filter_list: Dict[str, BaseFlag] = field(default_factory=lambda: {}, compare=False)


@dataclass
class SpellTimer:
    """Generic Spell Timer data to config the behavior of the Spell Timer in EQA"""

    consolidate: bool
    delay: int
    spell_timer_filter: SpellTimerFilter
    guess: bool
    other: bool
    self: bool
    zone_drift: bool


@dataclass
class Timers:
    mob: MobTimer
    spell: SpellTimer


@dataclass
class Settings:
    character_mention_alert: BaseFlag
    consider_eval: BaseFlag
    debug_mode: BaseFlag
    detect_character: BaseFlag
    encounter_parsing: EncounterParsing
    mute: BaseFlag
    paths: SystemPaths
    player_data: PlayerData
    raid_mode: RaidMode
    speech: Speech
    timers: Timers


@dataclass
class Setting:
    last_state: LastState
    settings: Settings
    version: str


@dataclass
class Zone:
    indoors: bool
    raid_mode: bool
    timer: int


@dataclass
class Zones:
    zones: Dict[str, Zone] = field(default_factory=lambda: {}, compare=False)


@dataclass
class LineAlert:
    reaction: str
    sound: bool
    alert: Dict[str, str] = field(default_factory=lambda: {}, compare=False)


@dataclass
class LineAlerts:
    line: Dict[str, LineAlert] = field(default_factory=lambda: {}, compare=False)


@dataclass
class LineAlertFile:
    line_alert: LineAlerts


@dataclass
class Config:
    characters: Character
    settings: Setting
    zones: Zones
    line_alerts: Dict[str, LineAlertFile] = field(
        default_factory=lambda: {}, compare=False
    )
