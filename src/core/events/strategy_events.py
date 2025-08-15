
from dataclasses import dataclass
from enum import IntEnum
from .base import BaseEvent

class SignalDirection(IntEnum):
    SHORT = -1
    FLAT = 0
    LONG = 1

@dataclass
class FeaturesReady(BaseEvent):
    symbol: str = "SPY"
    dt = None
    features: dict = None  # e.g., { 'sma_fast': 100, 'sma_slow': 120, 'ret': 0.001 }

@dataclass
class StrategySignalGenerated(BaseEvent):
    symbol: str = "SPY"
    dt = None
    signal: SignalDirection = SignalDirection.FLAT
    meta: dict = None  # e.g., thresholds, model_name, params
