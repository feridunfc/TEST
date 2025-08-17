import streamlit as st, pandas as pd
import plotly.express as px

# Simple registry shim; replace with your internal registry
class StrategyRegistry:
    _REG = {"AIStrategy": "src.strategies.ai_strategy.AIStrategy"}
    @classmethod
    def list_available(cls):
        return list(cls._REG.keys())
    @classmethod
    def get(cls, name: str):
        # naive dynamic import
        mod, clsname = cls._REG[name].rsplit(".", 1)
        import importlib
        return getattr(importlib.import_module(mod), clsname)

from ..services.runners import run_walk_forward

def render():
    st.title("Strategy Comparison")
    options = StrategyRegistry.list_available()
    selected = st.multiselect("Select Strategies", options=options, key="ns_compare_strategies")
    if len(selected) >= 2:
        rows = []
        for name in selected:
            strat_cls = StrategyRegistry.get(name)
            strat = strat_cls()
            wf = run_walk_forward(strategy=strat)
            agg = wf.aggregate()
            rows.append({"strategy": name, **agg})
        df = pd.DataFrame(rows).set_index("strategy")
        st.dataframe(df.style.highlight_max(axis=0))
        fig = px.bar(df, barmode="group", title="Strategy Comparison")
        st.plotly_chart(fig, use_container_width=True)
