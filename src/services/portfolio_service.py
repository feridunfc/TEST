from __future__ import annotations
import json
from ..core.bus.event_bus import event_bus
from ..core.events.order_portfolio_events import OrderFilled, PortfolioUpdated
from ..core.events.data_events import BarDataEvent
from ..engines.portfolio_manager_engine import PortfolioManagerEngine

class PortfolioService:
    def __init__(self, initial_cash: float = 100000.0):
        self.bus = event_bus
        self.engine = PortfolioManagerEngine(initial_cash=initial_cash)
        self.prices = {}
        self.bus.subscribe(OrderFilled, self.on_filled)
        self.bus.subscribe(BarDataEvent, self.on_bar)

    def on_filled(self, event: OrderFilled):
        self.engine.on_fill(event.symbol, event.quantity, event.price, ts="now")

    def on_bar(self, event: BarDataEvent):
        self.prices[event.symbol] = event.close
        self.engine.mark_to_market({event.symbol: event.close}, ts=event.index_ts)
        eq = self.engine.state.total_value
        self.bus.publish(PortfolioUpdated(
            source="PortfolioService",
            symbol=event.symbol,
            total_value=eq,
            cash=self.engine.state.cash,
            positions_json=json.dumps(self.engine.state.positions)
        ))
