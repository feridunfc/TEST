from typing import Any
import pandas as pd

class BaseStrategy:
    def __init__(self, name: str, params: dict | None = None):
        self.name = name
        self.params = params or {}
        self.is_trained = False

    def train(self, df: pd.DataFrame) -> None:
        self.is_trained = True

    def predict(self, df: pd.DataFrame) -> pd.Series:
        raise NotImplementedError
