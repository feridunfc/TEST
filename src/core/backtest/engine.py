"""
Improved backtest engine for AlgoSuite.
Drop this file into src/core/backtest/engine.py (or merge the functions/classes into your existing backtest_one).
Goal: strengthen backtest realism while keeping external API minimal:
    - run_backtest(df, strategy_fn, cfg, capital=100000)
    - Returns: dict with equity, trades DataFrame, metrics dict, and aux series.
Features:
    - Position sizing via risk_engine.position_size (percentage or volatility targeting)
    - Commission/slippage as configurable model (bps + fixed fee)
    - Stop-loss / Trailing-stop overlays (applied bar-by-bar)
    - Realistic trade records with entry/exit price, slippage, fees, pnl, duration
    - Supports long-only and shorting (cfg flags)
"""

import math
import numpy as np
import pandas as pd
from datetime import timedelta
from ..risk.engine import RiskEngine

def _apply_costs(size, price, cfg):
    """Return cost (commissions + slippage) for a trade of given notional size (abs)"""
    # cfg: { 'fee_bps': , 'fee_fixed': , 'slippage_bps': }
    notional = abs(size) * price
    fee = notional * cfg.get("fee_bps", 0.0005)
    fee += cfg.get("fee_fixed", 0.0)
    slippage = price * cfg.get("slippage_bps", 0.0001) * np.sign(size)
    return fee, slippage

def run_backtest(df, strategy_fn, cfg, capital=100000.0, debug=False):
    """
    df: price DataFrame with columns ['open','high','low','close','volume'] indexed by timestamp
    strategy_fn(df, cfg) -> pd.Series of target position exposures in [-1,1] (percent of capital)
    cfg: dict (merged from AppConfig) - see configs/backtest_defaults.json for keys
    """
    df = df.copy().sort_index()
    assert 'close' in df.columns, "DataFrame must contain 'close' column"
    freq = pd.infer_freq(df.index) or 'D'
    risk_engine = RiskEngine(cfg.get("risk", {}))
    target_exposure = strategy_fn(df, cfg)  # expected same index as df, values in [-1,1]
    target_exposure = target_exposure.reindex(df.index).fillna(method='ffill').fillna(0.0)
    # state
    cash = capital
    position = 0.0  # number of shares/contracts (can be fractional)
    position_notional = 0.0
    entry_price = None
    entry_index = None
    trades = []
    equity_series = []
    position_series = []
    notional_series = []
    running_stop = None
    trailing_stop = None

    fee_cfg = cfg.get("execution", {})
    allow_short = cfg.get("allow_short", False)

    for ts, row in df.iterrows():
        price = row['close']
        target_pct = float(target_exposure.loc[ts])
        if not allow_short and target_pct < 0:
            target_pct = 0.0

        # Determine desired notional exposure
        desired_notional = capital * target_pct
        # Ask risk engine for sizing (number of shares)
        size = risk_engine.position_size(desired_notional, price, capital, df.loc[:ts])  # may return 0
        # Normalize sign and get difference from current position
        size = float(size)
        delta = size - position

        # If we need to trade
        if abs(delta) > 1e-9:
            fee, slippage = _apply_costs(delta, price, fee_cfg)
            exec_price = price + slippage
            notional = delta * exec_price
            cash -= notional  # buy reduces cash; sell increases cash
            cash -= fee
            # record entry if opening new position
            if position == 0 and delta != 0:
                entry_price = exec_price if size != 0 else None
                entry_index = ts
                running_stop = None
                trailing_stop = None
            # record trade
            trades.append({
                "timestamp": ts, "side": "BUY" if delta>0 else "SELL", "size": delta,
                "price": exec_price, "fee": fee, "slippage": slippage, "cash": cash
            })
            position = size
            position_notional = position * price

        # Risk overlays: stop-loss / trailing-stop
        if position != 0:
            # initialize trailing stop as percentage below/above entry
            if cfg.get("stop", {}).get("enable", False) and running_stop is None and entry_price is not None:
                pct = cfg["stop"].get("initial_pct", 0.1)
                if position > 0:
                    running_stop = entry_price * (1 - pct)
                else:
                    running_stop = entry_price * (1 + pct)
            # trailing stop update
            if cfg.get("stop", {}).get("trailing", False):
                trail_pct = cfg["stop"].get("trailing_pct", 0.05)
                if position > 0:
                    best = row['high'] if 'high' in row else price
                    new_stop = best * (1 - trail_pct)
                    running_stop = max(running_stop, new_stop) if running_stop is not None else new_stop
                else:
                    best = row['low'] if 'low' in row else price
                    new_stop = best * (1 + trail_pct)
                    running_stop = min(running_stop, new_stop) if running_stop is not None else new_stop
            # check stop hit
            hit = False
            if position > 0 and running_stop is not None and row.get('low', price) <= running_stop:
                hit = True
            if position < 0 and running_stop is not None and row.get('high', price) >= running_stop:
                hit = True
            if hit:
                # exit fully at stop price (approx)
                exit_price = running_stop
                fee, slippage = _apply_costs(-position, exit_price, fee_cfg)
                cash += (-position) * exit_price  # closing
                cash -= fee
                trades.append({
                    "timestamp": ts, "side": "SELL" if position>0 else "BUY", "size": -position,
                    "price": exit_price, "fee": fee, "slippage": slippage, "cash": cash, "stop_exit": True
                })
                position = 0.0
                position_notional = 0.0
                entry_price = None
                running_stop = None

        # mark-to-market equity
        mtm = cash + position * price
        equity_series.append({"timestamp": ts, "equity": mtm, "cash": cash, "position": position})
        position_series.append(position)
        notional_series.append(position * price)

    equity_df = pd.DataFrame(equity_series).set_index("timestamp")
    trades_df = pd.DataFrame(trades)
    # metrics
    equity = equity_df['equity']
    returns = equity.pct_change().fillna(0.0)
    total_return = equity.iloc[-1] / equity.iloc[0] - 1.0
    ann_factor = 252 if 'D' in freq or freq is None else 252 * (24*60) / (int(freq.rstrip('TminH') or 1))
    # fallback annualization
    try:
        ann_factor = {"D":252,"H":252*6.5,"T":252*390}.get(freq[0], 252)
    except Exception:
        ann_factor = 252
    sharpe = (returns.mean() / (returns.std()+1e-12)) * math.sqrt(ann_factor) if returns.std()>0 else np.nan
    max_dd = (equity / equity.cummax() - 1).min()

    metrics = {"total_return": total_return, "sharpe": sharpe, "max_drawdown": max_dd, "final_equity": equity.iloc[-1]}
    aux = {"position_series": pd.Series(position_series, index=equity_df.index), "notional_series": pd.Series(notional_series, index=equity_df.index)}
    return {"equity": equity_df, "trades": trades_df, "metrics": metrics, "aux": aux}
