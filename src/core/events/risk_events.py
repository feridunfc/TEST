
from dataclasses import dataclass
from .base import BaseEvent
from .strategy_events import SignalDirection

@dataclass
class RiskAssessmentCompleted(BaseEvent):
    symbol: str = "SPY"
    dt = None
    desired_position: float = 0.0  # target gross exposure (-1..+1)
    rationale: str = ""
