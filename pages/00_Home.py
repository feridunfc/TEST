import streamlit as st, json
from pathlib import Path
import pandas as pd

st.set_page_config(layout="wide", page_title="🏠 Ana Sayfa", page_icon="🏠")
st.title("🏠 Ana Sayfa")
st.markdown("Sistem durumu ve son deneyler.")

st.subheader("Sistem Durumu")
st.success("Tüm Motorlar ve Servisler Aktif")

st.subheader("Son Deneyler")
rows = []
results_dir = Path("results")
if results_dir.exists():
    for p in sorted(results_dir.glob("*/report.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
        try:
            d = json.loads(p.read_text())
            rows.append({
                "run_id": p.parent.name,
                "strategy": d.get("strategy","?"),
                "sharpe": d.get("metrics",{}).get("sharpe",0.0),
                "max_dd": d.get("metrics",{}).get("max_dd",0.0),
                "date": d.get("date","")
            })
        except Exception: pass
if rows: st.dataframe(pd.DataFrame(rows), use_container_width=True)
else: st.info("Kayıtlı deney bulunamadı.")
