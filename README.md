
# v2.9.11 Hotfix (Event-Driven, Walk-Forward, Regime+Anomaly, Risk Upgrades)

## Quick Start
```python
import pandas as pd, numpy as np
from src.core.bus.event_bus import event_bus
from src.core.events.backtest_events import BacktestRequested
from src.services.backtest_service import BacktestingService
from src.utils.windows import WalkForwardConfig

# Wire services by instantiating BacktestingService (it subscribes itself)
_ = BacktestingService()

# Dummy data
idx = pd.date_range("2018-01-01", periods=1500, freq="B")
close = 100*(1+0.0004*np.random.randn(len(idx))).cumprod()
df = pd.DataFrame({"open":close, "high":close*1.001, "low":close*0.999, "close":close, "volume":1e4}, index=idx)

wf = WalkForwardConfig(train_len=504, test_len=126)
feature_cfg = {"regime": {"params": {"vol_window":20,"bull_q":0.35,"bear_q":0.8,"smooth":5}},
               "anomaly": {"params": {"method":"iforest","contamination":0.02}} }

event_bus.publish(BacktestRequested(
    source="example", asset_name="TEST", strategy_name="hybrid_v1", df=df,
    wf_cfg=wf, feature_cfg=feature_cfg, backtest_params={"commission":0.0005,"slippage":0.0002}
))
```

## What's New vs 2.9.10
- AdaptiveDrawdownManager (dynamic DD threshold)
- LiquidityRiskAnalyzer (order-book based checks, async stub)
- OrderBookSlippageModel (LOB-driven fills)
- ResidualAnalyzer (normality, ACF, stationarity; safe if deps missing)
- TimeValidator for event sequences
- AtomicTransaction scaffold for cross-venue atomic ops
- Walk-Forward replay integrated with Feature/Strategy/Risk/Execution/Portfolio/Reporting
- Vectorized PnL engine (next open execution, slippage, commission)

## Notes
- Set PYTHONPATH to include `src` when running examples.
- External deps (statsmodels, sklearn) are optional; modules degrade gracefully.
