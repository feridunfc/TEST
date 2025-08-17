import streamlit as st
def metric_card(title: str, value: str, delta: str = None, help: str = None):
    c = st.container()
    with c:
        st.markdown(f"**{title}**")
        st.metric(label="", value=value, delta=delta, help=help)
    return c
