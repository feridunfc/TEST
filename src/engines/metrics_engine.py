import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict

TRADING_DAYS = 252

@dataclass
class Metrics:
    sharpe: float
    sortino: float
    max_drawdown: float
    calmar: float
    annual_return: float
    win_rate: float

class MetricsEngine:
    @staticmethod
    def _returns_from_equity(equity: pd.Series) -> pd.Series:
        r = equity.pct_change().dropna()
        return r.replace([np.inf, -np.inf], np.nan).dropna()

    @staticmethod
    def compute_all(equity: pd.Series) -> Dict[str, float]:
        if not isinstance(equity, pd.Series) or equity.empty:
            return {k: 0.0 for k in ["sharpe","sortino","max_drawdown","calmar","annual_return","win_rate"]}
        r = MetricsEngine._returns_from_equity(equity)
        if r.empty:
            return {k: 0.0 for k in ["sharpe","sortino","max_drawdown","calmar","annual_return","win_rate"]}
        mu = r.mean() * TRADING_DAYS
        sigma = r.std(ddof=1) * np.sqrt(TRADING_DAYS)
        downside = r[r < 0].std(ddof=1) * np.sqrt(TRADING_DAYS)
        sharpe = float(mu / sigma) if sigma and sigma > 0 else 0.0
        sortino = float(mu / downside) if downside and downside > 0 else 0.0
        cum = (1 + r).cumprod()
        dd = (cum / cum.cummax() - 1).min()
        max_dd = float(dd) if isinstance(dd, (float, np.floating)) else float(dd.values[0])
        annual_return = float(mu)
        calmar = float(annual_return / abs(max_dd)) if max_dd < 0 else 0.0
        win_rate = float((r > 0).mean())
        return {
            "sharpe": sharpe,
            "sortino": sortino,
            "max_drawdown": max_dd,
            "calmar": calmar,
            "annual_return": annual_return,
            "win_rate": win_rate,
        }
