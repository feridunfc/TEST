from __future__ import annotations
from collections import defaultdict
from threading import RLock
from typing import Callable, Dict, List, Type

class EventBus:
    def __init__(self):
        self._subs: Dict[Type, List[Callable]] = defaultdict(list)
        self._lock = RLock()

    def subscribe(self, event_type: Type, callback: Callable):
        with self._lock:
            self._subs[event_type].append(callback)

    def publish(self, event):
        with self._lock:
            for cb in list(self._subs.get(type(event), [])):
                cb(event)

event_bus = EventBus()
