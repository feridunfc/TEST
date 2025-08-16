from __future__ import annotations
import numpy as np, pandas as pd

def backtest_vectorized(prices: pd.DataFrame, signals: pd.Series, commission: float=0.0005, slippage_bps: float=1.0) -> pd.DataFrame:
    s = signals.reindex(prices.index).fillna(0.0)
    slipped_open = prices["open"] * (1 + (slippage_bps/1e4))
    rets = (prices["close"] / slipped_open - 1.0).fillna(0.0)
    strat_rets = s.shift(1).fillna(0.0) * rets
    trades = s.diff().abs().fillna(0.0)
    costs = trades * commission
    net = strat_rets - costs
    equity = (1+net).cumprod()
    return pd.DataFrame({"returns": net, "equity": equity})
