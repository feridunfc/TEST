
from dataclasses import dataclass
import pandas as pd
from .base import BaseEvent

@dataclass
class BarDataEvent(BaseEvent):
    symbol: str = ""
    open: float = 0.0
    high: float = 0.0
    low: float = 0.0
    close: float = 0.0
    volume: float = 0.0
    index: pd.Timestamp = None  # bar time index

@dataclass
class FeaturesReady(BaseEvent):
    symbol: str = ""
    features_row: pd.Series = None  # last bar features (Series)
    features_df_tail: pd.DataFrame = None  # optional rolling tail for models
    in_sample: bool = False  # train window or test window
