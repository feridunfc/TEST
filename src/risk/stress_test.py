from __future__ import annotations
from typing import Dict

class StressTester:
    def __init__(self, scenarios: Dict[str, Dict[str, float]]):
        self.scenarios = scenarios

    def test(self, portfolio_usd: Dict[str, float]) -> Dict[str, Dict[str, float]]:
        total = sum(float(v) for v in portfolio_usd.values()) or 1.0
        out = {}
        for name, moves in self.scenarios.items():
            loss = 0.0
            for sym, val in portfolio_usd.items():
                shock = float(moves.get(sym, 0.0))
                loss += float(val) * shock
            out[name] = {"loss_usd": float(loss), "loss_pct": float(loss/total)}
        return out
