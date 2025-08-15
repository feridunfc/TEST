from __future__ import annotations
import pandas as pd
import numpy as np
import yfinance as yf

from config.config import AppConfig, load_config
from pipeline.backtest import simple_backtest
from core.strategies import ALL_STRATEGIES

# ---------- data utilities ----------
def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        # yfinance may return MultiIndex (field, ticker) or (ticker, field)
        levels = [df.columns.get_level_values(i).str.lower() for i in range(df.columns.nlevels)]
        # try to find field level
        # heuristic: choose level containing 'close'/'adj close'
        if "close" in levels[0].unique().tolist() or "adj close" in levels[0].unique().tolist():
            field_level = 0
        elif "close" in levels[1].unique().tolist() or "adj close" in levels[1].unique().tolist():
            field_level = 1
        else:
            # fallback: take first level as field
            field_level = 0

        out = pd.DataFrame(index=df.index)
        def pick(field_name: str) -> pd.Series | None:
            lname = field_name.lower()
            try:
                cols = [c for c in df.columns if c[field_level].lower() == lname]
                if not cols:
                    return None
                sub = df.loc[:, cols]
                # pick first column if multiple tickers
                s = sub.iloc[:, 0]
                return pd.to_numeric(s, errors="coerce")
            except Exception:
                return None

        for key, outname in [
            ("open", "open"),
            ("high", "high"),
            ("low", "low"),
            ("close", "close"),
            ("adj close", "adj_close"),
            ("volume", "volume"),
        ]:
            s = pick(key)
            if s is not None:
                out[outname] = s
        if "close" not in out and "adj_close" in out:
            out["close"] = out["adj_close"]
        return out

    # Single-level columns
    mapping = {
        "open":"open","high":"high","low":"low","close":"close",
        "adj close":"adj_close","adj_close":"adj_close","volume":"volume",
        "Open":"open","High":"high","Low":"low","Close":"close","Adj Close":"adj_close","Volume":"volume",
    }
    cols = {c: mapping.get(c, c) for c in df.columns}
    out = df.rename(columns=cols).copy()
    if "close" not in out.columns and "adj_close" in out.columns:
        out["close"] = out["adj_close"]
    # keep only known columns (but tolerate missing ones)
    keep = [c for c in ["open","high","low","close","adj_close","volume"] if c in out.columns]
    return out[keep]

def _validate(df: pd.DataFrame) -> pd.DataFrame:
    if "close" not in df.columns:
        raise ValueError("DataFrame must contain 'close' column after normalization")
    # basic sanity
    df = df.sort_index()
    df = df[~df.index.duplicated(keep="first")]
    return df

def _load_data(cfg: AppConfig) -> pd.DataFrame:
    df = yf.download(cfg.data.symbol, start=cfg.data.start, end=cfg.data.end, interval=cfg.data.interval, progress=False)
    if df is None or len(df) == 0:
        raise ValueError("yfinance returned no data")
    df = _normalize_columns(df)
    df = _validate(df).copy()
    df = df.ffill().dropna(subset=["close"])
    return df

# ---------- orchestrator ----------
def run_pipeline(
    strategy_name: str,
    params: dict | None = None,
    cfg: AppConfig | None = None,
    wf_n_splits: int | None = None,
):
    cfg = cfg or load_config()
    df = _load_data(cfg)

    if strategy_name not in ALL_STRATEGIES:
        raise ValueError(f"Unknown strategy: {strategy_name}")
    strat_cls = ALL_STRATEGIES[strategy_name]
    strat = strat_cls(params or {})

    signal = strat.generate_signals(df)
    out, stats = simple_backtest(df, signal, commission=cfg.fees.commission, slippage_bps=cfg.fees.slippage_bps)

    info = {
        "strategy": strategy_name,
        "params": params or {},
        "stats": stats,
    }
    return out, info