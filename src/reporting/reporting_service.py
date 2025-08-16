from __future__ import annotations
from core.event_bus import event_bus
from core.events import PortfolioUpdated, BacktestCompleted
from engines.metrics_engine import summarize
import pandas as pd

class ReportingService:
    def __init__(self):
        self.rows = []
        event_bus.subscribe(PortfolioUpdated, self._on_update)
        event_bus.subscribe(BacktestCompleted, self._on_done)

    def _on_update(self, evt: PortfolioUpdated):
        self.rows.append({"ts": evt.timestamp, "equity": evt.equity})

    def _on_done(self, evt: BacktestCompleted):
        if not self.rows:
            print("No portfolio history collected.")
            return
        df = pd.DataFrame(self.rows).set_index("ts").sort_index()
        rets = df["equity"].pct_change().fillna(0.0)
        summary = summarize(pd.DataFrame({"returns": rets, "equity": (1+rets).cumprod()}))
        print("\n=== BACKTEST SUMMARY ===")
        for k,v in summary.items():
            print(f"{k:16s}: {v}")
        self.rows = []
