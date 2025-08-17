from abc import ABC, abstractmethod
import pandas as pd

class Strategy(ABC):
    @classmethod
    def wf_compatible(cls) -> bool:
        return True

    def fit(self, df: pd.DataFrame) -> None:
        pass

    @abstractmethod
    def predict_proba(self, df: pd.DataFrame) -> pd.Series:
        """Return probabilities (0..1) aligned to df.index"""

    def to_signals(self, proba: pd.Series, threshold: float = 0.5) -> pd.Series:
        sig = proba.copy()
        sig[:] = 0
        sig[proba > threshold] = 1
        sig[proba < (1.0 - threshold)] = -1
        return sig
