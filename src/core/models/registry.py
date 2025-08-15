from __future__ import annotations
from typing import Dict, List, Type
from .base import BaseModel
from .sklearn_models import RandomForestModel, LogisticModel

REGISTRY: Dict[str, Type[BaseModel]] = {
    RandomForestModel.name: RandomForestModel,
    LogisticModel.name: LogisticModel,
}

try:
    from .lightgbm_model import LightGBMModel
    REGISTRY[LightGBMModel.name] = LightGBMModel
except Exception:
    pass

try:
    from .xgboost_model import XGBoostModel
    REGISTRY[XGBoostModel.name] = XGBoostModel
except Exception:
    pass

def list_models() -> List[str]:
    return sorted(list(REGISTRY.keys()))

def get_model(name: str) -> BaseModel:
    if name not in REGISTRY: raise ValueError(f"Unknown model '{name}'")
    return REGISTRY[name]()
