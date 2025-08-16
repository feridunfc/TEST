from typing import Dict, Type
from .base_strategy import BaseStrategy
from .conventional.sma_strategy import SMACrossoverStrategy
from .conventional.rsi_strategy import RSIStrategy
from .hybrid_v1 import HybridV1Strategy

REGISTRY: Dict[str, Type[BaseStrategy]] = {
    "sma_crossover": SMACrossoverStrategy,
    "rsi": RSIStrategy,
    "hybrid_v1": HybridV1Strategy,
}

def create(name: str, params: dict | None = None) -> BaseStrategy:
    key = name.lower()
    if key not in REGISTRY:
        raise ValueError(f"Unknown strategy: {name}. Available: {list(REGISTRY)}")
    return REGISTRY[key](params=params)
