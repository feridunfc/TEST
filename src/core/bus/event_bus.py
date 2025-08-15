from __future__ import annotations
from collections import defaultdict
from threading import RLock

class EventBus:
    _subscribers = defaultdict(list)
    _lock = RLock()

    @classmethod
    def subscribe(cls, event_type, callback):
        with cls._lock:
            cls._subscribers[event_type].append(callback)

    @classmethod
    def publish(cls, event):
        with cls._lock:
            callbacks = list(cls._subscribers[type(event)])
        for cb in callbacks:
            try:
                cb(event)
            except Exception as e:
                # In production push to logger
                print(f"EventBus callback error: {e}")

# convenience singleton-like alias
event_bus = EventBus
