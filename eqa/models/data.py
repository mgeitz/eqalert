from dataclasses import dataclass, field
from typing import Dict


@dataclass
class SpellTimer:
    """Spell Timer Data"""

    cast_time: str
    duration: str
    formula: str


@dataclass
class SpellTimerJSON:
    hash: str
    version: str
    spells: Dict[str, SpellTimer] = field(default_factory=lambda: {}, compare=False)
