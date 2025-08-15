from dataclasses import dataclass, field
from typing import Optional

@dataclass
class DataConfig:
    symbol: str = "SPY"
    start: str = "2018-01-01"
    end: Optional[str] = None
    interval: str = "1d"

@dataclass
class FeesConfig:
    commission: float = 0.0005   # 5 bps round-trip approx
    slippage_bps: float = 2.0    # per trade bps

@dataclass
class RiskConfig:
    max_dd: float = 0.3
    vol_target: float = 0.2

@dataclass
class AppConfig:
    data: DataConfig = field(default_factory=DataConfig)
    fees: FeesConfig = field(default_factory=FeesConfig)
    risk: RiskConfig = field(default_factory=RiskConfig)

def load_config() -> AppConfig:
    return AppConfig()