import streamlit as st, pandas as pd
from config.config import load_config
from pipeline.orchestrator import run_pipeline
from core.strategies.registry import list_strategies
from core.models.registry import list_models

def _sidebar():
    cfg = load_config()
    st.sidebar.header("Data")
    cfg.data.symbol = st.sidebar.text_input("Symbol", value=cfg.data.symbol)
    cfg.data.source = st.sidebar.selectbox("Source", ["yfinance","csv","parquet"], index=0)
    cfg.data.start = st.sidebar.text_input("Start", value=cfg.data.start)
    cfg.data.end = st.sidebar.text_input("End", value=cfg.data.end or "")
    cfg.data.interval = st.sidebar.selectbox("Interval", ["1d","1h","1wk"], index=0)
    if cfg.data.source=="csv":
        cfg.data.csv_path = st.sidebar.text_input("CSV Path", value=cfg.data.csv_path or "")
    if cfg.data.source=="parquet":
        cfg.data.parquet_path = st.sidebar.text_input("Parquet Path", value=cfg.data.parquet_path or "")
    st.sidebar.header("Fees")
    cfg.fees.commission = float(st.sidebar.number_input("Commission (decimal)", value=float(cfg.fees.commission), step=0.0001, format="%.4f"))
    cfg.fees.slippage_bps = float(st.sidebar.number_input("Slippage (bps)", value=float(cfg.fees.slippage_bps), step=1.0, format="%.0f"))
    st.sidebar.header("Backtest")
    cfg.bt.walkforward_splits = int(st.sidebar.number_input("Walk-Forward Splits", value=int(cfg.bt.walkforward_splits), step=1))
    cfg.bt.seed = int(st.sidebar.number_input("Seed", value=int(cfg.bt.seed), step=1))
    return cfg

def show_main():
    st.title("Autonom Trading Platform — 2.9.13 Hotfix")
    tabs = st.tabs(["Run", "Compare", "Report"])
    with tabs[0]:
        cfg = _sidebar()
        st.subheader("Strategy")
        strategies = list_strategies()
        strat = st.selectbox("Select Strategy", strategies, index=0 if strategies else -1)
        params = {}
        if strat == "ma_crossover":
            col1, col2 = st.columns(2)
            params["ma_fast"] = int(col1.number_input("MA Fast", value=20, step=1))
            params["ma_slow"] = int(col2.number_input("MA Slow", value=50, step=1))
        elif strat == "ai_unified":
            models = list_models()
            params["model_name"] = st.selectbox("AI Model", models, index=0 if models else -1)
            params["threshold"] = float(st.number_input("Threshold", value=0.5, step=0.05))

        if st.button("Run Backtest", type="primary"):
            try:
                df, info = run_pipeline(strat, params=params, cfg=cfg)
                st.success("Backtest done.")
                st.line_chart(info["equity"])
                st.dataframe(pd.DataFrame([info["stats"]]))
                st.session_state["last_info"] = info
            except Exception as e:
                st.error(str(e))

    with tabs[1]:
        st.subheader("Compare AI models")
        cfg = _sidebar()
        models = list_models()
        selected = st.multiselect("Models", models, default=models[:2] if models else [])
        if st.button("Run Compare"):
            rows = []
            for m in selected:
                try:
                    _, info = run_pipeline("ai_unified", params={"model_name": m, "threshold": 0.5}, cfg=cfg)
                    rows.append({"model": m, **info["stats"]})
                except Exception as e:
                    st.error(f"{m}: {e}")
            if rows:
                st.dataframe(pd.DataFrame(rows).sort_values("sharpe", ascending=False))

    with tabs[2]:
        st.subheader("Report (last run)")
        info = st.session_state.get("last_info")
        if info:
            st.dataframe(pd.DataFrame([info["stats"]]))
            st.line_chart(info["equity"])
        else:
            st.info("Run a backtest first.")
