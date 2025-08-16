from __future__ import annotations
from core.event_bus import event_bus
from core.events import FeaturesReady, StrategySignalGenerated, SignalDirection
from engines.signal_generator import vectorized_ma_signals
import pandas as pd

class StrategyService:
    def __init__(self):
        self.df_feat = pd.DataFrame()
        event_bus.subscribe(FeaturesReady, self._on_feat)

    def _on_feat(self, evt: FeaturesReady):
        row = evt.features.copy()
        row["symbol"] = evt.symbol
        self.df_feat.loc[evt.timestamp, list(row.keys())] = list(row.values())
        try:
            direction = int(vectorized_ma_signals(self.df_feat).iloc[-1])
        except Exception:
            direction = 0
        event_bus.publish(StrategySignalGenerated(
            source="StrategyService", symbol=evt.symbol, timestamp=evt.timestamp,
            direction=SignalDirection(direction), strength=1.0
        ))
