from typing import Type
import optuna, pandas as pd
from ..strategies.base import Strategy
from ..backtest.wf_runner import WalkForwardAdapter
from ..backtest.wf_runner import BacktestEngine  # if real engine exists, it's imported

class OptunaOptimizer:
    def __init__(self, strategy_class: Type[Strategy], n_trials: int = 50, seed: int = 42):
        self.strategy_class = strategy_class
        self.n_trials = n_trials
        self.seed = seed

    def optimize(self, data: pd.DataFrame):
        sampler = optuna.samplers.TPESampler(seed=self.seed)
        study = optuna.create_study(direction="maximize", sampler=sampler)
        study.optimize(lambda tr: self._objective(tr, data), n_trials=self.n_trials)
        return study

    def _objective(self, trial, data):
        params = self.strategy_class.suggest_params(trial)
        strategy = self.strategy_class(**params)
        wf = WalkForwardAdapter(BacktestEngine())
        res = wf.run(data, strategy)
        return float(res.aggregate().get("sharpe", 0.0))
