
from dataclasses import dataclass
import pandas as pd

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
