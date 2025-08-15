from __future__ import annotations
from dataclasses import dataclass
import pandas as pd

@dataclass(frozen=True)
class FeaturesReady:
    symbol: str
    features_df: pd.DataFrame
