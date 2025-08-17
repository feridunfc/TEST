# src/core/data_normalizer.py
from __future__ import annotations

import logging
import warnings
import pickle
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Optional, Union, List, Iterable, Tuple

import numpy as np
import pandas as pd

# Try importing sklearn bits; fall back gracefully if unavailable
try:
    from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, QuantileTransformer
    from sklearn.exceptions import NotFittedError
    SKLEARN_AVAILABLE = True
except Exception:  # pragma: no cover
    StandardScaler = MinMaxScaler = RobustScaler = QuantileTransformer = object  # type: ignore
    class NotFittedError(Exception):
        pass
    SKLEARN_AVAILABLE = False


class NormalizationMethod(Enum):
    ZSCORE = auto()
    MINMAX = auto()
    ROBUST = auto()
    LOG = auto()
    QUANTILE = auto()


class NaNPolicy(Enum):
    DROP = auto()
    FFILL = auto()
    BFILL = auto()
    INTERPOLATE = auto()
    FILL_WITH = auto()


@dataclass
class NormalizationConfig:
    method: NormalizationMethod = NormalizationMethod.ZSCORE
    nan_policy: NaNPolicy = NaNPolicy.FFILL
    fill_value: Optional[float] = None
    clip_outliers: bool = True
    clip_sigma: float = 3.0
    rolling_window: Optional[int] = None
    treat_negative: bool = True  # for LOG method, add offset for negatives
    include_cols: Optional[List[str]] = None  # which columns to normalize
    exclude_cols: Optional[List[str]] = None  # columns to leave untouched
    quantile_output_distribution: str = "normal"  # "normal" or "uniform"
    feature_range: Tuple[float, float] = (0.0, 1.0)  # for MinMax
    # persistence
    state_path: Optional[str] = None


class DataNormalizer:
    """
    Production-grade financial data normalizer.

    * Robust NaN handling policies
    * Multiple normalization methods (ZScore, MinMax, Robust, Log, Quantile)
    * Optional rolling (online) normalization without look-ahead
    * Column selection (include/exclude)
    * Sklearn-compatible interface (fit/transform/fit_transform)
    * State persistence (save_state/load_state)
    """

    def __init__(self, config: Optional[NormalizationConfig] = None):
        self.config = config or NormalizationConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            fmt = logging.Formatter("[%(levelname)s] %(name)s: %(message)s")
            handler.setFormatter(fmt)
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

        self.scaler = None
        self._is_fitted = False
        self._init_scaler()

    # ------------ public API ------------
    def fit(self, data: pd.DataFrame) -> "DataNormalizer":
        df = self._validate_and_prepare(data.copy())
        if self.config.rolling_window:
            # rolling mode => we don't fit globally
            self._is_fitted = True
            return self

        sel = self._select_columns(df)
        if self._requires_sklearn():
            self.scaler.fit(sel.values)
        else:
            # LOG or local QUANTILE fallback => nothing to fit
            pass
        self._is_fitted = True
        self.logger.info(f"Fitted normalizer with method={self.config.method.name} on {sel.shape[1]} cols.")
        return self

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        if not self._is_fitted and not self.config.rolling_window:
            raise NotFittedError("Normalizer must be fitted before transform (or use rolling_window).")

        df = self._validate_and_prepare(data.copy())
        if self.config.rolling_window:
            return self._rolling_transform(df)

        cols_sel = self._selected_col_names(df)
        untouched_cols = [c for c in df.columns if c not in cols_sel]

        # transform selected
        transformed = self._apply_method(df[cols_sel])

        # merge back
        out = df.copy()
        out[cols_sel] = transformed.values

        # clipping
        if self.config.clip_outliers:
            out[cols_sel] = self._clip_outliers(out[cols_sel])

        # untouched columns are preserved as-is
        return out

    def fit_transform(self, data: pd.DataFrame) -> pd.DataFrame:
        return self.fit(data).transform(data)

    def save_state(self, path: Optional[str] = None):
        if not self._is_fitted:
            raise NotFittedError("Cannot save state of an unfitted normalizer")
        path = path or self.config.state_path
        if not path:
            raise ValueError("Path must be provided to save_state")

        state = {
            "config": self.config,
            "sklearn": SKLEARN_AVAILABLE,
            "scaler": self.scaler if self._requires_sklearn() else None,
        }
        with open(path, "wb") as f:
            pickle.dump(state, f)
        self.logger.info(f"Normalizer state saved to {path}")

    def load_state(self, path: Optional[str] = None):
        path = path or self.config.state_path
        if not path:
            raise ValueError("Path must be provided to load_state")
        with open(path, "rb") as f:
            state = pickle.load(f)

        self.config = state["config"]
        self._init_scaler()
        if state.get("scaler") is not None:
            self.scaler = state["scaler"]
        self._is_fitted = True
        self.logger.info(f"Normalizer state loaded from {path}")

    # ------------ internals ------------
    def _init_scaler(self):
        m = self.config.method
        if m == NormalizationMethod.ZSCORE:
            self._ensure_sklearn("ZSCORE")
            self.scaler = StandardScaler()
        elif m == NormalizationMethod.MINMAX:
            self._ensure_sklearn("MINMAX")
            self.scaler = MinMaxScaler(feature_range=self.config.feature_range)
        elif m == NormalizationMethod.ROBUST:
            self._ensure_sklearn("ROBUST")
            self.scaler = RobustScaler()
        elif m == NormalizationMethod.QUANTILE:
            if SKLEARN_AVAILABLE:
                self.scaler = QuantileTransformer(
                    output_distribution=self.config.quantile_output_distribution,
                    subsample=10_000, random_state=42
                )
            else:
                self.scaler = None  # we will fallback to rank-gauss in _apply_method
        elif m == NormalizationMethod.LOG:
            self.scaler = None  # handled manually
        else:  # pragma: no cover
            raise ValueError(f"Unknown method: {m}")

    def _ensure_sklearn(self, method: str):
        if not SKLEARN_AVAILABLE:
            self.logger.warning(
                f"scikit-learn not found; method {method} needs sklearn. "
                f"Please install scikit-learn>=1.1. Falling back where possible."
            )

    def _requires_sklearn(self) -> bool:
        return self.config.method in (NormalizationMethod.ZSCORE, NormalizationMethod.MINMAX,
                                      NormalizationMethod.ROBUST, NormalizationMethod.QUANTILE) and SKLEARN_AVAILABLE

    def _validate_and_prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Input must be pandas DataFrame")
        if df.empty:
            raise ValueError("Input data is empty")

        # NaN handling
        df = self._handle_nans(df)

        # LOG negative handling
        if self.config.method == NormalizationMethod.LOG and self.config.treat_negative:
            min_val = df.min(numeric_only=True).min()
            if pd.notnull(min_val) and min_val <= 0:
                offset = abs(min_val) + 1e-9
                df = df + offset

        # ensure numeric dtypes for selected cols
        sel = self._select_columns(df)
        if not all(np.issubdtype(df[c].dtype, np.number) for c in sel.columns):
            non_num = [c for c in sel.columns if not np.issubdtype(df[c].dtype, np.number)]
            raise TypeError(f"Selected columns must be numeric. Non-numeric: {non_num}")

        return df

    def _handle_nans(self, df: pd.DataFrame) -> pd.DataFrame:
        if not df.isnull().values.any():
            return df

        p = self.config.nan_policy
        if p == NaNPolicy.DROP:
            return df.dropna()
        elif p == NaNPolicy.FFILL:
            return df.ffill().dropna()
        elif p == NaNPolicy.BFILL:
            return df.bfill().dropna()
        elif p == NaNPolicy.INTERPOLATE:
            return df.interpolate(method="time").ffill().bfill().dropna()
        elif p == NaNPolicy.FILL_WITH:
            if self.config.fill_value is None:
                raise ValueError("fill_value must be set for FILL_WITH policy")
            return df.fillna(self.config.fill_value)
        else:  # pragma: no cover
            raise ValueError(f"Unknown NaN policy: {p}")

    def _selected_col_names(self, df: pd.DataFrame) -> List[str]:
        include = self.config.include_cols or list(df.columns)
        exclude = set(self.config.exclude_cols or [])
        return [c for c in include if c in df.columns and c not in exclude]

    def _select_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[self._selected_col_names(df)]

    def _apply_method(self, df_sel: pd.DataFrame) -> pd.DataFrame:
        m = self.config.method

        if m == NormalizationMethod.LOG:
            # natural log scaling
            with np.errstate(divide="ignore"):
                out = np.log(df_sel.values + 1e-12)
            return pd.DataFrame(out, index=df_sel.index, columns=df_sel.columns)

        if m == NormalizationMethod.QUANTILE and not SKLEARN_AVAILABLE:
            # rank-gauss fallback
            def rank_gauss(col):
                r = col.rank(method="average").to_numpy()
                denom = len(col) + 1.0
                u = r / denom  # (0,1)
                # map to normal with inverse CDF (approx via scipy not guaranteed here)
                # use numpy approximation via erf^-1
                from math import sqrt
                from numpy import clip
                u = clip(u, 1e-6, 1 - 1e-6)
                # Approx inverse CDF using erfinv: Phi^{-1}(u) = sqrt(2)*erfinv(2u-1)
                from numpy import sqrt as np_sqrt
                from numpy import erfinv
                return np_sqrt(2.0) * erfinv(2*u - 1)
            out = df_sel.apply(rank_gauss)
            return out

        if self._requires_sklearn():
            arr = self.scaler.transform(df_sel.values)
            return pd.DataFrame(arr, index=df_sel.index, columns=df_sel.columns)

        # if we get here, something unexpected happened
        raise RuntimeError(f"Method {m.name} requires sklearn or is not supported.")

    def _rolling_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Look-ahead safe rolling normalization: fit scaler on [i-window, i) then transform i."""
        window = int(self.config.rolling_window)
        cols_sel = self._selected_col_names(df)
        out = pd.DataFrame(index=df.index, columns=cols_sel, dtype=float)

        for i in range(len(df)):
            if i < window:
                continue  # not enough history
            hist = df.iloc[i-window:i][cols_sel]
            x = df.iloc[i:i+1][cols_sel]
            # fit temporary scaler
            tmp_cfg = NormalizationConfig(**{**self.config.__dict__, "rolling_window": None})
            tmp = DataNormalizer(tmp_cfg)
            tmp.fit(hist)
            out.iloc[i] = tmp.transform(x).iloc[0].values

        # merge back into original DataFrame
        res = df.copy()
        res[cols_sel] = out[cols_sel]
        # drop leading NaNs introduced by rolling
        return res.dropna()

    def _clip_outliers(self, df_sel: pd.DataFrame) -> pd.DataFrame:
        if self.config.method == NormalizationMethod.MINMAX:
            lo, hi = self.config.feature_range
            return df_sel.clip(lo, hi)
        sigma = float(self.config.clip_sigma)
        mean = df_sel.mean()
        std = df_sel.std(ddof=0).replace(0, np.nan)
        lower = mean - sigma * std
        upper = mean + sigma * std
        return df_sel.clip(lower=lower, upper=upper, axis=1)


class FinancialDataNormalizer(DataNormalizer):
    """Financial-data friendly normalizer with better negative handling for LOG method."""

    def __init__(self, config: Optional[NormalizationConfig] = None):
        cfg = config or NormalizationConfig()
        super().__init__(cfg)

    def _validate_and_prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        df = super()._validate_and_prepare(df)
        # Additional financial sanity checks can be added here
        return df


def create_normalizer(kind: str = "financial", config: Optional[NormalizationConfig] = None) -> DataNormalizer:
    kind = (kind or "financial").lower()
    if kind in ("financial", "fin", "quant"):
        return FinancialDataNormalizer(config)
    return DataNormalizer(config)
