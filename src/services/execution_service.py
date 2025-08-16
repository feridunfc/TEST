
from dataclasses import dataclass
from typing import Any
import asyncio

try:
    from core.bus.event_bus import event_bus as default_bus
    from core.events.risk_events import RiskAssessmentCompleted
    from core.events.order_events import OrderFilled
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
    class RiskAssessmentCompleted:
        source: str
        symbol: str
        side: str
        quantity: float
        price: float
        timestamp: Any
    @dataclass
    class OrderFilled:
        source: str
        symbol: str
        side: str
        quantity: float
        avg_price: float
        timestamp: Any

from ..execution.engine import AsyncExecutionEngine, Order

class ExecutionService:
    def __init__(self, bus=None):
        self.bus = bus or default_bus
        self.engine = AsyncExecutionEngine()
        self.bus.subscribe(RiskAssessmentCompleted, self.on_decision)

    def on_decision(self, event: 'RiskAssessmentCompleted'):
        async def _run():
            report = await self.engine.execute(Order(event.symbol, event.side, event.quantity, event.price))
            self.bus.publish(OrderFilled(
                source="ExecutionService",
                symbol=report.symbol,
                side=report.side,
                quantity=report.qty,
                avg_price=report.avg_price,
                timestamp=event.timestamp
            ))
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(_run())
        except RuntimeError:
            asyncio.run(_run())
