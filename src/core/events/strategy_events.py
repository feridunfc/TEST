from __future__ import annotations
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Dict, Any
from .base_event import BaseEvent

class SignalDirection(IntEnum):
    SHORT = -1
    HOLD = 0
    LONG = 1

@dataclass
class FeaturesReady(BaseEvent):
    symbol: str = ""
    features_json: str = ""  # bar-aligned features (single row) to JSON

@dataclass
class StrategySignalGenerated(BaseEvent):
    symbol: str = ""
    strategy_name: str = ""
    direction: SignalDirection = SignalDirection.HOLD
    price: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
