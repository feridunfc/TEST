# Non-invasive bootstrap: create event loop policy early, then import user's app.
import asyncio, sys, importlib

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

# Prefer user's original app if present; otherwise fall back to our Compare page.
try:
    app = importlib.import_module("ui.streamlit_app")
    if hasattr(app, "main"):
        import streamlit as st
        st.write("Bootstrap OK → delegating to existing UI...")
        app.main()
    else:
        raise ImportError("ui.streamlit_app has no main()")
except Exception:
    # Fallback to a tiny one-page app that exposes Compare WF/HPO
    import streamlit as st
    from ui.pages._compare_impl import render as compare_render
    st.set_page_config(layout="wide", page_title="QuantFlow Pro (Bootstrap)", page_icon="📊")
    st.sidebar.success("Bootstrap UI (non-invasive)")
    compare_render()
