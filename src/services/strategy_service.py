
import logging
from core.bus.event_bus import event_bus
from core.events.strategy_events import FeaturesReady, StrategySignalGenerated, SignalDirection

log = logging.getLogger("StrategyService")

class StrategyService:
    """Simple MA-crossover strategy that emits a per-bar signal.

    - LONG if sma_fast > sma_slow, SHORT if sma_fast < sma_slow, FLAT otherwise.
    """
    def __init__(self, name: str = "ma_crossover") -> None:
        self.name = name
        event_bus.subscribe(FeaturesReady, self.on_features)

    def on_features(self, ev: FeaturesReady) -> None:
        f = ev.features or {}
        sf, ss = f.get('sma_fast'), f.get('sma_slow')
        if sf is None or ss is None:
            return
        if sf > ss:
            sig = SignalDirection.LONG
        elif sf < ss:
            sig = SignalDirection.SHORT
        else:
            sig = SignalDirection.FLAT
        event_bus.publish(StrategySignalGenerated(
            source="StrategyService",
            symbol=ev.symbol,
            dt=ev.dt,
            signal=sig,
            meta={'strategy': self.name}
        ))
