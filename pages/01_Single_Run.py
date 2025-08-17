import streamlit as st, importlib
from ui.components.metric_card import metric_card

st.set_page_config(layout="wide", page_title="🔬 Tekli Çalıştırma", page_icon="🔬")
st.title("🔬 Tekli Çalıştırma")

with st.sidebar:
    st.header("Veri & Risk")
    asset = st.selectbox("Varlık", ["AAPL","MSFT","BTC-USD"], index=0)
    interval = st.selectbox("Zaman Aralığı", ["1d","1h","15m"], index=0)
    commission = st.slider("Komisyon (bps)", 0, 50, 5)
    slippage = st.slider("Slippage (bps)", 0, 50, 5)

def list_strategies():
    try:
        mod = importlib.import_module("src.strategies.registry")
        return list(getattr(mod, "STRATEGY_REGISTRY", {}).keys())
    except Exception:
        return ["rb_ma_crossover"]
key = st.selectbox("Strateji", list_strategies())

if st.button("Backtest'i Çalıştır", type="primary"):
    try:
        from ui.services_ext.wf_hpo_runner_ext import run_wf_batch
        res = run_wf_batch([key], wf_splits=3, wf_test=30)
        sharpe = float(res.loc[key,"sharpe"]) if not res.empty else 0.0
        maxdd = float(res.loc[key,"max_dd"]) if not res.empty else 0.0
        winr  = float(res.loc[key,"win_rate"]) if not res.empty else 0.0
        metric_card("Sharpe", f"{sharpe:.2f}")
        metric_card("Max DD", f"{maxdd:.1%}")
        metric_card("Win Rate", f"{winr:.1%}")
    except Exception as e:
        st.error(f"Backtest hatası: {e}")
