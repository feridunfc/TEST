import logging
import pandas as pd
from core.bus.event_bus import EventBus
from core.events.feature_events import FeaturesReady

logger = logging.getLogger("FeatureService")

class FeatureService:
    def __init__(self):
        EventBus.subscribe(FeaturesReady, self.on_features_ready)  # no-op, shows route

    def publish_features(self, symbol: str, features_df: pd.DataFrame):
        logger.debug(f"Features ready for {symbol}, publishing FeaturesReady")
        EventBus.publish(FeaturesReady(symbol=symbol, features_df=features_df))

    def on_features_ready(self, event: FeaturesReady):
        # downstream services (signal/risk) will also subscribe
        pass
