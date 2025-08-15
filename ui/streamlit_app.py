import os, sys
import streamlit as st

# Best effort to add src to path if PYTHONPATH is missing
ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from st_tabs import show_main  # noqa: E402

st.set_page_config(page_title="Autonom Trading v2.9", layout="wide")
show_main()
