# Auto-loaded by Python if present on sys.path.
# Purpose: make repo root and 'src' importable, set event loop policy,
# and provide backward-compatible aliases (e.g., FinancialDataNormalizer).
import sys, asyncio
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
for p in [str(ROOT), str(SRC)]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Windows / Py3.12 event loop fix for Streamlit ScriptRunner threads
try:
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
except Exception:
    pass
try:
    asyncio.get_running_loop()
except RuntimeError:
    try:
        asyncio.set_event_loop(asyncio.new_event_loop())
    except Exception:
        pass

# Compatibility aliases without modifying frozen modules:
# If FinancialDataNormalizer is missing, alias it to DataNormalizer at import time.
try:
    import importlib
    m = importlib.import_module("core.data_normalizer")
    if not hasattr(m, "FinancialDataNormalizer") and hasattr(m, "DataNormalizer"):
        setattr(m, "FinancialDataNormalizer", getattr(m, "DataNormalizer"))
    # Optional common names
    for name in ("NormalizationConfig","NormalizationMethod","NaNPolicy"):
        if not hasattr(m, name):
            # quietly ignore if not present
            pass
except Exception:
    # Don't fail import; UI may still run.
    pass
