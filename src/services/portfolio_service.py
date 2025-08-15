
import logging
from typing import Optional, List, Tuple
from collections import OrderedDict

from core.bus.event_bus import event_bus
from core.events.data_events import BarDataEvent
from core.events.risk_events import RiskAssessmentCompleted
from core.events.portfolio_events import PortfolioUpdated
from core.events.backtest_events import BacktestCompleted

log = logging.getLogger("PortfolioService")

class PortfolioService:
    def __init__(self, start_equity: float = 1_000_000.0) -> None:
        self.equity = float(start_equity)
        self.prev_close: Optional[float] = None
        self.position: float = 0.0   # applied position (lagged by 1 bar)
        self.pending_target: Optional[float] = None
        self.timeline: List[Tuple] = []  # (dt, equity, position, pnl)
        event_bus.subscribe(BarDataEvent, self.on_bar)
        event_bus.subscribe(RiskAssessmentCompleted, self.on_risk)

    def on_risk(self, ev: RiskAssessmentCompleted) -> None:
        # Apply new target on the *next* bar
        self.pending_target = float(ev.desired_position)

    def on_bar(self, ev: BarDataEvent) -> None:
        if self.prev_close is None:
            self.prev_close = float(ev.close)
            # No PnL on first bar
            event_bus.publish(PortfolioUpdated(
                source="PortfolioService", symbol=ev.symbol, dt=ev.dt,
                equity=self.equity, position=self.position, pnl=0.0
            ))
            self.timeline.append((ev.dt, self.equity, self.position, 0.0))
            return

        r = (float(ev.close) / self.prev_close) - 1.0 if self.prev_close != 0 else 0.0
        pnl = self.equity * (r * self.position)
        self.equity += pnl
        self.prev_close = float(ev.close)

        # After computing pnl for current bar, roll position if a new target exists
        if self.pending_target is not None:
            self.position = float(self.pending_target)
            self.pending_target = None

        event_bus.publish(PortfolioUpdated(
            source="PortfolioService", symbol=ev.symbol, dt=ev.dt,
            equity=self.equity, position=self.position, pnl=pnl
        ))
        self.timeline.append((ev.dt, self.equity, self.position, pnl))

    # Helper for reporters
    def export_equity_curve(self):
        from pandas import DataFrame
        return DataFrame(self.timeline, columns=['dt','equity','position','pnl']).set_index('dt')
