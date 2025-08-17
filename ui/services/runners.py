import pandas as pd
from ...src.backtest.wf_runner import WalkForwardAdapter, BacktestEngine
from ...src.strategies.ai_strategy import AIStrategy

def _load_demo_data() -> pd.DataFrame:
    # Replace with your real loader; this uses the golden sample for demo
    return pd.read_csv("tests/fixtures/golden_sample.csv", parse_dates=["timestamp"], index_col="timestamp")

def run_single():
    data = _load_demo_data()
    eng = BacktestEngine()
    strat = AIStrategy()
    # The engine's run should return an object with .summary or similar;
    # we return a minimal dict if not present.
    try:
        return eng.run(data=data, strategy=strat)
    except Exception as e:
        raise

def run_walk_forward(n_splits=5, test_size=63, gap=1, strategy=None):
    data = _load_demo_data()
    wf = WalkForwardAdapter(BacktestEngine())
    strat = strategy or AIStrategy()
    return wf.run(data=data, strategy=strat, n_splits=n_splits, test_size=test_size, gap=gap)
