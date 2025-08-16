
from dataclasses import dataclass
from typing import Dict, Any
import pandas as pd

@dataclass
class BacktestRequested:
    source: str
    df: pd.DataFrame
    strategy_name: str
    params: Dict[str, Any]

@dataclass
class BacktestCompleted:
    source: str
    summary: Dict[str, Any]
