
from dataclasses import dataclass
from typing import Any, Dict

try:
    from core.bus.event_bus import event_bus as default_bus
    from core.events.order_events import OrderFilled
    from core.events.portfolio_events import PortfolioUpdated
except Exception:
    class SimpleBus:
        def __init__(self):
            self.subs = {}
        def subscribe(self, etype, cb):
            self.subs.setdefault(etype, []).append(cb)
        def publish(self, e):
            for cb in self.subs.get(type(e), []):
                cb(e)
    default_bus = SimpleBus()
    @dataclass
    class OrderFilled:
        source: str
        symbol: str
        side: str
        quantity: float
        avg_price: float
        timestamp: Any
    @dataclass
    class PortfolioUpdated:
        source: str
        timestamp: Any
        cash: float
        total_value: float
        positions: Dict[str, float]

class PortfolioService:
    def __init__(self, start_cash: float = 100000.0, bus=None):
        self.bus = bus or default_bus
        self.cash = start_cash
        self.positions: Dict[str, float] = {}
        self.prices: Dict[str, float] = {}
        self.bus.subscribe(OrderFilled, self.on_fill)

    def mark_price(self, symbol: str, price: float):
        self.prices[symbol] = price

    def _calc_total_value(self) -> float:
        pv = self.cash
        for sym, qty in self.positions.items():
            px = self.prices.get(sym, 0.0)
            pv += qty * px
        return pv

    def on_fill(self, event: 'OrderFilled'):
        qty = event.quantity if event.side.upper() == "BUY" else -event.quantity
        self.positions[event.symbol] = self.positions.get(event.symbol, 0.0) + qty
        self.cash -= qty * event.avg_price
        self.mark_price(event.symbol, event.avg_price)
        total = self._calc_total_value()
        self.bus.publish(PortfolioUpdated(
            source="PortfolioService",
            timestamp=event.timestamp,
            cash=self.cash,
            total_value=total,
            positions=self.positions.copy()
        ))
