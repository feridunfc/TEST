import pandas as pd

REQUIRED = ["open","high","low","close","volume"]

def normalize_ohlc_columns(df: pd.DataFrame) -> pd.DataFrame:
    cols = {c: c.lower() for c in df.columns}
    df2 = df.rename(columns=cols)
    if "adj close" in df2.columns and "close" not in df2.columns:
        df2["close"] = df2["adj close"]
    return df2

def ensure_timezone(df: pd.DataFrame, tz: str = "UTC") -> pd.DataFrame:
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("DataFrame index must be DatetimeIndex")
    if df.index.tz is None:
        df.index = df.index.tz_localize(tz)
    else:
        df.index = df.index.tz_convert(tz)
    return df

def validate_ohlc(df: pd.DataFrame) -> None:
    for col in REQUIRED:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    if not (df["high"] >= df["low"]).all():
        raise ValueError("OHLC validation failed: high < low found")
    if not ((df["close"] <= df["high"]) & (df["close"] >= df["low"])).all():
        raise ValueError("OHLC validation failed: close not within [low, high]")
    if (df["volume"] < 0).any():
        raise ValueError("OHLC validation failed: negative volume found")
    if not df.index.is_monotonic_increasing:
        raise ValueError("Index must be sorted ascending")
