
from __future__ import annotations
from typing import List, Dict, Any
import pandas as pd
from backtest.simulator import run_backtest

def rolling_windows(df: pd.DataFrame, n_splits: int = 3) -> List[pd.DataFrame]:
    n = len(df)
    if n_splits < 1 or n < 10:
        return [df]
    size = n // n_splits
    chunks = [df.iloc[i*size:(i+1)*size].copy() for i in range(n_splits-1)]
    chunks.append(df.iloc[(n_splits-1)*size:].copy())
    return chunks

def walk_forward_backtest(df: pd.DataFrame, n_splits: int = 3) -> List[Dict[str, Any]]:
    results = []
    for i, chunk in enumerate(rolling_windows(df, n_splits)):
        res = run_backtest(chunk)
        res["fold"] = i+1
        results.append(res)
    return results
