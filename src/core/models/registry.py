import numpy as np, pandas as pd
from typing import Dict, List

_MODELS: Dict[str,type] = {}

def register(name:str):
    def deco(cls): _MODELS[name]=cls; return cls
    return deco

def list_models()->List[str]: return sorted(_MODELS.keys())
def get_model(name:str):
    if name not in _MODELS: raise ValueError(f'unknown model: {name}')
    return _MODELS[name]()

class BaseModel:
    def fit(self, X: pd.DataFrame, y: pd.Series): ...
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray: ...

@register("random_forest")
class RF(BaseModel):
    def __init__(self):
        from sklearn.ensemble import RandomForestClassifier
        self.clf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1, class_weight='balanced_subsample')
    def fit(self, X,y): self.clf.fit(X,y)
    def predict_proba(self, X): return self.clf.predict_proba(X)[:,1]
