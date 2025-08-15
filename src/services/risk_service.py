import logging
from core.bus.event_bus import EventBus
from core.events.strategy_events import StrategySignalGenerated, SignalDirection

logger = logging.getLogger("RiskService")

class RiskService:
    def __init__(self, max_leverage: float = 1.0):
        self.max_leverage = float(max_leverage)
        EventBus.subscribe(StrategySignalGenerated, self.on_signal)

    def on_signal(self, event: StrategySignalGenerated):
        # placeholder: just log / simple checks
        if abs(event.strength) > 1.0:
            logger.warning("Capping strength to 1.0")
        # would publish OrderEvent here in a full ED stack
        logger.info(f"Risk accepted signal {event.direction.name} for {event.symbol}")
