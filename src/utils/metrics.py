
# utils/metrics.py
import numpy as np
import pandas as pd

def max_drawdown(equity: pd.Series) -> float:
    if equity.empty:
        return 0.0
    roll_max = equity.cummax()
    dd = (equity / roll_max) - 1.0
    return dd.min()

def annualized_return(equity: pd.Series, periods_per_year: int = 252) -> float:
    if equity.empty:
        return 0.0
    total_return = equity.iloc[-1] / equity.iloc[0] - 1.0
    years = len(equity) / periods_per_year
    if years <= 0:
        return 0.0
    return (1 + total_return) ** (1 / years) - 1

def sharpe_ratio(returns: pd.Series, periods_per_year: int = 252) -> float:
    if returns.empty:
        return 0.0
    mu = returns.mean() * periods_per_year
    sigma = returns.std(ddof=0) * np.sqrt(periods_per_year)
    return mu / sigma if sigma > 0 else 0.0

def sortino_ratio(returns: pd.Series, periods_per_year: int = 252) -> float:
    if returns.empty:
        return 0.0
    downside = returns[returns < 0]
    denom = downside.std(ddof=0) * np.sqrt(periods_per_year)
    mu = returns.mean() * periods_per_year
    return mu / denom if denom > 0 else 0.0

def metrics_from_equity(equity: pd.Series, periods_per_year: int = 252):
    if equity.empty:
        return {"CAGR": 0.0, "Sharpe": 0.0, "Sortino": 0.0, "MaxDD": 0.0}
    rets = equity.pct_change().dropna()
    return {
        "CAGR": annualized_return(equity, periods_per_year),
        "Sharpe": sharpe_ratio(rets, periods_per_year),
        "Sortino": sortino_ratio(rets, periods_per_year),
        "MaxDD": float(max_drawdown(equity)),
    }
