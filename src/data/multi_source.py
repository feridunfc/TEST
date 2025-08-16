from typing import Literal, Optional
import pandas as pd

def load_data(source: Literal["yfinance","csv"], symbol: str, start: Optional[str]=None, end: Optional[str]=None, path: Optional[str]=None) -> pd.DataFrame:
    if source == "csv":
        if not path:
            raise ValueError("path required for csv source")
        df = pd.read_csv(path, parse_dates=True, index_col=0)
        return df
    elif source == "yfinance":
        try:
            import yfinance as yf
        except Exception as e:
            raise RuntimeError("yfinance not installed") from e
        df = yf.download(symbol, start=start, end=end, progress=False)
        return df
    else:
        raise ValueError("unsupported source")
