
from dataclasses import dataclass
from .base import BaseEvent

@dataclass
class PortfolioUpdated(BaseEvent):
    cash: float = 0.0
    total_value: float = 0.0
    positions: dict = None
