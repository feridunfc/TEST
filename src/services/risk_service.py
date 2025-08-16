from __future__ import annotations
import json
from ..core.bus.event_bus import event_bus
from ..core.events.strategy_events import StrategySignalGenerated, SignalDirection
from ..core.events.risk_events import RiskAssessmentCompleted
from ..engines.risk_manager_engine import RiskManagerEngine
from ..configs.main_config import RiskConfig

class RiskService:
    def __init__(self, cfg: RiskConfig):
        self.bus = event_bus
        self.engine = RiskManagerEngine(cfg)
        self.current_equity = cfg.initial_cash
        self.atr_last = 1.0
        self.vol_last = cfg.vol_target_annual
        self.bus.subscribe(StrategySignalGenerated, self.on_signal)

    def on_signal(self, event: StrategySignalGenerated):
        price = event.price
        # ATR/Vol placeholders: can be enhanced with true ATR
        decision = self.engine.assess_trade(price, event.direction, self.atr_last, self.current_equity, self.vol_last)
        self.bus.publish(RiskAssessmentCompleted(
            source="RiskService",
            symbol=event.symbol,
            strategy_name=event.strategy_name,
            direction=event.direction,
            position_size_pct=decision.position_size_pct,
            stop_loss_price=decision.stop_loss_price,
            take_profit_price=decision.take_profit_price,
            rationale=decision.rationale,
            price=price
        ))

    def update_equity(self, equity_value: float):
        self.current_equity = equity_value
        self.engine.update_equity(equity_value)
