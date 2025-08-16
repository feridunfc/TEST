from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Dict
from ..configs.main_config import FeatureConfig

class FeatureEngineerEngine:
    def __init__(self, cfg: FeatureConfig):
        self.cfg = cfg

    def compute_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        out = pd.DataFrame(index=df.index)
        out["close"] = df["close"]
        out["ret"] = df["close"].pct_change()
        out["sma_fast"] = df["close"].rolling(self.cfg.sma_fast).mean()
        out["sma_slow"] = df["close"].rolling(self.cfg.sma_slow).mean()
        delta = df["close"].diff()
        gain = (delta.where(delta>0, 0)).rolling(self.cfg.rsi_period).mean()
        loss = (-delta.where(delta<0, 0)).rolling(self.cfg.rsi_period).mean()
        rs = gain / (loss.replace(0, np.nan))
        out["rsi"] = 100 - (100 / (1 + rs))
        out["vol"] = df["ret"].rolling(self.cfg.vol_window).std() * np.sqrt(252)
        out = out.fillna(method="bfill").fillna(method="ffill")
        return out

    def compute_for_bar(self, features_df: pd.DataFrame) -> pd.Series:
        # features_df is expected to be the full features frame; we return the last row as "current bar" features
        return features_df.iloc[-1]
