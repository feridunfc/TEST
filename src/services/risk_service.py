
import logging
from core.bus.event_bus import event_bus
from core.events.strategy_events import StrategySignalGenerated, SignalDirection
from core.events.risk_events import RiskAssessmentCompleted

log = logging.getLogger("RiskService")

class RiskService:
    """Pass-through risk with optional gross cap. Extend later with vol targeting / max DD constraints."""
    def __init__(self, gross_cap: float = 1.0) -> None:
        self.gross_cap = float(gross_cap)
        event_bus.subscribe(StrategySignalGenerated, self.on_signal)

    def on_signal(self, ev: StrategySignalGenerated) -> None:
        # Convert discrete signal to target position within [-gross_cap, +gross_cap]
        mapping = {
            SignalDirection.SHORT: -self.gross_cap,
            SignalDirection.LONG: +self.gross_cap,
            SignalDirection.FLAT: 0.0,
        }
        pos = float(mapping.get(ev.signal, 0.0))
        rationale = f"pass_through; gross_cap={self.gross_cap}"
        event_bus.publish(RiskAssessmentCompleted(
            source="RiskService",
            symbol=ev.symbol,
            dt=ev.dt,
            desired_position=pos,
            rationale=rationale
        ))
