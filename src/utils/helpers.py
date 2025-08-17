
from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Tuple

def safe_division(a: float, b: float, default: float = 0.0) -> float:
    try:
        if b == 0 or b is None:
            return default
        return float(a) / float(b)
    except Exception:
        return default

def format_currency(x: float, symbol: str = "$") -> str:
    try:
        return f"{symbol}{x:,.2f}"
    except Exception:
        return f"{symbol}{x}"

class TechnicalAnalysis:
    """Tiny TA helper for RSI and MACD used by the risk engine."""
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def rsi(self, period: int = 14) -> pd.Series:
        close = self._get_series("close")
        delta = close.diff()
        up = delta.clip(lower=0)
        down = -delta.clip(upper=0)
        roll_up = up.ewm(alpha=1/period, adjust=False).mean()
        roll_down = down.ewm(alpha=1/period, adjust=False).mean()
        rs = roll_up / (roll_down.replace(0, np.nan))
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50.0)

    def macd(self, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series]:
        close = self._get_series("close")
        ema_fast = close.ewm(span=fast, adjust=False).mean()
        ema_slow = close.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        return macd_line.fillna(0.0), signal_line.fillna(0.0)

    def _get_series(self, name: str) -> pd.Series:
        if isinstance(self.df, pd.Series):
            return self.df
        if name in self.df.columns:
            return self.df[name]
        # attempt to infer case-insensitive
        for c in self.df.columns:
            if c.lower() == name.lower():
                return self.df[c]
        raise KeyError(f"Column '{name}' not found in technicals/features DataFrame")
