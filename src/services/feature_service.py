from __future__ import annotations
import json
import pandas as pd
from ..core.bus.event_bus import event_bus
from ..core.events.data_events import BarDataEvent, DataSnapshotReady
from ..core.events.strategy_events import FeaturesReady
from ..engines.feature_engineer_engine import FeatureEngineerEngine
from ..configs.main_config import FeatureConfig

class FeatureService:
    def __init__(self, cfg: FeatureConfig):
        self.bus = event_bus
        self.engine = FeatureEngineerEngine(cfg)
        self.df_hist = None
        self.features_df = None
        self.bus.subscribe(DataSnapshotReady, self.on_snapshot_ready)
        self.bus.subscribe(BarDataEvent, self.on_bar)

    def on_snapshot_ready(self, event: DataSnapshotReady):
        df = pd.read_json(event.df_json, orient="split")
        self.df_hist = df
        self.features_df = self.engine.compute_batch(df)

    def on_bar(self, event: BarDataEvent):
        if self.features_df is None:
            return
        # take last row features as current
        row = self.features_df.loc[pd.to_datetime(event.index_ts)]
        self.bus.publish(FeaturesReady(
            source="FeatureService",
            symbol=event.symbol,
            features_json=row.to_json()
        ))
