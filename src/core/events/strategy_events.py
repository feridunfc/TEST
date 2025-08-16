
from dataclasses import dataclass
from enum import IntEnum
from .base import BaseEvent

class SignalDirection(IntEnum):
    SHORT = -1
    HOLD = 0
    LONG = 1

@dataclass
class StrategySignalGenerated(BaseEvent):
    symbol: str = ""
    direction: SignalDirection = SignalDirection.HOLD
    strength: float = 0.0  # [-1,1]
    price: float = 0.0
    info: dict = None
