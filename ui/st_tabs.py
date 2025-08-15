import traceback
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
import plotly.express as px

from config.config import load_config, AppConfig
from pipeline.orchestrator import run_pipeline, list_models

# ---------------- Sidebar controls ----------------
def _sidebar_controls() -> AppConfig:
    cfg = load_config()
    st.sidebar.header("Config")
    symbol = st.sidebar.text_input("Symbol", value=cfg.data.symbol)
    interval = st.sidebar.selectbox("Interval", options=["1d","1h","30m","15m"], index=0)
    end_default = datetime.utcnow().date()
    start_default = end_default - timedelta(days=365*3)
    start = st.sidebar.date_input("Start", value=start_default)
    end = st.sidebar.date_input("End", value=end_default)

    commission = st.sidebar.number_input("Commission (fraction)", value=float(cfg.fees.commission), step=float(0.0001), format="%.4f")
    slippage_bps = st.sidebar.number_input("Slippage (bps)", value=float(cfg.fees.slippage_bps), step=float(1))

    vol_target = st.sidebar.number_input("Vol Target (ann.)", value=float(cfg.risk.vol_target), step=float(0.01))
    max_dd = st.sidebar.number_input("Max Drawdown limit", value=float(cfg.risk.max_drawdown), step=float(0.01))

    wf_splits = st.sidebar.number_input("Walkforward splits", value=int(cfg.backtest.walkforward_splits), step=1, min_value=2)

    cfg.data.symbol = symbol
    cfg.data.interval = interval
    cfg.data.start = start.strftime("%Y-%m-%d")
    cfg.data.end = end.strftime("%Y-%m-%d")
    cfg.fees.commission = float(commission)
    cfg.fees.slippage_bps = float(slippage_bps)
    cfg.risk.vol_target = float(vol_target)
    cfg.risk.max_drawdown = float(max_dd)
    cfg.backtest.walkforward_splits = int(wf_splits)
    return cfg

# --------------- Tabs -----------------------------
def show_main():
    st.title("Autonom Trading v2.9 – Hybrid ED Backtester")
    cfg = _sidebar_controls()

    tabs = st.tabs(["Data", "Train", "Run", "Compare", "Report"])

    with tabs[0]:
        st.subheader("Load & Inspect Data")
        st.write("Veri kaynağı: yfinance. Sembol ve tarihleri soldan güncelleyin.")
        try:
            # use run_pipeline with tiny simple strategy just to fetch/feature df quickly
            df, info = run_pipeline("ma_crossover", params={"ma_fast": 20, "ma_slow": 50}, cfg=cfg, mode="simple")
            st.write(df.tail())
            fig = px.line(df.reset_index(), x=df.index.name or "index", y="close", title=f"{cfg.data.symbol} Close")
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Data load error: {e}")
            st.code(traceback.format_exc())

    with tabs[1]:
        st.subheader("Train (AI Unified)")
        models = list_models()
        selected_models = st.multiselect("AI Models", options=models, default=([m for m in models if m in ['random_forest','lightgbm','xgboost']][:2]))
        train_ratio = st.slider("Train Ratio", min_value=0.5, max_value=0.9, value=0.7, step=0.05)
        threshold = st.slider("Buy Threshold", min_value=0.4, max_value=0.6, value=0.5, step=0.01)

        if st.button("Run Walkforward AI"):
            results = []
            for m in selected_models:
                try:
                    params = {"model_type": m, "train_ratio": float(train_ratio), "threshold": float(threshold)}
                    _, info = run_pipeline("ai_unified", params=params, cfg=cfg, mode="walkforward")
                    stats = info["stats"]
                    stats["model"] = m
                    results.append(stats)
                except Exception as e:
                    st.error(f"{m} failed: {e}")
                    st.code(traceback.format_exc())
            if results:
                dfres = pd.DataFrame(results).set_index("model")
                st.dataframe(dfres.style.format("{:.4f}"))
                st.bar_chart(dfres["sharpe"])

    with tabs[2]:
        st.subheader("Run (Conventional)")
        ma_fast = st.number_input("MA Fast", value=20, step=1)
        ma_slow = st.number_input("MA Slow", value=50, step=1)
        mode = st.selectbox("Mode", options=["simple", "walkforward"], index=0)
        if st.button("Run Backtest"):
            try:
                df, info = run_pipeline("ma_crossover", params={"ma_fast": int(ma_fast), "ma_slow": int(ma_slow)}, cfg=cfg, mode=mode)
                st.write(info["stats"])
                eq = info["equity"]
                fig = px.line(eq.reset_index(), x=eq.index.name or "index", y=eq.name or 0, title="Equity Curve")
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Backtest error: {e}")
                st.code(traceback.format_exc())

    with tabs[3]:
        st.subheader("Compare")
        st.write("Aynı veri penceresinde birden fazla stratejiyi karşılaştır.")
        compare_choices = st.multiselect("Strategies", options=["ma_crossover","ai_unified"], default=["ma_crossover","ai_unified"])
        run_mode = st.selectbox("Mode", options=["simple","walkforward"], index=1)
        if st.button("Run Compare"):
            rows = []
            for sname in compare_choices:
                try:
                    params = {"ma_fast":20,"ma_slow":50} if sname=="ma_crossover" else {"model_type":"random_forest","train_ratio":0.7,"threshold":0.5}
                    _, info = run_pipeline(sname, params=params, cfg=cfg, mode=run_mode)
                    r = dict(info["stats"])
                    r["strategy"] = sname
                    rows.append(r)
                except Exception as e:
                    st.error(f"{sname} failed: {e}")
                    st.code(traceback.format_exc())
            if rows:
                dfcmp = pd.DataFrame(rows).set_index("strategy")
                st.dataframe(dfcmp.style.format("{:.4f}"))
                st.bar_chart(dfcmp["sharpe"])

    with tabs[4]:
        st.subheader("Report & Next Steps")
        st.markdown("""
        **Metrikler:** Sharpe, Sortino, Calmar, MaxDD, Annualized Return, Vol, WinRate
        **Walk-Forward:** TimeSeriesSplit ile OOS test.
        **Risk:** Vol Target ve MaxDD stop.
        **Event-Driven:** EventBus çekirdeği ve Feature/Signal/Risk servisleri eklendi.
        """)
