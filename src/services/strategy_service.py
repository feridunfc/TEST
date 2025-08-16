from __future__ import annotations
import json
import pandas as pd
from ..core.bus.event_bus import event_bus
from ..core.events.strategy_events import FeaturesReady, StrategySignalGenerated, SignalDirection
from ..engines.signal_generator_engine import SignalGeneratorEngine

class StrategyService:
    def __init__(self, strategy_params: dict):
        self.bus = event_bus
        self.engine = SignalGeneratorEngine(strategy_params)
        self.bus.subscribe(FeaturesReady, self.on_features)

        # keep small rolling features frame to help AI predict
        self._feat_roll = []

    def on_features(self, event: FeaturesReady):
        row = pd.read_json(event.features_json, typ='series')
        self._feat_roll.append(row)
        if len(self._feat_roll) > 400:
            self._feat_roll = self._feat_roll[-400:]
        features_df = pd.DataFrame(self._feat_roll)

        for name in self.engine.strategies.keys():
            # Ensure trained if needed
            try:
                self.engine.ensure_trained(name, features_df)
            except Exception:
                pass
            sig = self.engine.signal_for_bar(name, features_df)
            direction = SignalDirection(sig)
            self.bus.publish(StrategySignalGenerated(
                source="StrategyService",
                symbol=event.symbol,
                strategy_name=name,
                direction=direction,
                price=float(row["close"]),
                metadata={"features": row.to_dict()}
            ))
