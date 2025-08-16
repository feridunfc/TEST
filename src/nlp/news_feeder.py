# src/nlp/news_feeder.py
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

@dataclass
class NewsItem:
    title: str
    content: str
    source: str
    timestamp: datetime
    asset: Optional[str] = None

class NewsFeeder:
    """
    Minimal stub that calls back with dummy news every N seconds.
    Replace with RSS/Twitter integration in production.
    """
    def __init__(self, config: Dict):
        self.config = config
        self._stop_event = threading.Event()

    def start_feeding(self, callback, period_sec: int = 60):
        def loop():
            i = 0
            while not self._stop_event.is_set():
                i += 1
                item = NewsItem(
                    title=f"Dummy headline {i}",
                    content="Market update lorem ipsum...",
                    source="dummy",
                    timestamp=datetime.utcnow(),
                    asset="BTC",
                )
                try:
                    callback(item)
                except Exception:
                    pass
                time.sleep(period_sec)
        t = threading.Thread(target=loop, daemon=True)
        t.start()
        return t

    def stop_feeding(self):
        self._stop_event.set()
