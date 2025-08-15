from typing import Dict, Type, List
from .strategies import (
    BaseStrategy,
    MovingAverageCrossover,
    AIUnifiedStrategy,
    HybridEnsembleStrategy,
)

ALL_STRATEGIES: Dict[str, Type[BaseStrategy]] = {
    "ma_crossover": MovingAverageCrossover,
    "ai_unified": AIUnifiedStrategy,
    "hybrid_ensemble": HybridEnsembleStrategy,
}

FAMILIES = {
    "conventional": ["ma_crossover"],
    "ai": ["ai_unified"],
    "hybrid": ["hybrid_ensemble"],
}

def list_strategies() -> List[str]:
    return sorted(ALL_STRATEGIES.keys())