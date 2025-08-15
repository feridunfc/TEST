
from dataclasses import dataclass
from .base import BaseEvent

@dataclass
class PortfolioUpdated(BaseEvent):
    symbol: str = "SPY"
    dt = None
    equity: float = 1.0
    position: float = 0.0
    pnl: float = 0.0
