from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Dict, Any, Callable, Optional
from sklearn.model_selection import TimeSeriesSplit
from backtesting.adapter import run_backtest_adapter

def walk_forward_run(
    df_price: pd.DataFrame,
    df_features: pd.DataFrame,
    y: pd.Series,
    strategy_factory: Callable[..., Any],  # returns an object with fit() and predict_proba()
    strategy_params: Dict[str, Any],
    n_splits: int = 5,
    test_size: int = 60,
    initial_cash: float = 100_000.0,
    commission_bps: int = 5,
    slippage_bps: int = 5,
) -> Dict[str, Any]:
    """TimeSeriesSplit walk-forward with per-fold backtests.

    Returns a dict with fold metrics and combined equity.
    """
    # Align features/target to common index
    common = df_features.index.intersection(y.index).intersection(df_price.index)
    X = df_features.loc[common]
    yy = y.loc[common]
    px = df_price.loc[common]

    tscv = TimeSeriesSplit(n_splits=n_splits, test_size=test_size)
    fold_rows = []
    equities = []

    for fold, (tr_idx, te_idx) in enumerate(tscv.split(X)):
        X_tr, y_tr = X.iloc[tr_idx], yy.iloc[tr_idx]
        X_te, y_te = X.iloc[te_idx], yy.iloc[te_idx]
        px_te = px.iloc[te_idx]

        strat = strategy_factory(**strategy_params)
        strat.fit(X_tr, y_tr)

        proba = strat.predict_proba(X_te)
        sig = strat.signals_from_proba(proba)
        signals = pd.Series(sig, index=X_te.index, name="signal")

        rep = run_backtest_adapter(px, signals, initial_cash=initial_cash,
                                   commission_bps=commission_bps, slippage_bps=slippage_bps)
        equity = rep["equity"]
        equities.append(equity)

        stats = rep["stats"]
        row = {"fold": fold, **stats}
        fold_rows.append(row)

    # Combine equities (align & average)
    eq_df = pd.concat(equities, axis=1)
    eq_df.columns = [f"eq_fold_{i}" for i in range(eq_df.shape[1])]
    eq_df = eq_df.ffill().dropna(how="all")
    return {"fold_metrics": pd.DataFrame(fold_rows), "equities": eq_df}