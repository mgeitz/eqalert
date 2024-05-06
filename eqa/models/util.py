from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Location:
    x: str = "0.00"
    y: str = "0.00"
    z: str = "0.00"


@dataclass
class BaseFlag:
    enabled: bool
