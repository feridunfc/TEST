from __future__ import annotations
from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Dict

class SignalDirection(IntEnum):
    SELL = -1
    HOLD = 0
    BUY = 1

@dataclass(frozen=True)
class StrategySignalGenerated:
    strategy_id: str
    symbol: str
    direction: SignalDirection
    strength: float
    metadata: Dict[str, Any] | None = None
