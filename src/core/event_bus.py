from collections import defaultdict
from typing import Type, Callable, Any
import pandas as pd
import warnings

class Event:
    pass

class EventBus:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._handlers = defaultdict(list)
            cls._instance._event_log = []
        return cls._instance

    def subscribe(self, event_type: Type[Event], handler: Callable[[Any], None]):
        if not isinstance(event_type, type):
            raise TypeError("event_type must be a class")
        self._handlers[event_type].append(handler)

    def publish(self, event: Event):
        if not isinstance(event, Event):
            raise TypeError("Can only publish Event instances")
        self._event_log.append({'timestamp': pd.Timestamp.now(), 'event_type': type(event).__name__, 'event': str(event)})
        # dispatch to exact type and subclasses of subscribed types
        for etype, handlers in list(self._handlers.items()):
            try:
                if isinstance(event, etype):
                    for h in list(handlers):
                        try:
                            h(event)
                        except Exception as e:
                            warnings.warn(f"Handler failed for {etype}: {e}")
            except Exception:
                continue
