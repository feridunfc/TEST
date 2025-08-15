from __future__ import annotations
import pandas as pd
from typing import Dict, Any, Optional, Tuple
import numpy as np
from config.config import AppConfig, DataConfig, FeesConfig, RiskConfig, load_config
from utils.features import validate_ohlc, add_basic_indicators
from pipeline.backtest import simple_backtest
from pipeline.walkforward import run_walkforward
from core.strategies import get_strategy_class, list_ai_models

def _normalize_yf(df: pd.DataFrame) -> pd.DataFrame:
    # yfinance returns columns like ['Open','High','Low','Close','Adj Close','Volume']
    cols = {c.lower(): c for c in df.columns}
    # map to lowercase then select
    ldf = pd.DataFrame(index=df.index)
    for k in ['open','high','low','close','volume']:
        if k in cols:
            ldf[k] = df[cols[k]]
        elif k.capitalize() in df.columns:
            ldf[k] = df[k.capitalize()]
        else:
            # some intervals miss volume -> fill 0
            if k == 'volume':
                ldf[k] = 0.0
            else:
                raise ValueError(f"yfinance missing column: {k}")
    return ldf

def _load_data(cfg: AppConfig) -> pd.DataFrame:
    if cfg.data.source == "yfinance":
        import yfinance as yf
        df = yf.download(
            cfg.data.symbol,
            start=cfg.data.start,
            end=cfg.data.end,
            interval=cfg.data.interval,
            progress=False,
        )
        if isinstance(df.columns, pd.MultiIndex):
            df = df.droplevel(0, axis=1)
        df = _normalize_yf(df)
    else:
        raise NotImplementedError(f"Unknown data source {cfg.data.source}")
    if not validate_ohlc(df):
        raise ValueError("Data validation failed")
    return df

def _make_features(df: pd.DataFrame) -> pd.DataFrame:
    return add_basic_indicators(df)

def run_single(strategy_name: str, params: Optional[Dict[str, Any]] = None, cfg: Optional[AppConfig] = None):
    cfg = cfg or load_config()
    df = _load_data(cfg)
    fdf = _make_features(df)
    Strat = get_strategy_class(strategy_name)
    strat = Strat(**(params or {}))
    sig = strat.generate_signal(fdf).astype(float).clip(-1, 1)
    bt = simple_backtest(
        fdf, sig,
        commission=cfg.fees.commission,
        slippage_bps=cfg.fees.slippage_bps,
        delay=cfg.backtest.rebalance_delay,
        vol_target=cfg.risk.vol_target,
        max_drawdown=cfg.risk.max_drawdown
    )
    info = {
        "stats": bt["stats"],
        "equity": bt["equity"],
        "returns": bt["returns"],
        "signal": sig
    }
    return fdf, info

def run_walkforward_pipeline(strategy_name: str, params: Optional[Dict[str, Any]] = None,
                             cfg: Optional[AppConfig] = None, n_splits: Optional[int] = None):
    cfg = cfg or load_config()
    df = _load_data(cfg)
    fdf = _make_features(df)
    Strat = get_strategy_class(strategy_name)

    def make_sig(full_df, split):
        tr_idx, te_idx = split
        strat = Strat(**(params or {}))
        sig = strat.generate_signal(full_df)
        # keep only test slice
        mask = pd.Series(0.0, index=full_df.index)
        mask.iloc[te_idx] = 1.0
        return (sig * mask).replace(0.0, np.nan)

    wf = run_walkforward(fdf, make_sig, n_splits=n_splits or cfg.backtest.walkforward_splits)
    sig = wf["signal"].fillna(0.0)
    bt = simple_backtest(
        fdf, sig,
        commission=cfg.fees.commission,
        slippage_bps=cfg.fees.slippage_bps,
        delay=cfg.backtest.rebalance_delay,
        vol_target=cfg.risk.vol_target,
        max_drawdown=cfg.risk.max_drawdown
    )
    info = {
        "stats": bt["stats"],
        "equity": bt["equity"],
        "returns": bt["returns"],
        "signal": sig
    }
    return fdf, info

# Facade for UI
def run_pipeline(strategy_name: str, params: Optional[Dict[str, Any]] = None,
                 cfg: Optional[AppConfig] = None, mode: str = "simple"):
    if mode == "walkforward":
        return run_walkforward_pipeline(strategy_name, params=params, cfg=cfg)
    return run_single(strategy_name, params=params, cfg=cfg)

def list_models():
    return list_ai_models()
