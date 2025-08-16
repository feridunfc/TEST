
import threading
from collections import defaultdict

class EventBus:
    """Synchronous, thread-safe pub/sub bus."""
    def __init__(self):
        self._subs = defaultdict(list)
        self._lock = threading.RLock()

    def subscribe(self, event_type, callback):
        with self._lock:
            self._subs[event_type].append(callback)

    def publish(self, event):
        # Call subscribers for exact class and base classes
        callbacks = []
        with self._lock:
            for etype, subs in self._subs.items():
                if isinstance(event, etype):
                    callbacks.extend(subs)
        for cb in callbacks:
            cb(event)

# Singleton
event_bus = EventBus()
