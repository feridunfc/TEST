# --- path bootstrap ---
import os, sys
ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(os.path.join(ROOT, "..", "src"))
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import time
from datetime import date, timedelta

import numpy as np
import pandas as pd
import streamlit as st

# orchestrator import: sembol/tarih parametreleri opsiyonel, yoksa fallback
from pipeline.orchestrator import run_pipeline
from core.strategies import list_strategies
try:
    from core.strategies.ai_models import list_models
except Exception:
    def list_models():
        return ["random_forest"]  # garanti fallback

# ---------- ortak yardımcılar ----------

def _run_with_fallback(strategy_name, params, symbol=None, start=None, end=None, wf_n_splits=None):
    """orchestrator eski imza ise TypeError yakala ve minimum argümanlarla tekrar dene"""
    kw = {"strategy_name": strategy_name, "params": params}
    if symbol is not None: kw["symbol"] = symbol
    if start is not None:  kw["start"]  = str(start)
    if end is not None:    kw["end"]    = str(end)
    if wf_n_splits is not None: kw["wf_n_splits"] = wf_n_splits
    try:
        return run_pipeline(**kw)
    except TypeError:
        return run_pipeline(strategy_name=strategy_name, params=params)

def _plot_series(df, sig=None, title="Price"):
    import altair as alt
    base = alt.Chart(df.reset_index()).encode(x="Date:T")
    price = base.mark_line().encode(y="close:Q", tooltip=["Date:T", "close:Q"]).properties(height=300)
    chart = price
    if sig is not None and "signal" in sig:
        long_pts = base.transform_filter("datum.signal == 1").mark_point(size=50).encode(y="close:Q", color=alt.value("green"))
        flat_pts = base.transform_filter("datum.signal == 0").mark_point(size=50).encode(y="close:Q", color=alt.value("gray"))
        chart = (price + long_pts + flat_pts)
    st.altair_chart(chart.properties(title=title), use_container_width=True)

def _show_metrics(stats: dict):
    if not stats:
        return
    m = pd.DataFrame([stats]).T
    m.columns = ["value"]
    st.dataframe(m, use_container_width=True)

# ---------- Beginner ----------

def show_beginner_tab(state: dict):
    st.subheader("Beginner (Guided)")

    colL, colR = st.columns([1, 1])
    with colL:
        ticker = st.text_input("Ticker", value="SPY")
        rng = st.date_input(
            "Date range",
            value=(date.today() - timedelta(days=365*2), date.today()),
        )
        if isinstance(rng, tuple) and len(rng) == 2:
            start_dt, end_dt = rng
        else:
            start_dt, end_dt = date.today() - timedelta(days=365*2), date.today()

        preset = st.selectbox(
            "Preset",
            ["Trend Following (MA 20/50)", "AI (RandomForest)", "Hybrid (MA+AI)"],
        )

    with colR:
        strategies = list_strategies()
        st.caption(f"Available strategies: {', '.join(strategies)}")
        models = list_models()
        st.caption(f"AI models: {', '.join(models)}")

    # preset paramları
    if preset.startswith("Trend"):
        strategy = "ma_crossover" if "ma_crossover" in strategies else strategies[0]
        params = {"ma_fast": 20, "ma_slow": 50}
    elif preset.startswith("AI"):
        strategy = "ai_unified" if "ai_unified" in strategies else strategies[0]
        params = {"model_type": models[0] if models else "random_forest", "train_ratio": 0.7, "threshold": 0.5}
    else:
        strategy = "hybrid_ensemble" if "hybrid_ensemble" in strategies else strategies[0]
        params = {"ma_fast": 20, "ma_slow": 50, "model_type": models[0] if models else "random_forest", "train_ratio": 0.7, "threshold": 0.5}

    run_btn = st.button("Run Backtest")
    if run_btn:
        with st.spinner("Running..."):
            df, info = _run_with_fallback(strategy, params, symbol=ticker, start=start_dt, end=end_dt)
        state["last_df"] = df
        state["last_info"] = info

        st.success("Done.")
        _plot_series(df, info.get("signals_df") if info else None, title=f"{ticker} - Price & Signals")
        if info and "equity_curve" in info:
            ec = pd.Series(info["equity_curve"], index=df.index, name="equity").to_frame()
            _plot_series(ec.rename(columns={"equity": "close"}), title="Equity Curve")
        _show_metrics(info.get("stats", {}))

# ---------- Advanced (eski “run”) ----------

def show_advanced_tab(state: dict):
    st.subheader("Advanced")

    strategies = list_strategies()
    strategy = st.sidebar.selectbox("Strategy", strategies, index=0 if strategies else None)

    params = {}
    if strategy == "ma_crossover":
        ma_fast = st.sidebar.slider("MA Fast", 5, 200, 20, step=1)
        ma_slow = st.sidebar.slider("MA Slow", 10, 250, 50, step=1)
        if ma_slow <= ma_fast:
            st.sidebar.warning("MA Slow > MA Fast olmalı")
        params = {"ma_fast": ma_fast, "ma_slow": ma_slow}

    elif strategy == "ai_unified":
        models = list_models()
        model = st.sidebar.selectbox("AI Model", models, index=0 if models else None)
        tr = st.sidebar.slider("Train ratio", 0.5, 0.95, 0.7, step=0.01)
        th = st.sidebar.slider("Threshold", 0.1, 0.9, 0.5, step=0.05)
        params = {"model_type": model, "train_ratio": float(tr), "threshold": float(th)}

    elif strategy == "hybrid_ensemble":
        ma_fast = st.sidebar.slider("MA Fast", 5, 200, 20, step=1)
        ma_slow = st.sidebar.slider("MA Slow", 10, 250, 50, step=1)
        models = list_models()
        model = st.sidebar.selectbox("AI Model", models, index=0 if models else None)
        tr = st.sidebar.slider("Train ratio", 0.5, 0.95, 0.7, step=0.01)
        th = st.sidebar.slider("Threshold", 0.1, 0.9, 0.5, step=0.05)
        params = {"ma_fast": ma_fast, "ma_slow": ma_slow, "model_type": model, "train_ratio": float(tr), "threshold": float(th)}

    # veri aralığı ve walk-forward opsiyonları
    with st.sidebar.expander("Data & Walk-forward"):
        ticker = st.text_input("Ticker", value="SPY")
        start_dt = st.date_input("Start", value=date.today() - timedelta(days=365*3))
        end_dt = st.date_input("End", value=date.today())
        wf = st.number_input("Walk-forward splits (0=off)", min_value=0, max_value=10, value=0, step=1)

    run_btn = st.button("Run Backtest")
    if run_btn:
        with st.spinner("Running..."):
            df, info = _run_with_fallback(strategy, params, symbol=ticker, start=start_dt, end=end_dt, wf_n_splits=(wf or None))
        state["last_df"] = df
        state["last_info"] = info

        st.success("Done.")
        _plot_series(df, info.get("signals_df") if info else None, title=f"{ticker} - Price & Signals")
        if info and "equity_curve" in info:
            ec = pd.Series(info["equity_curve"], index=df.index, name="equity").to_frame()
            _plot_series(ec.rename(columns={"equity": "close"}), title="Equity Curve")
        _show_metrics(info.get("stats", {}))

# ---------- Live (stub) ----------

def show_live_stub_tab(state: dict):
    st.subheader("Live Trading (Stub)")
    st.info("Bu ekran canlı akışın **mock** versiyonudur. Gerçek emir/bağlantı yok.")

    col1, col2 = st.columns(2)
    with col1:
        ticker = st.text_input("Ticker", value="SPY")
        ticks = st.number_input("Simulate N ticks", min_value=10, max_value=500, value=60, step=10)
    with col2:
        mu = st.number_input("Drift (bp/tick)", value=0.0)
        vol = st.number_input("Vol (bp/tick)", value=10.0)

    holder = st.empty()
    start_price = 500.0
    if st.button("Start Simulation"):
        prices = [start_price]
        for i in range(int(ticks)):
            rnd = np.random.randn() * vol + mu
            prices.append(prices[-1] * (1 + rnd / 10000.0))
            df = pd.DataFrame({"price": prices}, index=pd.RangeIndex(len(prices)))
            holder.line_chart(df)
            time.sleep(0.02)

        st.success("Simulation finished.")
        st.caption("Not: Bu ekran yalnızca arayüz/sinyal akışı denemeleri içindir.")

# ---------- Reports ----------

def show_report_tab(state: dict):
    st.subheader("Reports")
    info = state.get("last_info")
    df = state.get("last_df")
    if not info or df is None:
        st.info("Önce Beginner/Advanced sekmesinde bir backtest çalıştırın.")
        return
    _show_metrics(info.get("stats", {}))
    if "signals_df" in info:
        st.write("Signals (tail):")
        st.dataframe(info["signals_df"].tail(20), use_container_width=True)
