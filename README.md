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
