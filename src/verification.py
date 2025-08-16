from .data_quality import verify_implementation
from .monitoring.dashboard import PerformanceTracker
from .risk.checks import RiskChecks
from .engines.metrics_engine import MetricsEngine
import pandas as pd

def verify_all(repo_path="."):
    rep = verify_implementation(repo_path)
    perf = PerformanceTracker().snapshot()
    idx = pd.date_range("2023-01-01", periods=100, freq="B")
    eq = pd.Series(100000 * (1 + 0.001)**(range(100)), index=idx, name="equity")
    metrics = MetricsEngine.compute_all(eq)
    risk_ok = RiskChecks.verify_risk_controls({"risk_controls": {"kelly":True,"vol_target":True,"max_dd":True,"daily_loss_limit":True,"min_volume":True,"max_position_%":True}})
    return {"data_quality": rep, "perf": perf, "metrics_sample": metrics, "risk_controls": risk_ok}
