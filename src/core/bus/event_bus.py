
from collections import defaultdict
from threading import RLock
from typing import Callable, Dict, List, Type

# Simple, thread-safe synchronous event bus
class EventBus:
    def __init__(self) -> None:
        self._subs: Dict[type, List[Callable]] = defaultdict(list)
        self._lock = RLock()

    def subscribe(self, event_type: Type, callback: Callable) -> None:
        with self._lock:
            self._subs[event_type].append(callback)

    def publish(self, event) -> None:
        # Synchronous dispatching
        callbacks = []
        with self._lock:
            callbacks = list(self._subs.get(type(event), []))
        for cb in callbacks:
            cb(event)

# Global singleton
event_bus = EventBus()
