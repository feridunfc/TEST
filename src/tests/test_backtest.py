import numpy as np
import pandas as pd
import pytest

class LookAheadError(Exception):
    pass

def generate_test_data(n=1000, seed=0):
    rng = np.random.default_rng(seed)
    r = rng.normal(0, 0.01, n)
    close = 100 * (1 + pd.Series(r)).cumprod()
    idx = pd.date_range("2020-01-01", periods=n, freq="B")
    df = pd.DataFrame({"close": close}, index=idx)
    df["open"] = df["close"].shift(1).fillna(df["close"])
    df["high"] = df[["open","close"]].max(axis=1) * (1 + abs(rng.normal(0, 0.002, n)))
    df["low"] = df[["open","close"]].min(axis=1) * (1 - abs(rng.normal(0, 0.002, n)))
    df["volume"] = rng.integers(1000, 5000, n)
    return df

def detect_lookahead(df: pd.DataFrame):
    for c in df.columns:
        if "future" in c.lower():
            raise LookAheadError(f"Potential look-ahead via column: {c}")

def backtest(strategy, df: pd.DataFrame):
    detect_lookahead(df)
    if hasattr(strategy, "train"):
        strategy.train(df.iloc[:-100])
    sig = strategy.predict(df)
    ret = df["close"].pct_change().fillna(0.0)
    pnl = (sig.shift(1).fillna(0.0) * ret).cumsum()
    return pnl

def test_lookahead_bias():
    df = generate_test_data(500)
    df["future_leak"] = df["close"].shift(-1).ffill()
    class Dummy:
        def train(self, _): pass
        def predict(self, d): return pd.Series(0, index=d.index)
    with pytest.raises(LookAheadError):
        backtest(Dummy(), df)
