
from dataclasses import dataclass
import pandas as pd
from .base import BaseEvent

@dataclass
class BacktestRequested(BaseEvent):
    asset_name: str = ""
    strategy_name: str = "hybrid_v1"
    df: pd.DataFrame = None
    wf_cfg: object = None
    feature_cfg: dict = None
    backtest_params: dict = None

@dataclass
class BacktestCompleted(BaseEvent):
    asset_name: str = ""
    strategy_name: str = ""
    summary: dict = None
