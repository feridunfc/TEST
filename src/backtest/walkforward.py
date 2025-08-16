
import pandas as pd

def generate_walkforward_dates(data: pd.DataFrame, train_size: int = 252, test_size: int = 63):
    n = len(data)
    i = 0
    while i + train_size + test_size <= n:
        train = data.iloc[i:i+train_size]
        test = data.iloc[i+train_size:i+train_size+test_size]
        yield train, test
        i += test_size

class WalkforwardRunner:
    def __init__(self, strategy):
        self.strategy = strategy

    def run(self, df: pd.DataFrame, train_size: int = 252, test_size: int = 63) -> pd.Series:
        sigs = []
        for train, test in generate_walkforward_dates(df, train_size, test_size):
            if hasattr(self.strategy, "fit"):
                self.strategy.fit(train)
            s = self.strategy.predict(test)
            if not isinstance(s, pd.Series):
                s = pd.Series(s, index=test.index)
            sigs.append(s)
        if not sigs:
            return pd.Series(index=df.index, dtype=float)
        return pd.concat(sigs).reindex(df.index).fillna(0.0)
