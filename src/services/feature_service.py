
from collections import deque
from typing import Deque, Optional
import logging

from core.bus.event_bus import event_bus
from core.events.data_events import BarDataEvent, CleanedDataReady
from core.events.strategy_events import FeaturesReady

log = logging.getLogger("FeatureService")

class FeatureService:
    """Stream-based rolling features.

    - Subscribes to BarDataEvent for live/replay flow.
    - Also supports bootstrapping from CleanedDataReady by publishing a sequence of BarDataEvent.

    """
    def __init__(self, sma_fast: int = 20, sma_slow: int = 50) -> None:
        self.fast = sma_fast
        self.slow = sma_slow
        self.buf_fast: Deque[float] = deque(maxlen=self.fast)
        self.buf_slow: Deque[float] = deque(maxlen=self.slow)
        self.prev_close: Optional[float] = None
        event_bus.subscribe(BarDataEvent, self.on_bar)
        event_bus.subscribe(CleanedDataReady, self.on_bootstrap)
        log.info(f"[FeatureService] Initialized with fast={self.fast} slow={self.slow}")

    def on_bootstrap(self, ev: CleanedDataReady) -> None:
        # Emit BarDataEvent for each row to drive stream
        for dt, row in ev.df.iterrows():
            event_bus.publish(BarDataEvent(
                source="FeatureService.bootstrap",
                symbol=ev.symbol,
                dt=dt,
                open=row['open'], high=row['high'], low=row['low'], close=row['close'], volume=row['volume']
            ))

    def on_bar(self, ev: BarDataEvent) -> None:
        close = float(ev.close)
        self.buf_fast.append(close)
        self.buf_slow.append(close)
        ret = 0.0
        if self.prev_close is not None and self.prev_close != 0.0:
            ret = (close / self.prev_close) - 1.0
        self.prev_close = close

        features = {}
        if len(self.buf_fast) == self.fast:
            features['sma_fast'] = sum(self.buf_fast) / self.fast
        if len(self.buf_slow) == self.slow:
            features['sma_slow'] = sum(self.buf_slow) / self.slow
        features['ret'] = ret
        # Only publish once both SMAs are available
        if 'sma_fast' in features and 'sma_slow' in features:
            event_bus.publish(FeaturesReady(
                source="FeatureService",
                symbol=ev.symbol,
                dt=ev.dt,
                features=features
            ))
