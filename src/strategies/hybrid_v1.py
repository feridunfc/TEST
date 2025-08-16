
import numpy as np
import pandas as pd
from .base_strategy import BaseStrategy

class HybridV1Strategy(BaseStrategy):
    """TA (MA20/50) + regime + anomaly mixing."""
    def __init__(self, name='hybrid_v1', w_ta=0.5, w_regime=0.3, w_anom=0.2):
        super().__init__(name)
        self.w_ta = w_ta
        self.w_regime = w_regime
        self.w_anom = w_anom

    def signal_for_row(self, row: pd.Series) -> float:
        ta = 0.0
        if pd.notna(row.get('ma_fast')) and pd.notna(row.get('ma_slow')):
            ta = 1.0 if row['ma_fast'] > row['ma_slow'] else -1.0
        regime = float(row.get('regime', 0.0))  # -1,0,1
        anom = -1.0 if row.get('anomaly', 0) == 1 else 0.0  # anomaly => risk-off
        s = self.w_ta*ta + self.w_regime*regime + self.w_anom*anom
        return float(np.clip(s, -1.0, 1.0))
