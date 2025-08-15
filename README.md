<<<<<<< HEAD
# algosuite v2.3 hotfix (minimal)

## Run
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
# source .venv/bin/activate

pip install -r requirements.txt
set PYTHONPATH=src   # Windows PowerShell: $env:PYTHONPATH="src"
streamlit run ui/streamlit_app.py
```

## Notes
- Absolute imports are used to avoid `attempted relative import beyond top-level package`.
- Strategies are registered through `core.strategies.__init__` (ALL_STRATEGIES, FAMILIES).
- AI models registry at `core/strategies/ai_models/__init__.py`.
=======
# e1.8.4 Minimal Sandbox

**Run UI**

```bash
streamlit run ui/streamlit_app.py
```

If you use `yfinance`, intraday for some tickers may fail. Default `synthetic` is reliable.

**Smoke Test (CLI)**

```bash
python -c "import sys, json; sys.path.insert(0,'src'); from pipeline.orchestrator import run_pipeline; cfg={'mode':'backtest','out_dir':'runs/smoke','data':{'source':'synthetic','symbols':['BTC-USD','ETH-USD'],'freq':'30min','seed':42},'fees':{'capital':10000,'fee_bps':5,'slippage_bps':5},'strategy':{'name':'ma_crossover','params':{'ma_fast':10,'ma_slow':30}}}; print(run_pipeline(cfg))"
```

Artifacts are written under `runs/...`.
>>>>>>> 9de8cc4c42b37e5b0d39288e87244dc7e7f49c65
