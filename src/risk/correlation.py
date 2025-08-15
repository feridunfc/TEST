
from __future__ import annotations
import pandas as pd

def rolling_corr(frame: pd.DataFrame, window: int = 60) -> pd.DataFrame:
    """frame: columns = symbols, rows = aligned returns"""
    return frame.rolling(window).corr().dropna()
