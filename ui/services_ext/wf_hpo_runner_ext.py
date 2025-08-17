import importlib, pandas as pd, numpy as np
def _load_fixture():
    try:
        return pd.read_csv("tests/fixtures/golden_sample.csv", parse_dates=["timestamp"], index_col="timestamp")
    except Exception:
        idx = pd.date_range("2020-01-01", periods=300, freq="D")
        price = 100 + np.cumsum(np.random.normal(0,1,size=len(idx)))
        df = pd.DataFrame({
            "open": price + np.random.normal(0,0.1,size=len(idx)),
            "high": price + abs(np.random.normal(0,0.5,size=len(idx))),
            "low":  price - abs(np.random.normal(0,0.5,size=len(idx))),
            "close": price + np.random.normal(0,0.1,size=len(idx)),
            "volume": abs(np.random.normal(1e6,1e5,size=len(idx)))
        }, index=idx); df.index.name="timestamp"; return df

def _registry():
    try:
        mod = importlib.import_module("src.strategies.registry")
        return getattr(mod, "STRATEGY_REGISTRY", {})
    except Exception: return {}

def list_strategies(): return list(_registry().keys())

def _wf_engine():
    try: return importlib.import_module("src.backtest.wf_engine").WalkForwardEngine
    except Exception:
        try: return importlib.import_module("backtest_ext.wf_engine_ext").WalkForwardEngineExt
        except Exception: return None

def _hpo_engine():
    try: return importlib.import_module("optimization.hpo_engine").HPOEngine
    except Exception:
        try: return importlib.import_module("optimization_ext.hpo_engine_ext").HPOEngineExt
        except Exception: return None

def run_wf_batch(strategy_keys, wf_splits=5, wf_test=63):
    reg = _registry(); WF = _wf_engine(); data = _load_fixture()
    if not reg or WF is None or not strategy_keys:
        return pd.DataFrame()
    rows = []
    for k in strategy_keys:
        Strat = reg[k]; strat = Strat()
        wf = WF(n_splits=wf_splits, test_size=wf_test)
        rep = wf.run(strat, data)
        agg = rep.aggregate() if hasattr(rep,"aggregate") else getattr(rep,"summary",{})
        rows.append({
            "strategy": k,
            "sharpe": float(agg.get("sharpe", 0.0)),
            "max_dd": float(agg.get("max_dd", 0.0)),
            "win_rate": float(agg.get("win_rate", 0.0)),
            "turnover": float(agg.get("turnover", 0.0))
        })
    df = pd.DataFrame(rows).set_index("strategy")
    return df

def run_hpo(strategy_key: str, n_trials: int = 25, metric: str = "sharpe"):
    HPO = _hpo_engine()
    if HPO is None: return {"best_value":0.0,"best_params":{},"trials":0}
    data = _load_fixture(); hpo = HPO(metric=metric)
    study = hpo.optimize(strategy_key, data, n_trials=n_trials)
    return {"best_value": getattr(study,"best_value",0.0),
            "best_params": getattr(study,"best_params",{}),
            "trials": len(getattr(study,"trials",[]))}
