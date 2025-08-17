import streamlit as st

st.set_page_config(layout="wide", page_title="🤖 Otonom Algo-Trade Platformu", page_icon="🤖")
st.title("🤖 Otonom Algo-Trade Platformu")
st.markdown("Profesyonel, modüler ve genişletilebilir algo-trading arayüzü. Soldaki **Pages** menüsünden odaları açın veya aşağıdan hızlı geçiş yapın.")

st.divider()
cols = st.columns(5)
paths = [
    ("pages/00_Home.py", "🏠 Ana Sayfa", "🏠"),
    ("pages/01_Single_Run.py", "🔬 Tekli Çalıştırma", "🔬"),
    ("pages/02_Compare.py", "⚖️ Karşılaştırma", "⚖️"),
    ("pages/03_HPO.py", "⚙️ Optimizasyon (HPO)", "⚙️"),
    ("pages/04_History.py", "📜 Geçmiş Sonuçlar", "📜"),
]
for i, (p, label, icon) in enumerate(paths):
    with cols[i]:
        try:
            st.page_link(p, label=label, icon=icon, use_container_width=True)
        except Exception as e:
            st.caption(f"Navigation not available for {label}: {e}. Yandan 'Pages' menüsünü kullanın.")

st.warning("Eğer butonlar çalışmıyorsa, Streamlit sürümünüzü **>=1.25** olarak güncelleyin ve sayfaların `pages/` klasöründe olduğundan emin olun.")
