from __future__ import annotations
import threading
from collections import defaultdict
from typing import Callable, Dict, List, Type, Any

class EventBus:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init_internal()
            return cls._instance

    def _init_internal(self):
        self.subscribers: Dict[Type, List[Callable]] = defaultdict(list)
        self.bus_lock = threading.Lock()

    def subscribe(self, event_type: Type, callback: Callable[[Any], None]) -> None:
        with self.bus_lock:
            self.subscribers[event_type].append(callback)

    def publish(self, event: Any) -> None:
        # Synchronous publish; can be swapped for async executor in future
        callbacks = []
        with self.bus_lock:
            callbacks = list(self.subscribers.get(type(event), []))
        for cb in callbacks:
            cb(event)

event_bus = EventBus()
