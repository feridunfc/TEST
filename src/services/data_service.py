
import pandas as pd
from typing import Optional
import logging

try:
    import yfinance as yf
except Exception:  # pragma: no cover
    yf = None

from core.bus.event_bus import event_bus
from core.events.data_events import DataFetchRequested, CleanedDataReady

log = logging.getLogger("DataService")

def _normalize_yf(df: pd.DataFrame) -> pd.DataFrame:
    # Accept either lower-case or capitalized columns from yfinance
    cols = {c.lower(): c for c in df.columns}
    required = ["open", "high", "low", "close", "volume"]
    # Map present columns to lower-case view
    out = {}
    for r in required:
        if r in cols:
            out[r] = df[cols[r]].astype(float)
        elif r.capitalize() in df.columns:
            out[r] = df[r.capitalize()].astype(float)
        else:
            raise ValueError(f"Missing column from yfinance: {r}")
    out_df = pd.DataFrame(out, index=df.index)
    out_df.index = pd.to_datetime(out_df.index)
    return out_df.sort_index()

class DataService:
    def __init__(self) -> None:
        event_bus.subscribe(DataFetchRequested, self.on_fetch)

    def on_fetch(self, ev: DataFetchRequested) -> None:
        log.info(f"[DataService] Fetching {ev.symbol} {ev.interval} {ev.start}→{ev.end} via {ev.source}")
        if ev.source == "yfinance":
            if yf is None:
                raise RuntimeError("Please install yfinance")
            raw = yf.download(ev.symbol, start=ev.start, end=ev.end, interval=ev.interval, progress=False)
            df = _normalize_yf(raw)
        else:
            raise NotImplementedError(f"Unknown data source: {ev.source}")
        event_bus.publish(CleanedDataReady(source="DataService", symbol=ev.symbol, df=df))
