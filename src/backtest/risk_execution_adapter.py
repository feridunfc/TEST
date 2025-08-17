from dataclasses import dataclass, field
from typing import Dict, Optional
import json
from pathlib import Path
import pandas as pd

from ..core.risk_chain import DefaultRiskChain, RiskConfig, RiskContext

# Try to import real BacktestEngine; fall back to placeholder
try:
    from .engine import BacktestEngine as _Engine
except Exception:
    from .wf_runner import BacktestEngine as _Engine

@dataclass
class PortfolioState:
    cash: float = 1_000_000.0
    positions: Dict[str, float] = field(default_factory=dict)  # shares or weight
    sector_map: Dict[str, str] = field(default_factory=dict)   # symbol -> sector

class RiskExecutionAdapter:
    """Wraps a BacktestEngine and enforces portfolio constraints via DefaultRiskChain.
    This adapter expects the underlying engine to consume signals/orders produced
    by a strategy. If your engine already has pre/post hooks, you can call
    `pre_order_hook` inside engine with the same logic below.
    """
    def __init__(self, risk_cfg_path: str = "config/default_risk.json"):
        self.engine = _Engine()
        self.risk_cfg_path = Path(risk_cfg_path)
        self.risk_chain = self._load_chain()

    def _load_chain(self) -> DefaultRiskChain:
        cfg = RiskConfig()
        if self.risk_cfg_path.exists():
            raw = json.loads(self.risk_cfg_path.read_text()).get("risk_chain", {})
            # map keys if needed
            kwargs = {}
            if "market_regime_rejection_threshold" in raw:
                kwargs["market_regime_rejection_threshold"] = float(raw["market_regime_rejection_threshold"])
            if "min_adv_pct" in raw:
                kwargs["min_adv_pct"] = float(raw["min_adv_pct"])
            if "max_allocation_per_asset" in raw:
                kwargs["max_allocation_per_asset"] = float(raw["max_allocation_per_asset"])
            if "max_correlation" in raw:
                kwargs["max_correlation"] = float(raw["max_correlation"])
            cfg = RiskConfig(**kwargs)
        return DefaultRiskChain(cfg)

    def _apply_constraints(self, symbol: str, proposed_weight: float, portfolio: PortfolioState,
                           sentiment_score: float = 0.5, anomaly_score: float = 0.0,
                           regime_score: float = 1.0, adv_pct: float = 0.05) -> Optional[float]:
        ctx = RiskContext(
            symbol=symbol,
            features={"regime_score": regime_score},
            sentiment_score=sentiment_score,
            anomaly_score=anomaly_score,
            adv_pct=adv_pct,
            proposed_weight=proposed_weight,
            corr_matrix=None,
            sector=portfolio.sector_map.get(symbol, "unknown")
        )
        decision = self.risk_chain.process(ctx)
        if not decision.ok:
            return None
        return float(decision.weight if decision.weight else proposed_weight)

    def run(self, data: pd.DataFrame, strategy, portfolio: Optional[PortfolioState] = None):
        """Example orchestration:
        1) Get probabilities/signals from strategy
        2) Size them via risk chain
        3) Hand off to underlying engine for fills & PnL
        """
        portfolio = portfolio or PortfolioState()
        if hasattr(strategy, "fit"):
            strategy.fit(data)

        # Strategy must expose predict_proba or signals; we derive weights in [-1,1]
        if hasattr(strategy, "predict_proba"):
            proba = strategy.predict_proba(data)
            signals = strategy.to_signals(proba)
        else:
            # Fallback: zero signals
            signals = pd.Series(0, index=data.index)

        # Map raw signals to weights and enforce constraints per symbol
        # Here we assume single-asset for simplicity; extend for multi-asset
        symbol = "ASSET"
        sized = []
        for ts, sig in signals.items():
            raw_w = float(sig) * 0.1  # 10% notional target per unit signal
            approved_w = self._apply_constraints(symbol, raw_w, portfolio)
            sized.append(approved_w if approved_w is not None else 0.0)
        sized_ser = pd.Series(sized, index=signals.index, name="weight")

        # Hand off to engine; engine should be able to accept weights or signals
        # If your engine requires a specific adapter, replace below accordingly.
        return self.engine.run(data=data, strategy=strategy)
