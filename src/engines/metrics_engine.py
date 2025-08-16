
import numpy as np
import pandas as pd

class MetricsEngine:
    @staticmethod
    def _annualize(mean_daily, std_daily):
        return (mean_daily * 252.0), (std_daily * np.sqrt(252.0))

    @staticmethod
    def sharpe(returns: pd.Series, rf_daily: float = 0.0) -> float:
        r = returns.dropna() - rf_daily
        if r.std() == 0 or len(r) < 2:
            return 0.0
        return np.sqrt(252.0) * r.mean() / r.std()

    @staticmethod
    def sortino(returns: pd.Series, rf_daily: float = 0.0) -> float:
        r = returns.dropna() - rf_daily
        downside = r[r < 0]
        if downside.std() == 0 or len(r) < 2:
            return 0.0
        return np.sqrt(252.0) * r.mean() / downside.std()

    @staticmethod
    def max_drawdown(equity: pd.Series) -> float:
        if equity.isna().all():
            return 0.0
        peak = equity.cummax()
        dd = equity / peak - 1.0
        return dd.min()

    @staticmethod
    def annual_return(equity: pd.Series) -> float:
        if len(equity.dropna()) < 2:
            return 0.0
        total_return = equity.dropna().iloc[-1] / equity.dropna().iloc[0] - 1.0
        years = len(equity.dropna()) / 252.0
        if years <= 0:
            return 0.0
        return (1 + total_return) ** (1 / years) - 1

    @staticmethod
    def win_rate(returns: pd.Series) -> float:
        r = returns.dropna()
        if len(r) == 0:
            return 0.0
        return (r > 0).mean()

    @classmethod
    def compute_all(cls, equity: pd.Series) -> dict:
        rets = equity.pct_change().fillna(0.0)
        maxdd = cls.max_drawdown(equity)
        annret = cls.annual_return(equity)
        return {
            "sharpe": float(cls.sharpe(rets)),
            "sortino": float(cls.sortino(rets)),
            "max_drawdown": float(maxdd),
            "calmar": float((annret / abs(maxdd)) if maxdd != 0 else 0.0),
            "annual_return": float(annret),
            "win_rate": float(cls.win_rate(rets)),
        }
