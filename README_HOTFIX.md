# v2.5/v2.6 HOTFIX PACKAGE

This package drops in:
- DataNormalizer (strict), golden tests
- Walk-Forward Adapter (leakage-free), metrics
- Enhanced Risk Chain (portfolio constraints + anomaly/sentiment bridge + liquidity)
- Streamlit UI (Single/WF controls, error panel, CSV export), Risk controls, Compare page
- Optuna HPO scaffold
- CI Smoke for DataNormalizer and Backtest Engine

## Quick start
1) Unzip at repo root
2) Ensure deps: pydantic, optuna, scikit-learn, plotly, streamlit, pandas, pyarrow
3) Run tests: `pytest -q tests/test_data_normalizer.py` and `pytest -q tests/smoke/`
4) UI: `python -m ui.main` (ensure your entrypoint uses new panels)

## Notes
- Golden fixtures included under tests/fixtures/
- Replace demo data loader in `ui/services/runners.py` with your pipeline datasource.
