from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from .base_event import BaseEvent

@dataclass
class BacktestRequested(BaseEvent):
    symbol: str = "SPY"
    start: Optional[str] = None
    end: Optional[str] = None
    interval: str = "1d"
    strategy_names: List[str] = field(default_factory=lambda: ["sma_crossover"])
    mode: str = "simple"  # "simple" or "walkforward"
    wf_train: int = 252
    wf_test: int = 63

@dataclass
class BacktestCompleted(BaseEvent):
    symbol: str = ""
    strategy_names: List[str] = field(default_factory=list)
    mode: str = "simple"
    results: Dict[str, Any] = field(default_factory=dict)
