from __future__ import annotations
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Dict, Optional
import pandas as pd

class SignalDirection(IntEnum):
    SHORT = -1
    HOLD  = 0
    LONG  = 1

@dataclass
class BacktestRequested:
    source: str
    symbol: str
    start: Optional[str] = None
    end: Optional[str] = None
    interval: str = "1d"
    wf_train: int = 252
    wf_test: int = 63
    mode: str = "walkforward"

@dataclass
class BacktestCompleted:
    source: str
    symbol: str
    results: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BarDataEvent:
    source: str
    symbol: str
    timestamp: pd.Timestamp
    open: float
    high: float
    low: float
    close: float
    volume: float
    is_train: bool

@dataclass
class FeaturesReady:
    source: str
    symbol: str
    timestamp: pd.Timestamp
    features: Dict[str, float]

@dataclass
class StrategySignalGenerated:
    source: str
    symbol: str
    timestamp: pd.Timestamp
    direction: SignalDirection
    strength: float = 1.0
    meta: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RiskAssessmentCompleted:
    source: str
    symbol: str
    timestamp: pd.Timestamp
    direction: SignalDirection
    quantity: float
    entry_price: float

@dataclass
class OrderFilled:
    source: str
    symbol: str
    timestamp: pd.Timestamp
    direction: SignalDirection
    quantity: float
    fill_price: float

@dataclass
class PortfolioUpdated:
    source: str
    timestamp: pd.Timestamp
    equity: float
    cash: float
    positions: Dict[str, float] = field(default_factory=dict)
