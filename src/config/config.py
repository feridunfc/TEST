from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class DataConfig:
    source: str = "yfinance"
    symbol: str = "SPY"
    start: str = "2015-01-01"
    end: Optional[str] = None
    interval: str = "1d"

@dataclass
class FeesConfig:
    commission: float = 0.0005  # 5 bps one-way commission
    slippage_bps: float = 1.0   # 1 bp slippage per trade

@dataclass
class RiskConfig:
    vol_target: float = 0.15       # annualized target volatility
    max_drawdown: float = 0.25     # portfolio-level hard stop
    position_cap: float = 1.0      # |position| <= 1.0 (100% of capital)

@dataclass
class BacktestConfig:
    walkforward_splits: int = 5
    rebalance_delay: int = 1  # bars delay to avoid look-ahead
    cash: float = 1.0

@dataclass
class AppConfig:
    data: DataConfig = field(default_factory=DataConfig)
    fees: FeesConfig = field(default_factory=FeesConfig)
    risk: RiskConfig = field(default_factory=RiskConfig)
    backtest: BacktestConfig = field(default_factory=BacktestConfig)

def load_config(overrides: Optional[Dict[str, Any]] = None) -> AppConfig:
    cfg = AppConfig()
    if overrides:
        # shallow override: cfg.<section>.<key> = value
        for k, v in overrides.items():
            if hasattr(cfg, k) and isinstance(v, dict):
                section = getattr(cfg, k)
                for kk, vv in v.items():
                    if hasattr(section, kk):
                        setattr(section, kk, vv)
            elif hasattr(cfg, k):
                setattr(cfg, k, v)
    return cfg
