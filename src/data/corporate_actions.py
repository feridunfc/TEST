import pandas as pd

def apply_split(df: pd.DataFrame, split_date: pd.Timestamp, ratio: float) -> pd.DataFrame:
    df = df.copy()
    mask = df.index < split_date
    cols = ["open","high","low","close"]
    df.loc[mask, cols] = df.loc[mask, cols] / ratio
    if "volume" in df.columns:
        df.loc[mask, "volume"] = df.loc[mask, "volume"] * ratio
    return df

def apply_dividend(df: pd.DataFrame, ex_date: pd.Timestamp, amount: float) -> pd.DataFrame:
    df = df.copy()
    if ex_date in df.index:
        df.loc[ex_date, "open"] = max(0.0, df.loc[ex_date, "open"] - amount)
    return df
