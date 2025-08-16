
from collections import defaultdict
import threading

class EventBus:
    def __init__(self):
        self._subs = defaultdict(list)
        self._lock = threading.Lock()

    def subscribe(self, event_type, callback):
        with self._lock:
            self._subs[event_type].append(callback)

    def publish(self, event):
        for cb in list(self._subs.get(type(event), [])):
            cb(event)

event_bus = EventBus()
