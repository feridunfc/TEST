from __future__ import annotations
import json
from ..core.bus.event_bus import event_bus
from ..core.events.backtest_events import BacktestRequested, BacktestCompleted
from ..core.events.data_events import BarDataEvent, DataSnapshotReady
from ..engines.data_provider_engine import DataProviderEngine

class BacktestingService:
    def __init__(self):
        self.bus = event_bus
        self.bus.subscribe(BacktestRequested, self.run_replay)
        self.data = DataProviderEngine()

    def run_replay(self, event: BacktestRequested):
        df = self.data.fetch(event.symbol, event.start, event.end, event.interval)

        # full snapshot for training services
        self.bus.publish(DataSnapshotReady(
            source="BacktestingService",
            symbol=event.symbol,
            df_json=df.to_json(orient="split")
        ))

        for ts, row in df.iterrows():
            self.bus.publish(BarDataEvent(
                source="BacktestingService",
                symbol=event.symbol,
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
                volume=float(row["volume"]),
                index_ts=str(ts)
            ))
        self.bus.publish(BacktestCompleted(
            source="BacktestingService",
            symbol=event.symbol,
            strategy_names=event.strategy_names,
            mode=event.mode,
            results={}
        ))
