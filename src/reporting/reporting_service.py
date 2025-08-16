from typing import Dict
import pandas as pd
from ..engines.metrics_engine import MetricsEngine

def build_report_from_equity(equity: pd.Series) -> Dict[str, float]:
    metrics = MetricsEngine.compute_all(equity)
    return metrics
