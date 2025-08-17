
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class Config:
    # Portfolio
    INITIAL_BALANCE: float = 100_000.0
    BASE_POSITION_SIZE: float = 0.03         # base 3% per asset
    MIN_POSITION_SIZE: float = 0.002         # 0.2% min
    MAX_DAILY_LOSS: float = 0.06             # 6% halt
    MAX_DRAWDOWN: float = 0.35               # 35% halt
    HALT_IN_CRISIS: bool = True

    # Risk normalization params per metric
    RISK_NORMALIZATION: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        # values assumed in *daily* std space or unitless normalizations
        "volatility": {"min": 0.005, "max": 0.06, "inverse": False},
        "liquidity":  {"min": 1e5,  "max": 5e7,  "inverse": True},  # higher liquidity -> lower risk (inverse)
        "drawdown":   {"min": 0.0,  "max": 0.6,  "inverse": False},
        "fundamental":{"min": 0.0,  "max": 1.0,  "inverse": False},
        "concentration": {"min": 0.0, "max": 0.5, "inverse": False},
    })

    # Per-asset overrides for max allocation (0..1)
    MAX_ALLOCATION: Dict[str, float] = field(default_factory=dict)
    DEFAULT_MAX_ALLOCATION: float = 0.15      # fallback 15%
