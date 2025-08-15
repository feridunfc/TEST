from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Dict, Any
from utils.metrics import summarize

def simple_backtest(df: pd.DataFrame, signal: pd.Series,
                    commission: float = 0.0005,
                    slippage_bps: float = 1.0,
                    delay: int = 1,
                    vol_target: float = 0.0,
                    max_drawdown: float = 1.0) -> Dict[str, Any]:
    """
    - df: must contain 'close'
    - signal: in [-1, 0, 1], index aligned to df
    - delay: bars between signal and execution to avoid look-ahead
    - slippage_bps: applied when position changes
    - commission: applied on turnover
    - vol_target: if >0, scale position to target vol using rolling std(20)
    - max_drawdown: portfolio-level stop (fraction), if equity DD breaches, flat
    """
    assert 'close' in df.columns, "df must have 'close'"
    c = df['close']
    ret = c.pct_change().fillna(0.0)  # simple returns

    sig = signal.shift(delay).fillna(0.0).clip(-1, 1)

    if vol_target and vol_target > 0:
        # scale by recent vol (20-day) so that position * vol ~= vol_target / sqrt(252)
        ann2d = vol_target / np.sqrt(252.0)
        realized = ret.rolling(20).std(ddof=0).replace(0.0, np.nan).ffill().fillna(ret.std(ddof=0))
        scaler = (ann2d / (realized + 1e-12)).clip(0, 3.0)
        pos = (sig * scaler).clip(-1.0, 1.0)
    else:
        pos = sig

    # Transaction costs on changes of position
    pos_prev = pos.shift(1).fillna(0.0)
    turnover = (pos - pos_prev).abs()
    cost = turnover * (commission + slippage_bps * 1e-4)

    strat_ret = pos_prev * ret - cost  # use yesterday's position for today's return
    equity = (1.0 + strat_ret).cumprod()

    # Apply max drawdown hard stop
    if max_drawdown < 1.0:
        peak = equity.cummax()
        dd = equity / peak - 1.0
        # flat from first breach onward
        breach = dd < -abs(max_drawdown)
        if breach.any():
            first = breach.idxmax() if breach.sum() else None
            if first is not None and breach.loc[first]:
                after = strat_ret.copy()
                after.loc[after.index >= first] = 0.0
                strat_ret = after
                equity = (1.0 + strat_ret).cumprod()

    stats = summarize(strat_ret)
    out = {
        "returns": strat_ret,
        "equity": equity,
        "stats": stats
    }
    return out
