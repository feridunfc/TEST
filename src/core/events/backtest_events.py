
from dataclasses import dataclass
from .base import BaseEvent

@dataclass
class BacktestRequested(BaseEvent):
    symbol: str = "SPY"
    start: str = "2018-01-01"
    end: str = "2024-12-31"
    interval: str = "1d"
    strategy: str = "ma_crossover"
    params: dict = None

@dataclass
class BacktestCompleted(BaseEvent):
    symbol: str = "SPY"
    strategy: str = "ma_crossover"
    results: dict = None  # metrics etc.
