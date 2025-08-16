# src/anomaly/detector.py
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Union

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

@dataclass
class AnomalyAlert:
    timestamp: datetime
    metric: str
    value: float
    threshold: float
    severity: str
    description: str

class AnomalyDetector:
    def __init__(self, config: Dict):
        self.config = config
        self.models: Dict[str, IsolationForest] = {}
        self.history = pd.DataFrame(columns=["timestamp", "metric", "value"])

    def _model_for(self, metric: str) -> IsolationForest:
        if metric not in self.models:
            params = self.config.get("isolation_forest", {"n_estimators": 100, "contamination": 0.05})
            self.models[metric] = IsolationForest(**params)
        return self.models[metric]

    def detect(self, data: Union[pd.DataFrame, Dict], metric: str = "price") -> List[AnomalyAlert]:
        if isinstance(data, dict):
            data = pd.DataFrame([data])
        self._update_history(data, metric)
        if len(self.history) <= self.config.get("min_samples", 100):
            return []
        model = self._model_for(metric)
        hist_metric = self.history[self.history["metric"] == metric][["value"]]
        model.fit(hist_metric)
        preds = model.predict(data[["value"]])
        scores = model.decision_function(data[["value"]])

        alerts: List[AnomalyAlert] = []
        for i, (pred, score) in enumerate(zip(preds, scores)):
            if pred == -1:
                alerts.append(
                    AnomalyAlert(
                        timestamp=pd.to_datetime(data.iloc[i]["timestamp"]).to_pydatetime(),
                        metric=metric,
                        value=float(data.iloc[i]["value"]),
                        threshold=float(score),
                        severity=self._severity(score),
                        description=f"{metric} anomaly detected",
                    )
                )
        return alerts

    def detect_multivariate(self, df: pd.DataFrame) -> List[AnomalyAlert]:
        out: List[AnomalyAlert] = []
        for col in df.columns:
            if col == "timestamp":
                continue
            sub = df[["timestamp", col]].rename(columns={col: "value"})
            out.extend(self.detect(sub, metric=col))
        return out

    def _update_history(self, new_data: pd.DataFrame, metric: str):
        new = new_data.copy()
        new["metric"] = metric
        self.history = pd.concat([self.history, new], ignore_index=True)
        max_history = self.config.get("max_history", 1000)
        if len(self.history) > max_history:
            self.history = self.history.iloc[-max_history:]

    def _severity(self, score: float) -> str:
        if score < -0.5:
            return "CRITICAL"
        if score < -0.3:
            return "HIGH"
        if score < -0.1:
            return "MEDIUM"
        return "LOW"
