from __future__ import annotations
from core.event_bus import event_bus
from core.events import RiskAssessmentCompleted, OrderFilled

class ExecutionService:
    def __init__(self):
        event_bus.subscribe(RiskAssessmentCompleted, self._on_risk)

    def _on_risk(self, evt: RiskAssessmentCompleted):
        event_bus.publish(OrderFilled(
            source="ExecutionService", symbol=evt.symbol, timestamp=evt.timestamp,
            direction=evt.direction, quantity=evt.quantity, fill_price=evt.entry_price
        ))
