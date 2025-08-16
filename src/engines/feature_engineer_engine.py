
import pandas as pd
import numpy as np
from detectors.market_regime_detector import MarketRegimeDetector
from detectors.anomaly_detector import AnomalyDetector

class FeatureEngineerEngine:
    def __init__(self, regime_params=None, anomaly_params=None):
        self.regime = MarketRegimeDetector(**(regime_params or {}))
        self.anomaly = AnomalyDetector(**(anomaly_params or {}))
        self._trained = False
        self._df = pd.DataFrame()

    def reset(self):
        self._trained = False
        self._df = pd.DataFrame()

    def update_with_bar(self, bar: dict, in_sample: bool):
        # append bar to internal df
        s = pd.Series(bar, name=bar['index'])
        self._df = pd.concat([self._df, s.to_frame().T])
        df = self._df.copy()

        # basic TA
        df['ret'] = df['close'].pct_change()
        df['ma_fast'] = df['close'].rolling(20).mean()
        df['ma_slow'] = df['close'].rolling(50).mean()

        # regime/anomaly
        if not self._trained and in_sample and len(df) > 100:
            # "fit" stage (for detectors needing training)
            _ = self.regime.fit_transform(df)
            _ = self.anomaly.fit_predict(df)
            self._trained = True

        regime = self.regime.fit_transform(df) if self._trained else pd.Series(0, index=df.index)
        anomaly = self.anomaly.fit_predict(df) if self._trained else pd.Series(0, index=df.index)

        df['regime'] = regime
        df['anomaly'] = anomaly

        # last row as features
        last = df.iloc[-1].copy()
        tail = df.iloc[-200:].copy()
        return last, tail
