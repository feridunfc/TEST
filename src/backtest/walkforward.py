from typing import Iterator, Tuple
import numpy as np
import pandas as pd

def generate_walkforward_dates(data: pd.DataFrame, train_size: int=252, test_size: int=63) -> Iterator[Tuple[pd.DataFrame, pd.DataFrame]]:
    n = len(data)
    for i in range(0, n - train_size - test_size + 1, test_size):
        train = data.iloc[i:i+train_size]
        test = data.iloc[i+train_size:i+train_size+test_size]
        yield train, test

class WalkforwardRunner:
    def __init__(self, strategy):
        self.strategy = strategy

    def run(self, df: pd.DataFrame, train_size: int=252, test_size: int=63, label_col: str="close") -> pd.Series:
        outputs = []
        for train_df, test_df in generate_walkforward_dates(df, train_size, test_size):
            if hasattr(self.strategy, "train"):
                self.strategy.train(train_df)
            preds = self.strategy.predict(test_df)
            if not isinstance(preds, (pd.Series, pd.DataFrame)):
                preds = pd.Series(np.asarray(preds).ravel(), index=test_df.index, name="signal")
            outputs.append(preds if isinstance(preds, pd.Series) else preds.iloc[:,0])
        if not outputs:
            return pd.Series([], dtype=float, name="signal")
        out = pd.concat(outputs).sort_index()
        out.name = "signal"
        return out
