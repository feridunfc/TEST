
import pandas as pd
import numpy as np

try:
    from sklearn.ensemble import IsolationForest
except Exception:
    IsolationForest = None

class AnomalyDetector:
    def __init__(self, method='iforest', contamination=0.02, zscore_window=50, z_thresh=3.0):
        self.method = method
        self.contamination = contamination
        self.zscore_window = zscore_window
        self.z_thresh = z_thresh
        self.model = None

    def fit_predict(self, df: pd.DataFrame) -> pd.Series:
        # simple features: returns and volume change
        feats = pd.DataFrame({
            'r': df['close'].pct_change().fillna(0.0),
            'v': df['volume'].pct_change().replace([np.inf, -np.inf], 0.0).fillna(0.0)
        }, index=df.index)

        if self.method == 'iforest' and IsolationForest is not None:
            self.model = IsolationForest(contamination=self.contamination, random_state=42)
            lab = self.model.fit_predict(feats.values)
            # sklearn: -1 anomaly, 1 normal
            anom = pd.Series((lab == -1).astype(int), index=df.index)
            return anom
        else:
            # z-score fallback
            z = (feats['r'] - feats['r'].rolling(self.zscore_window).mean()) / feats['r'].rolling(self.zscore_window).std()
            return (z.abs() > self.z_thresh).astype(int).fillna(0)
