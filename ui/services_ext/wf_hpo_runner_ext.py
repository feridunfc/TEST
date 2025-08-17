import importlib
import pandas as pd

def _load_fixture():
    try:
        df = pd.read_csv("tests/fixtures/golden_sample.csv", parse_dates=["timestamp"], index_col="timestamp")
        return df
    except Exception:
        # minimal synthetic fixture
        import numpy as np
        idx = pd.date_range("2022-01-01", periods=300, freq="D")
        price = 100 + np.cumsum(np.random.normal(0,1, size=len(idx)))
        high = price + abs(np.random.normal(0,0.5,size=len(idx)))
        low  = price - abs(np.random.normal(0,0.5,size=len(idx)))
        openp = price + np.random.normal(0,0.1,size=len(idx))
        close = price + np.random.normal(0,0.1,size=len(idx))
        vol = abs(np.random.normal(1e6,1e5,size=len(idx)))
        df = pd.DataFrame({"open":openp,"high":high,"low":low,"close":close,"volume":vol}, index=idx)
        df.index.name="timestamp"
        return df

def _get_registry():
    try:
        mod = importlib.import_module("src.strategies.registry")
        return getattr(mod, "STRATEGY_REGISTRY", {})
    except Exception:
        return {}

def list_strategies():
    reg = _get_registry()
    return list(reg.keys())

def run_wf_batch(strategy_keys, wf_splits=5, wf_test=63):
    # Prefer project WF engine if available; otherwise use our non-invasive ext engine
    reg = _get_registry()
    if not reg:
        return pd.DataFrame()

    try:
        WF = importlib.import_module("src.backtest.wf_engine").WalkForwardEngine
    except Exception:
        WF = importlib.import_module("backtest_ext.wf_engine_ext").WalkForwardEngineExt

    data = _load_fixture()
    rows = []
    for key in strategy_keys:
        Strat = reg[key]
        strat = Strat()
        wf = WF(n_splits=wf_splits, test_size=wf_test)
        rep = wf.run(strat, data)
        agg = rep.aggregate() if hasattr(rep, "aggregate") else getattr(rep, "summary", {"sharpe":0,"max_dd":0,"win_rate":0,"turnover":0})
        agg["strategy"] = key
        rows.append(agg)
    df = pd.DataFrame(rows).set_index("strategy")
    return df[["sharpe","max_dd","win_rate","turnover"]]

def run_hpo(strategy_key: str, n_trials: int = 50, metric: str = "sharpe"):
    # Prefer project HPO engine if available; otherwise use our ext engine
    try:
        HPO = importlib.import_module("optimization.hpo_engine").HPOEngine
    except Exception:
        HPO = importlib.import_module("optimization_ext.hpo_engine_ext").HPOEngineExt
    data = _load_fixture()
    hpo = HPO(metric=metric)
    study = hpo.optimize(strategy_key, data, n_trials=n_trials)
    return {"best_value": getattr(study, "best_value", 0.0),
            "best_params": getattr(study, "best_params", {}),
            "trials": len(getattr(study, "trials", []))}
