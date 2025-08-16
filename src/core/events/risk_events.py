from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any
from .base_event import BaseEvent
from .strategy_events import SignalDirection

@dataclass
class RiskAssessmentCompleted(BaseEvent):
    symbol: str = ""
    strategy_name: str = ""
    direction: SignalDirection = SignalDirection.HOLD
    position_size_pct: float = 0.0  # NEW: portfolio % to allocate (signed)
    stop_loss_price: float = 0.0
    take_profit_price: float = 0.0
    rationale: str = ""
    price: float = 0.0
