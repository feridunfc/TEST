
import numpy as np
import pandas as pd

class VolatilityPositionSizer:
    def __init__(self, target_annual_vol: float = 0.20, lookback_days: int = 30, max_position_weight_pct: float = 0.10):
        self.target_daily_vol = target_annual_vol / np.sqrt(252.0)
        self.lookback = lookback_days
        self.max_w = max_position_weight_pct

    def calculate_size_value(self, close: pd.Series, portfolio_value: float) -> float:
        returns = close.pct_change().dropna()
        if len(returns) < max(2, self.lookback // 2):
            return 0.0
        realized = returns[-self.lookback:].std()
        if realized == 0 or np.isnan(realized):
            return 0.0
        value = (self.target_daily_vol / realized) * portfolio_value
        return min(value, portfolio_value * self.max_w)
