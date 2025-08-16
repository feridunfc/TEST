
from dataclasses import dataclass
from datetime import datetime
from .base import BaseEvent

@dataclass
class OrderFilled(BaseEvent):
    symbol: str
    filled_weight: float
    fill_price: float
