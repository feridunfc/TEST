import numpy as np
import pandas as pd

def max_drawdown(equity: pd.Series) -> float:
    roll_max = equity.cummax()
    dd = equity / roll_max - 1.0
    return float(dd.min())

def sharpe(returns: pd.Series, periods_per_year: int = 252, rf: float = 0.0) -> float:
    # returns should be simple returns
    mu = returns.mean()
    sd = returns.std(ddof=0)
    if sd == 0 or np.isnan(sd):
        return 0.0
    return float((mu - rf/periods_per_year) / sd * np.sqrt(periods_per_year))

def sortino(returns: pd.Series, periods_per_year: int = 252, rf: float = 0.0) -> float:
    downside = returns[returns < 0]
    dd = downside.std(ddof=0)
    if dd == 0 or np.isnan(dd):
        return 0.0
    mu = returns.mean()
    return float((mu - rf/periods_per_year) / dd * np.sqrt(periods_per_year))

def calmar(returns: pd.Series, equity: pd.Series, periods_per_year: int = 252) -> float:
    ann_ret = annualized_return(returns, periods_per_year)
    mdd = abs(max_drawdown(equity))
    if mdd == 0:
        return 0.0
    return float(ann_ret / mdd)

def annualized_return(returns: pd.Series, periods_per_year: int = 252) -> float:
    # geometric annualization
    cum = (1.0 + returns).prod()
    n = len(returns)
    if n == 0:
        return 0.0
    return float(cum ** (periods_per_year / n) - 1.0)

def win_rate(returns: pd.Series) -> float:
    if len(returns) == 0:
        return 0.0
    wins = (returns > 0).sum()
    return float(wins / len(returns))

def summarize(returns: pd.Series) -> dict:
    equity = (1.0 + returns).cumprod()
    return {
        "total_return": float(equity.iloc[-1] - 1.0) if len(equity) else 0.0,
        "annual_return": annualized_return(returns),
        "sharpe": sharpe(returns),
        "sortino": sortino(returns),
        "calmar": calmar(returns, equity),
        "max_drawdown": max_drawdown(equity),
        "vol": float(returns.std(ddof=0) * np.sqrt(252)),
        "win_rate": win_rate(returns),
    }
