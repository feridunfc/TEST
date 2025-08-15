from __future__ import annotations
import numpy as np
import pandas as pd

def _max_drawdown(cum: pd.Series) -> float:
    roll_max = cum.cummax()
    dd = cum / roll_max - 1.0
    return float(dd.min()) if len(dd) else 0.0

def simple_backtest(df: pd.DataFrame, signal: pd.Series, commission: float = 0.0005, slippage_bps: float = 2.0):
    # Defensive copies
    close = df["close"].astype(float)
    # one-bar delay on execution
    pos = signal.shift(1).fillna(0.0).astype(float)

    ret = close.pct_change(fill_method=None).fillna(0.0)

    # Transaction costs: use turnover (position change magnitude)
    turnover = pos.diff().abs().fillna(0.0)
    cost_per_turn = commission + (slippage_bps / 10000.0)
    costs = turnover * cost_per_turn

    strat_ret = pos * ret - costs
    equity = (1.0 + strat_ret).cumprod()

    mu = float(strat_ret.mean()) * 252.0
    sigma = float(strat_ret.std(ddof=0)) * np.sqrt(252.0)
    sharpe = (mu / sigma) if sigma > 1e-12 else 0.0

    ann_vol = float(strat_ret.std(ddof=0)) * np.sqrt(252.0)
    total_ret = float(equity.iloc[-1] - 1.0) if len(equity) else 0.0
    ann_ret = (1.0 + total_ret) ** (252.0 / max(len(strat_ret), 1)) - 1.0 if len(strat_ret) else 0.0
    max_dd = _max_drawdown(equity)

    stats = {
        "total_return": total_ret,
        "ann_return": ann_ret,
        "ann_vol": ann_vol,
        "sharpe": sharpe,
        "max_drawdown": max_dd,
    }
    out = df.copy()
    out["signal"] = signal.reindex(df.index).fillna(0.0)
    out["equity"] = equity.reindex(df.index).ffill().fillna(1.0)
    return out, stats