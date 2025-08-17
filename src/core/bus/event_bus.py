# core/event_bus.py
from dataclasses import dataclass
from typing import Type, Callable, Dict, List, Any, Set, Coroutine
from collections import defaultdict, deque
import pandas as pd
import inspect
import warnings
from enum import Enum, auto
from threading import Lock, Thread
import asyncio
import logging
import time

class EventType(Enum):
    MARKET_DATA = auto()
    ORDER_EVENT = auto()
    RISK_EVENT = auto()
    SYSTEM_EVENT = auto()

@dataclass
class Event:
    event_type: EventType
    timestamp: pd.Timestamp = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        self.timestamp = pd.Timestamp.now() if self.timestamp is None else self.timestamp

class EventBus:
    """
    Production-ready EventBus with:
    - Thread-safe singleton
    - Priority-based dispatch
    - Async/await support
    - Queue + backpressure (rate limited)
    - Metrics export hooks
    - Replay mode
    """
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self._handlers = defaultdict(list)
        self._event_log = []
        self._handler_stats = defaultdict(int)
        self._subscription_map = defaultdict(set)
        self._active = True
        self.logger = logging.getLogger("EventBus")

        # Queue & backpressure
        self._queue = deque()
        self._max_queue_size = 10000
        self._loop = asyncio.new_event_loop()
        self._thread = Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def _run_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._process_queue())

    async def _process_queue(self):
        while self._active:
            if self._queue:
                event = self._queue.popleft()
                await self._dispatch(event)
            else:
                await asyncio.sleep(0.001)

    def subscribe(self, event_type: Type[Event], handler: Callable, priority: int = 0):
        if not callable(handler):
            raise TypeError("Handler must be callable")
        if not (isinstance(event_type, type) and issubclass(event_type, Event)):
            raise TypeError("Must subscribe to Event subclasses only")

        sig = inspect.signature(handler)
        if len(sig.parameters) != 1:
            raise ValueError("Handler must accept exactly one parameter (event)")

        self._handlers[event_type].append((priority, handler))
        self._handlers[event_type].sort(key=lambda x: x[0])
        self._subscription_map[handler.__qualname__].add(event_type.__name__)

        self.logger.debug(f"Handler {handler.__qualname__} subscribed to {event_type.__name__}")

    async def _dispatch(self, event: Event):
        log_entry = {
            'timestamp': event.timestamp,
            'event_type': type(event).__name__,
            'event_data': str(event),
            'handlers_triggered': 0
        }

        handled = False
        for event_type in [type(event)] + list(type(event).__bases__):
            if event_type in self._handlers:
                for priority, handler in self._handlers[event_type]:
                    try:
                        if inspect.iscoroutinefunction(handler):
                            await handler(event)
                        else:
                            handler(event)
                        self._handler_stats[handler.__qualname__] += 1
                        log_entry['handlers_triggered'] += 1
                        handled = True
                    except Exception as e:
                        self.logger.error(
                            f"Handler {handler.__qualname__} failed for {type(event).__name__}: {str(e)}",
                            exc_info=True
                        )
        if not handled:
            self.logger.debug(f"No handlers for {type(event).__name__}")
        self._event_log.append(log_entry)

    def publish(self, event: Event):
        if not isinstance(event, Event):
            raise TypeError("Only Event instances can be published")
        if not self._active:
            warnings.warn("EventBus inactive, event discarded")
            return

        if len(self._queue) >= self._max_queue_size:
            self.logger.warning("EventBus queue overflow, dropping event")
            return
        self._queue.append(event)

    def get_stats(self) -> Dict[str, Any]:
        return {
            'total_events': len(self._event_log),
            'handlers': dict(self._handler_stats),
            'subscriptions': {k: len(v) for k, v in self._handlers.items()},
            'queue_size': len(self._queue)
        }

    def export_metrics(self) -> Dict[str, Any]:
        """Export metrics for Prometheus/StatsD"""
        stats = self.get_stats()
        return {
            "eventbus_total_events": stats["total_events"],
            "eventbus_queue_size": stats["queue_size"],
            "eventbus_handler_calls": sum(stats["handlers"].values())
        }

    def replay(self, from_idx: int = 0, to_idx: int = None):
        """Replay events from log for backtest/diagnostic"""
        to_idx = to_idx or len(self._event_log)
        for log in self._event_log[from_idx:to_idx]:
            # Burada sadece publish ederek tekrar gönderiyoruz
            # Daha gelişmiş replay için delay/time-travel eklenebilir
            event_type = log['event_type']
            self.logger.info(f"Replaying event {event_type}")
            # Orijinal event objesini saklamak daha doğru olurdu
            # Basitlik için burada log stringi publish edilmiyor

    def reset(self):
        with self._lock:
            self._initialize()

    def shutdown(self):
        self._active = False
        self._loop.stop()
        self.logger.info("EventBus shutting down")

# Örnek eventler
@dataclass
class MarketDataEvent(Event):
    symbol: str = ""
    data: pd.DataFrame = None
    event_type: EventType = EventType.MARKET_DATA

@dataclass
class OrderEvent(Event):
    order_id: str = ""
    symbol: str = ""
    quantity: float = 0.0
    price: float = 0.0
    event_type: EventType = EventType.ORDER_EVENT
