import sys, asyncio
from pathlib import Path
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
for p in (str(ROOT), str(SRC)):
    if p not in sys.path:
        sys.path.insert(0, p)
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
try:
    import importlib
    m = importlib.import_module("core.data_normalizer")
    if not hasattr(m, "FinancialDataNormalizer") and hasattr(m, "DataNormalizer"):
        setattr(m, "FinancialDataNormalizer", getattr(m, "DataNormalizer"))
except Exception:
    pass
