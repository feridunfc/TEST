from __future__ import annotations
from core.event_bus import event_bus
from core.events import StrategySignalGenerated, RiskAssessmentCompleted, SignalDirection, BarDataEvent
from risk.position_sizing import AdvancedPositionSizer
import pandas as pd

class RiskService:
    def __init__(self, starting_cash: float=100000.0):
        self.cash = float(starting_cash)
        self.price_series = pd.Series(dtype=float)
        self.sizer = AdvancedPositionSizer()
        event_bus.subscribe(StrategySignalGenerated, self._on_sig)
        event_bus.subscribe(BarDataEvent, self._on_bar)

    def _on_bar(self, evt: BarDataEvent):
        self.price_series.loc[evt.timestamp] = evt.close

    def _on_sig(self, evt: StrategySignalGenerated):
        if len(self.price_series) == 0:
            return
        px = float(self.price_series.iloc[-1])
        qty_usd = self.sizer.calculate(self.price_series, self.cash + 0.0)
        qty = qty_usd / max(px, 1e-9)
        if evt.direction == SignalDirection.HOLD or qty <= 0:
            return
        event_bus.publish(RiskAssessmentCompleted(
            source="RiskService", symbol=evt.symbol, timestamp=evt.timestamp,
            direction=evt.direction, quantity=qty, entry_price=px
        ))
