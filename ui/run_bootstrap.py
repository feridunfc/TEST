import asyncio, sys
from pathlib import Path
import importlib

# 1) Event loop policy for Windows/Py3.12
try:
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
except Exception:
    pass
try:
    asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
    except Exception:
        pass

# 2) Ensure project ROOT is on sys.path so `ui.*` resolves when running `streamlit run ui/run_bootstrap.py`
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

def _load_compare_render():
    # Try normal absolute import
    try:
        from ui.pages._compare_impl import render as compare_render
        return compare_render
    except Exception:
        # Fallback: load from file to avoid packaging issues
        import importlib.util
        p = ROOT / "ui" / "pages" / "_compare_impl.py"
        if not p.exists():
            st.error("Compare implementation not found at ui/pages/_compare_impl.py")
            raise
        spec = importlib.util.spec_from_file_location("compare_impl", str(p))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore
        return getattr(mod, "render")

def main():
    st.set_page_config(layout="wide", page_title="QuantFlow Pro (Bootstrap)", page_icon="📊")
    st.sidebar.success("Bootstrap UI (safe & additive)")
    # Prefer user's full app if available
    try:
        app = importlib.import_module("ui.streamlit_app")
        if hasattr(app, "main"):
            app.main()
            return
    except Exception as e:
        st.info(f"User UI not found / failed: {e}")
    # Fallback to Compare page
    compare_render = _load_compare_render()
    compare_render()

if __name__ == "__main__":
    main()
