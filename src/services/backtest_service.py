
import logging
import pandas as pd
from core.bus.event_bus import event_bus
from core.events.backtest_events import BacktestRequested, BacktestCompleted
from core.events.data_events import DataFetchRequested, BarDataEvent, CleanedDataReady

log = logging.getLogger("BacktestingService")

class BacktestingService:
    """Replay-only engine.

    - Listens to BacktestRequested

    - Triggers DataFetchRequested

    - On CleanedDataReady, replays bars as BarDataEvent

    - Emits BacktestCompleted when done

    """
    def __init__(self) -> None:
        event_bus.subscribe(BacktestRequested, self.on_start)
        event_bus.subscribe(CleanedDataReady, self.on_data)

    def on_start(self, ev: BacktestRequested) -> None:
        self._current = ev
        log.info(f"[BacktestingService] Starting replay for {ev.symbol} {ev.start}→{ev.end} {ev.interval}")
        event_bus.publish(DataFetchRequested(
            source="BacktestingService",
            symbol=ev.symbol, start=ev.start, end=ev.end, interval=ev.interval
        ))

    def on_data(self, ev: CleanedDataReady) -> None:
        # Replay historical bars
        df = ev.df
        for dt, row in df.iterrows():
            event_bus.publish(BarDataEvent(
                source="BacktestingService.replay",
                symbol=ev.symbol, dt=dt,
                open=float(row['open']), high=float(row['high']), low=float(row['low']),
                close=float(row['close']), volume=float(row['volume'])
            ))
        # Signal completion
        bt = getattr(self, "_current", None)
        event_bus.publish(BacktestCompleted(
            source="BacktestingService",
            symbol=ev.symbol,
            strategy=(bt.strategy if bt else "unknown"),
            results={}
        ))
        log.info("[BacktestingService] Replay completed.")
