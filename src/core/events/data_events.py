
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from .base import BaseEvent

@dataclass
class DataFetchRequested(BaseEvent):
    symbol: str = "SPY"
    start: Optional[str] = None  # 'YYYY-MM-DD'
    end: Optional[str] = None    # 'YYYY-MM-DD'
    interval: str = "1d"
    source: str = "yfinance"

@dataclass
class CleanedDataReady(BaseEvent):
    symbol: str = "SPY"
    df = None  # pandas.DataFrame

@dataclass
class BarDataEvent(BaseEvent):
    symbol: str = "SPY"
    dt: datetime = None
    open: float = 0.0
    high: float = 0.0
    low: float = 0.0
    close: float = 0.0
    volume: float = 0.0
