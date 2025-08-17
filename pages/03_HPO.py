import streamlit as st
from ui.services_ext.wf_hpo_runner_ext import list_strategies, run_hpo

st.set_page_config(layout="wide", page_title="⚙️ Optimizasyon (HPO)", page_icon="⚙️")
st.title("⚙️ Optimizasyon (HPO)")

strategies = list_strategies()
key = st.selectbox("Strateji", strategies)
trials = st.number_input("Trials", 10, 500, 50)
metric = st.selectbox("Metric", ["sharpe","win_rate"], index=0)
if st.button("Başlat", type="primary"):
    res = run_hpo(key, n_trials=int(trials), metric=metric)
    st.json(res)
