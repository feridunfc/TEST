from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class BaseEvent:
    source: str = "system"
    timestamp: datetime = field(default_factory=datetime.utcnow)
