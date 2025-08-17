import streamlit as st
from ui.services_ext.wf_hpo_runner_ext import list_strategies, run_wf_batch

st.set_page_config(layout="wide", page_title="⚖️ Strateji Karşılaştırma", page_icon="⚖️")
st.title("⚖️ Strateji Karşılaştırma")

strategies = list_strategies()
selected = st.multiselect("Seçim", strategies, default=strategies[:5] if strategies else [])
c1,c2 = st.columns(2)
wf_splits = c1.number_input("WF Splits", 2, 10, 5)
wf_test   = c2.number_input("Test Days", 21, 252, 63)
if st.button("Çalıştır", type="primary"):
    table = run_wf_batch(selected, wf_splits=wf_splits, wf_test=wf_test)
    if table is None or table.empty: st.warning("Sonuç yok.")
    else:
        st.dataframe(table.style.highlight_max(axis=0), use_container_width=True)
        st.download_button("CSV indir", data=table.to_csv().encode("utf-8"), file_name="wf_compare.csv", mime="text/csv")
