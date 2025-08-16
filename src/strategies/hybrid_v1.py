import pandas as pd
from .base_strategy import BaseStrategy

class HybridV1Strategy(BaseStrategy):
    def __init__(self, params=None):
        super().__init__("hybrid_v1", params)
        self.rsi_buy = float(self.params.get("rsi_buy", 35))
        self.rsi_sell = float(self.params.get("rsi_sell", 65))
        self.min_anomaly_for_entry = float(self.params.get("min_anomaly_for_entry", 0.0))
        self.min_sentiment = float(self.params.get("min_sentiment", -1.0))
        self.period = int(self.params.get("rsi_period", 14))

    def _rsi(self, series: pd.Series, period: int = 14) -> pd.Series:
        delta = series.diff()
        up = delta.clip(lower=0).rolling(period).mean()
        down = -delta.clip(upper=0).rolling(period).mean()
        rs = up / (down + 1e-12)
        return 100 - (100 / (1 + rs))

    def predict(self, df: pd.DataFrame) -> pd.Series:
        c = df["close"].astype(float)
        rsi = self._rsi(c, self.period)

        regime = df["regime"] if "regime" in df.columns else pd.Series(1, index=df.index)
        anomaly = df["anomaly_score"] if "anomaly_score" in df.columns else pd.Series(0.0, index=df.index)
        sentiment = df["sentiment_score"] if "sentiment_score" in df.columns else pd.Series(0.0, index=df.index)

        long_cond = (rsi < self.rsi_buy) & (anomaly >= self.min_anomaly_for_entry) & (sentiment >= self.min_sentiment) & (regime >= 0)
        short_cond = (rsi > self.rsi_sell) & (anomaly >= self.min_anomaly_for_entry) & (regime < 0)

        sig = long_cond.astype(int) - short_cond.astype(int)
        sig = sig.shift(1).fillna(0.0)
        sig.name = "signal"
        return sig
