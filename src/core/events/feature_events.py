
# core/events/feature_events.py
from dataclasses import dataclass
import pandas as pd
from .base import BaseEvent

@dataclass
class FeaturesReady(BaseEvent):
    symbol: str = "SPY"
    features_df: pd.DataFrame = pd.DataFrame()  # usually a single-row DataFrame (last bar features)
