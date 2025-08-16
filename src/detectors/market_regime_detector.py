
import pandas as pd
import numpy as np

class MarketRegimeDetector:
    def __init__(self, vol_window=20, bull_q=0.35, bear_q=0.8, smooth=5):
        self.vol_window = vol_window
        self.bull_q = bull_q
        self.bear_q = bear_q
        self.smooth = smooth

    def fit_transform(self, df: pd.DataFrame) -> pd.Series:
        returns = df['close'].pct_change()
        vol = returns.rolling(self.vol_window).std()
        q_bull = vol.quantile(self.bull_q)
        q_bear = vol.quantile(self.bear_q)
        regime = pd.Series(index=df.index, dtype="int8")
        regime[vol <= q_bull] = 1   # bull (low vol)
        regime[vol >= q_bear] = -1  # bear (high vol)
        regime[(vol > q_bull) & (vol < q_bear)] = 0
        if self.smooth and self.smooth > 1:
            regime = regime.rolling(self.smooth, min_periods=1).median().astype("int8")
        return regime.fillna(0)
