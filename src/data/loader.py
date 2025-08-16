
import pandas as pd
from .validation import OHLCValidator, VolumeSpikeDetector, normalize_ohlc_columns, ensure_timezone, InvalidDataError
from .multi_source import load_csv, load_parquet, load_yfinance, load_binance_klines

class DataLoader:
    def __init__(self):
        self.validators = [OHLCValidator(), VolumeSpikeDetector()]
    def _apply_validators(self, df: pd.DataFrame) -> pd.DataFrame:
        for v in self.validators:
            if not v.validate(df):
                raise InvalidDataError(f"Validator failed: {v.__class__.__name__}")
        return df
    def load(self, source_type: str, **kwargs) -> pd.DataFrame:
        if source_type == "csv":
            df = load_csv(kwargs["path"], tz=kwargs.get("tz","UTC"))
        elif source_type == "parquet":
            df = load_parquet(kwargs["path"], tz=kwargs.get("tz","UTC"))
        elif source_type == "yfinance":
            df = load_yfinance(kwargs["symbol"], start=kwargs.get("start"), end=kwargs.get("end"), interval=kwargs.get("interval","1d"), tz=kwargs.get("tz","UTC"))
        elif source_type == "binance":
            df = load_binance_klines(kwargs["symbol"], interval=kwargs.get("interval","1h"), limit=kwargs.get("limit",1000))
        else:
            raise ValueError(f"Unknown source_type: {source_type}")
        df = normalize_ohlc_columns(df)
        df = ensure_timezone(df, kwargs.get("tz","UTC"))
        return self._apply_validators(df)
