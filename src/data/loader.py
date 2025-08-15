from __future__ import annotations
import pandas as pd
from typing import Optional

def _normalize_yf(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df = df.xs(df.columns.levels[0][0], axis=1, level=0, drop_level=True)
    df = df.rename(columns={c: c.lower() for c in df.columns})
    if "adj close" in df.columns:
        df["close"] = df["adj close"]
    required = ["open", "high", "low", "close"]
    for r in required:
        if r not in df.columns:
            raise ValueError(f"yfinance returned unexpected columns: {set(df.columns)}")
    df = df.sort_index().dropna()
    return df[["open", "high", "low", "close"] + (["volume"] if "volume" in df.columns else [])]

def load_data_yf(symbol: str, start: Optional[str], end: Optional[str], interval: str) -> pd.DataFrame:
    import yfinance as yf
    df = yf.download(symbol, start=start, end=end, interval=interval, progress=False)
    if df is None or len(df) == 0:
        raise ValueError("yfinance returned empty dataframe")
    return _normalize_yf(df)

def load_data_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=True, index_col=0)
    df.columns = [c.lower() for c in df.columns]
    return df
