from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from .base_event import BaseEvent

@dataclass
class DataSnapshotReady(BaseEvent):
    symbol: str = ""
    df_json: str = ""  # Historical dataframe to JSON (orient='split')

@dataclass
class BarDataEvent(BaseEvent):
    symbol: str = ""
    open: float = 0.0
    high: float = 0.0
    low: float = 0.0
    close: float = 0.0
    volume: float = 0.0
    index_ts: Optional[str] = None  # ISO timestamp of bar end
