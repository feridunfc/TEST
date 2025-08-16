
from dataclasses import dataclass
from .base import BaseEvent
from .strategy_events import SignalDirection

@dataclass
class RiskAssessmentCompleted(BaseEvent):
    symbol: str = ""
    direction: SignalDirection = SignalDirection.HOLD
    quantity: float = 0.0
    price: float = 0.0
    rationale: str = ""
