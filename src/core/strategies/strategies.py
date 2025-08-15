from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any
import numpy as np
import pandas as pd

from .ai_models import get_model_registry

# -------- Base --------
@dataclass
class BaseStrategy:
    params: Dict[str, Any] = field(default_factory=dict)

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        raise NotImplementedError

# -------- MA Crossover --------
class MovingAverageCrossover(BaseStrategy):
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        ma_fast = int(self.params.get("ma_fast", 20))
        ma_slow = int(self.params.get("ma_slow", 50))
        if ma_fast <= 0 or ma_slow <= 0:
            raise ValueError("ma_fast/ma_slow must be > 0")
        c = df["close"].astype(float)
        f = c.rolling(ma_fast, min_periods=ma_fast).mean()
        s = c.rolling(ma_slow, min_periods=ma_slow).mean()
        # 1D signal: np.where gives 1D array
        raw = np.where(f > s, 1.0, 0.0).astype(float)
        sig = pd.Series(raw, index=df.index, name="signal").shift(1).fillna(0.0)
        return sig

# -------- AI Unified --------
class AIUnifiedStrategy(BaseStrategy):
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        train_ratio = float(self.params.get("train_ratio", 0.7))
        threshold = float(self.params.get("threshold", 0.5))
        model_type = str(self.params.get("model_type", "random_forest")).lower()

        # Features (look-ahead safe)
        c = df["close"].astype(float)
        feats = pd.DataFrame(index=df.index)
        feats["ret1"] = c.pct_change(fill_method=None).fillna(0.0).shift(1).fillna(0.0)
        feats["ret5"] = c.pct_change(5, fill_method=None).fillna(0.0).shift(1).fillna(0.0)
        feats["mom20"] = c.pct_change(20, fill_method=None).fillna(0.0).shift(1).fillna(0.0)

        target = (c.pct_change(fill_method=None).shift(-1) > 0).astype(int)
        data = pd.concat([feats, target.rename("y")], axis=1).dropna()
        if len(data) < 50:
            return pd.Series(0.0, index=df.index, name="signal")

        n_train = max(int(len(data) * train_ratio), 20)
        train = data.iloc[:n_train]
        test = data.iloc[n_train:]

        X_train, y_train = train.drop(columns=["y"]), train["y"]
        X_test = test.drop(columns=["y"])

        reg = get_model_registry()
        Model = reg.get(model_type)
        model = Model()
        model.fit(X_train, y_train)
        proba = model.predict_proba(X_test)  # returns probability of class 1
        proba_series = pd.Series(proba, index=X_test.index)

        sig_test = (proba_series >= threshold).astype(float)
        sig_full = pd.Series(0.0, index=df.index, name="signal")
        sig_full.loc[sig_test.index] = sig_test.values
        # execution lag
        return sig_full.shift(1).fillna(0.0)

# -------- Hybrid (placeholder ensemble: average of MA & AI) --------
class HybridEnsembleStrategy(BaseStrategy):
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        # MA component
        ma_params = {
            "ma_fast": int(self.params.get("ma_fast", 20)),
            "ma_slow": int(self.params.get("ma_slow", 50)),
        }
        ma_sig = MovingAverageCrossover(ma_params).generate_signals(df)
        # AI component
        ai_params = {
            "model_type": self.params.get("model_type", "random_forest"),
            "train_ratio": float(self.params.get("train_ratio", 0.7)),
            "threshold": float(self.params.get("threshold", 0.5)),
        }
        ai_sig = AIUnifiedStrategy(ai_params).generate_signals(df)
        # Combine (average), then threshold at 0.5
        comb = (ma_sig + ai_sig) / 2.0
        return (comb >= 0.5).astype(float).rename("signal")