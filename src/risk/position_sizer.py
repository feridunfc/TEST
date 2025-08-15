
from __future__ import annotations
from typing import Optional
import numpy as np

def volatility_sizer(equity: float, price: float, atr: float, risk_perc: float = 0.01) -> float:
    """ATR tabanlı boyutlandırma. Risk= risk_perc * equity; stop mesafesi ~ ATR.
    qty = (risk_dolar) / ATR  ≈ (risk_perc * equity)/ATR
    """
    if atr is None or atr <= 0 or price <= 0 or equity <= 0:
        return 0.0
    risk_dollar = risk_perc * equity
    qty = risk_dollar / atr
    # qty'yi çok uçuk olmaması için biraz yumuşat
    return max(qty, 0.0)

def clamp_by_exposure(qty: float, price: float, equity: float, max_pos_frac: float) -> float:
    if price <= 0 or equity <= 0:
        return 0.0
    max_qty = max_pos_frac * equity / price
    return float(min(qty, max_qty))

def kelly_fraction(win_prob: float, payoff: float) -> float:
    """Basit Kelly kesri: f* = p - (1-p)/b  (b=payoff ratio)"""
    if payoff <= 0:
        return 0.0
    p = np.clip(win_prob, 0.0, 1.0)
    b = payoff
    f = p - (1-p)/b
    return float(max(0.0, min(f, 1.0)))
