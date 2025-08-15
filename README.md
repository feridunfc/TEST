# Autonom Trading v2.9 Hotfix (Hybrid Event-Driven)

## Kurulum
```bash
python -m venv .venv
# Windows PowerShell:
# .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:PYTHONPATH="src"   # Windows PowerShell
# Linux/Mac:
# export PYTHONPATH=src
streamlit run ui/streamlit_app.py
```

## Notlar
- `src` içinde hiçbir modul Streamlit'e import etmez (UI bağımlılığı yok).
- `orchestrator.py` yfinance verisini normalize eder (OHLCV lowercase).
- Walk-forward ve simple backtest mevcuttur.
- Event-bus çekirdeği eklendi, servisler kademeli geçiş için hazırdır.
