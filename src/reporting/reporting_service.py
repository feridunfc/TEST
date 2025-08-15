
import logging
import numpy as np
import pandas as pd

from core.bus.event_bus import event_bus
from core.events.portfolio_events import PortfolioUpdated
from core.events.backtest_events import BacktestCompleted

log = logging.getLogger("ReportingService")

def _max_drawdown(equity: pd.Series) -> float:
    peak = equity.cummax()
    dd = equity/peak - 1.0
    return float(dd.min())

def _annualized_return(equity: pd.Series, periods_per_year: int = 252) -> float:
    if equity.empty:
        return 0.0
    total_return = equity.iloc[-1] / equity.iloc[0] - 1.0
    years = max(len(equity) / periods_per_year, 1e-9)
    return float((1.0 + total_return) ** (1.0/years) - 1.0)

def _sharpe(returns: pd.Series, periods_per_year: int = 252) -> float:
    if returns.std(ddof=0) == 0:
        return 0.0
    return float(np.sqrt(periods_per_year) * returns.mean() / (returns.std(ddof=0) + 1e-12))

def _sortino(returns: pd.Series, periods_per_year: int = 252) -> float:
    downside = returns[returns < 0]
    denom = downside.std(ddof=0)
    if denom == 0 or np.isnan(denom):
        return 0.0
    return float(np.sqrt(periods_per_year) * returns.mean() / denom)

class ReportingService:
    def __init__(self) -> None:
        self._records = []  # (dt, equity)
        event_bus.subscribe(PortfolioUpdated, self.on_portfolio)
        event_bus.subscribe(BacktestCompleted, self.on_completed)

    def on_portfolio(self, ev: PortfolioUpdated) -> None:
        self._records.append((ev.dt, ev.equity))

    def on_completed(self, ev: BacktestCompleted) -> None:
        if not self._records:
            log.warning("[ReportingService] No portfolio records to report.")
            return
        df = pd.DataFrame(self._records, columns=['dt','equity']).set_index('dt')
        rets = df['equity'].pct_change().fillna(0.0)
        metrics = {
            'CAGR': _annualized_return(df['equity']),
            'Sharpe': _sharpe(rets),
            'Sortino': _sortino(rets),
            'MaxDrawdown': _max_drawdown(df['equity']),
        }
        log.info(f"[ReportingService] Results: {metrics}")
        # Save to CSV for inspection
        df.to_csv('equity_curve.csv')
        pd.Series(metrics).to_csv('metrics.csv')
        print("\n=== BACKTEST METRICS ===\n", pd.Series(metrics))
        print("\nEquity curve saved to equity_curve.csv, metrics to metrics.csv\n")
