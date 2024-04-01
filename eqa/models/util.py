from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Location:
    x: float
    y: float
    z: float


@dataclass
class BaseFlag:
    enabled: bool
