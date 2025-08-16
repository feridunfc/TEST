from __future__ import annotations
import numpy as np, pandas as pd

def max_drawdown(equity: pd.Series) -> float:
    roll_max = equity.cummax()
    dd = equity/roll_max - 1.0
    return float(dd.min())

def sharpe(returns: pd.Series, rf_daily: float=0.0) -> float:
    r = returns.dropna() - rf_daily
    sd = r.std()
    if sd == 0 or np.isnan(sd):
        return 0.0
    return float((r.mean()/sd) * (252**0.5))

def sortino(returns: pd.Series, rf_daily: float=0.0) -> float:
    r = returns.dropna() - rf_daily
    downside = r[r<0].std()
    if downside == 0 or np.isnan(downside):
        return 0.0
    return float((r.mean()/downside) * (252**0.5))

def annual_return(returns: pd.Series) -> float:
    r = returns.fillna(0.0)
    cum = (1+r).prod()
    years = len(r)/252
    if years <= 0:
        return 0.0
    return float(cum**(1/years) - 1.0)

def summarize(df_bt: pd.DataFrame) -> dict:
    eq = df_bt["equity"]
    rets = df_bt["returns"]
    return {
        "sharpe": sharpe(rets),
        "sortino": sortino(rets),
        "max_dd": max_drawdown(eq),
        "annual_return": annual_return(rets),
        "last_equity": float(eq.iloc[-1])
    }
