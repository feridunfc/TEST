import streamlit as st, json
from pathlib import Path
import pandas as pd

st.set_page_config(layout="wide", page_title="📜 Geçmiş Sonuçlar", page_icon="📜")
st.title("📜 Geçmiş Sonuçlar")

rows = []
results_dir = Path("results")
if results_dir.exists():
    for p in sorted(results_dir.glob("*/report.json"), key=lambda x: x.stat().st_mtime, reverse=True):
        try:
            d = json.loads(p.read_text())
            rows.append({
                "run_id": p.parent.name,
                "strategy": d.get("strategy","?"),
                "date": d.get("date",""),
                "sharpe": d.get("metrics",{}).get("sharpe",0.0),
                "max_dd": d.get("metrics",{}).get("max_dd",0.0),
                "win_rate": d.get("metrics",{}).get("win_rate",0.0),
            })
        except Exception: pass
df = pd.DataFrame(rows)
if df.empty: st.info("Henüz kayıt yok.")
else:
    q = st.text_input("Strateji ara", "")
    if q: df = df[df["strategy"].str.contains(q, case=False, na=False)]
    st.dataframe(df, use_container_width=True, height=420)
