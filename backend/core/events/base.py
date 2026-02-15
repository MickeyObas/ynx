from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict

@dataclass
class Event:
    event_id: str
    integration: str
    trigger: str
    source_id: str
    occurred_at: datetime
    data: Dict[str, Any]
    raw: Dict[str, Any]
