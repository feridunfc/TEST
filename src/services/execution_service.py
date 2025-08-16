from __future__ import annotations
from ..core.bus.event_bus import event_bus
from ..core.events.risk_events import RiskAssessmentCompleted
from ..core.events.order_portfolio_events import OrderFilled
from ..engines.execution_engine import ExecutionEngine

class ExecutionService:
    def __init__(self, fee_bps: float = 2.0, slippage_bps: float = 5.0):
        self.bus = event_bus
        self.engine = ExecutionEngine(fee_bps=fee_bps, slippage_bps=slippage_bps)
        self.portfolio_value = 100000.0  # will be updated from portfolio service
        self.bus.subscribe(RiskAssessmentCompleted, self.on_decision)

    def on_decision(self, event: RiskAssessmentCompleted):
        if abs(event.position_size_pct) <= 0.0:
            return
        res = self.engine.execute_weight(self.portfolio_value, event.price, event.position_size_pct)
        self.bus.publish(OrderFilled(
            source="ExecutionService",
            symbol=event.symbol,
            strategy_name=event.strategy_name,
            direction=event.direction,
            quantity=res.quantity,
            price=res.price,
            weight=res.weight
        ))

    def update_portfolio_value(self, val: float):
        self.portfolio_value = val
