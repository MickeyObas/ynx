from .base import Event
import uuid
from datetime import datetime, timezone

def build_event(*, integration, trigger, source_id, data, raw, occurred_at):
    return Event(
        id=f"evt_{uuid.uuid4()}",
        integration=integration,
        trigger=trigger,
        source_id=source_id,
        occurred_at=occurred_at,
        data=data,
        raw=raw,
    )
