
from dataclasses import dataclass
from datetime import datetime
from .base import BaseEvent

@dataclass
class PortfolioUpdated(BaseEvent):
    equity: float
    weight: float
    drawdown: float
