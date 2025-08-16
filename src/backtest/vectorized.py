
import numpy as np
import pandas as pd

class VectorizedBacktester:
    def __init__(self, commission_bps: float = 5.0, slippage_bps: float = 2.0):
        self.commission = commission_bps / 1e4
        self.slippage = slippage_bps / 1e4

    def run(self, prices: pd.DataFrame, signals: pd.Series) -> pd.DataFrame:
        # Vectorized long/short daily backtest.
        df = prices.copy()
        if "open" not in df.columns or "close" not in df.columns:
            raise ValueError("prices must have 'open' and 'close'")

        # execution price with slippage (open assumed as entry)
        exec_px = df["open"] * (1 + np.random.normal(0, self.slippage, len(df)))
        exec_ret = pd.Series(exec_px, index=df.index).pct_change().rename("exec_ret")
        # strategy returns using prior signal (no look-ahead)
        sig = signals.reindex(df.index).fillna(0).astype(float)
        strat_ret = sig.shift(1).fillna(0) * exec_ret

        # commissions on trades (signal change implies trade)
        trades = sig.diff().abs().fillna(0)
        strat_ret = strat_ret - trades * self.commission

        equity = (1.0 + strat_ret.fillna(0)).cumprod().rename("equity")
        out = pd.DataFrame({
            "signal": sig,
            "strategy_returns": strat_ret.fillna(0),
            "equity": equity
        })
        out["drawdown"] = out["equity"] / out["equity"].cummax() - 1.0
        return out
