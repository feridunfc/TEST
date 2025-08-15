# --- path bootstrap: src'yi import edilebilir yap ---
import os, sys
ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(os.path.join(ROOT, "..", "src"))
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import streamlit as st
from st_tabs import (
    show_beginner_tab,
    show_advanced_tab,   # Advanced (eski “run”)
    show_live_stub_tab,
    show_report_tab,
)

st.set_page_config(
    page_title="AlgoSuite v2.3",
    layout="wide",
    initial_sidebar_state="expanded",
)

# basit state saklama
if "state" not in st.session_state:
    st.session_state["state"] = {}

st.sidebar.title("AlgoSuite v2.3")
mode = st.sidebar.radio(
    "Mode",
    options=["Beginner", "Advanced", "Live (stub)", "Reports"],
    index=0,
)

st.title("AlgoSuite v2.3")

if mode == "Beginner":
    show_beginner_tab(st.session_state["state"])
elif mode == "Advanced":
    show_advanced_tab(st.session_state["state"])
elif mode == "Live (stub)":
    show_live_stub_tab(st.session_state["state"])
else:
    show_report_tab(st.session_state["state"])
