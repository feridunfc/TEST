from __future__ import annotations
from core.event_bus import event_bus
from core.events import BarDataEvent, FeaturesReady
from engines.feature_engineer import make_features
import pandas as pd

class FeatureService:
    def __init__(self):
        self.cache = []
        event_bus.subscribe(BarDataEvent, self._on_bar)

    def _on_bar(self, evt: BarDataEvent):
        self.cache.append({
            "timestamp": evt.timestamp, "open": evt.open, "high": evt.high,
            "low": evt.low, "close": evt.close, "volume": evt.volume,
            "symbol": evt.symbol
        })
        df = pd.DataFrame(self.cache).set_index("timestamp")
        feat = make_features(df).iloc[-1]
        event_bus.publish(FeaturesReady(
            source="FeatureService", symbol=evt.symbol, timestamp=evt.timestamp,
            features=feat.to_dict()
        ))
