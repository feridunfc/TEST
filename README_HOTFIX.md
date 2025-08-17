
# Hotfix 2.9.13 — EventBus & Event System

This hotfix delivers a production-grade EventBus with:
- sync/async handlers, priorities, filters, once
- sticky events (replay last), pre/post middlewares
- bounded queue + drop policies, DLQ
- request/response pattern
- dynamic worker scaling
- optional Pydantic schema validation
- optional OpenTelemetry tracing hooks
- metrics (published/processed/errors/latency_ms_avg)

## Install
```bash
pip install -e .
```

## Imports
```python
from core.event_bus import event_bus, EventBus, BaseEvent
from core.events import DataReadyEvent, RiskViolationDetected, BacktestCompleted
```
