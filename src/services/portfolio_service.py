from __future__ import annotations
from core.event_bus import event_bus
from core.events import OrderFilled, PortfolioUpdated, BarDataEvent
from collections import defaultdict

class PortfolioService:
    def __init__(self, starting_cash: float=100000.0):
        self.cash = float(starting_cash)
        self.positions = defaultdict(float)
        self.last_prices = {}
        event_bus.subscribe(OrderFilled, self._on_filled)
        event_bus.subscribe(BarDataEvent, self._on_bar)

    def _on_filled(self, evt: OrderFilled):
        sign = 1 if evt.direction.value > 0 else -1
        self.cash -= sign * evt.quantity * evt.fill_price
        self.positions[evt.symbol] += sign * evt.quantity

    def _on_bar(self, evt: BarDataEvent):
        self.last_prices[evt.symbol] = evt.close
        equity = self.cash + sum(qty * self.last_prices.get(sym, 0.0) for sym, qty in self.positions.items())
        event_bus.publish(PortfolioUpdated(
            source="PortfolioService", timestamp=evt.timestamp,
            equity=float(equity), cash=float(self.cash), positions=dict(self.positions)
        ))
