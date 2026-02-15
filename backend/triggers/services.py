from integrations.registry import INTEGRATION_REGISTRY
import traceback
from datetime import datetime, timezone

from django.utils import timezone
from django.db import IntegrityError, transaction
from automations.engine import process_events
from automations.models import Trigger, Automation, EventRecord


class PollingTriggerExecutor:
    def run(self, *, service, trigger_key, trigger_instance, connection, payload=None, mode="test", since_cursor, limit):
        service.bind_trigger_instance(trigger_instance)
        trigger = service.TRIGGERS[trigger_key]
        client = service.get_client(connection)
        since = None
        if mode == "live":
            since = trigger_instance.last_run_at

        raw_items = getattr(service, trigger["fetch"])(
            client=client,
            since_cursor=since,
            limit=limit
        )

        events = [
            getattr(service, trigger["normalize"])(item)
            for item in raw_items
        ]

        if mode == "live" and events:
            trigger_instance.last_run_at = max(
                e.occurred_at for e in events
            )
            trigger_instance.save(update_fields=["last_run_at"])

        return events
    

class WebhookTriggerExecutor:
    def run(self, *, service, trigger_key, connection=None, trigger_instance=None, payload=None, mode="live", since_cursor=None, limit=None):
        trigger = service.TRIGGERS[trigger_key]

        if mode == "test":
            sample = getattr(service, trigger["sample_event"])()
            return [sample]

        event = getattr(service, trigger["normalize"])(payload)
        return [event]

def serialize_event(event):
    return {
        "id": event.event_id,
        "integration": event.integration,
        "trigger": event.trigger,
        "source_id": event.source_id,
        "occurred_at": event.occurred_at.isoformat(),
        "data": event.data,
    }

def resolve_trigger_executor(trigger_definition):
    if trigger_definition.get("type") == "poll":
        return PollingTriggerExecutor()

    if trigger_definition.get("type") == "webhook":
        return WebhookTriggerExecutor()

    raise ValueError("Unknown trigger type")

def run_trigger_test(*, service, trigger_key, trigger_instance, connection):
    trigger_definition = service.TRIGGERS[trigger_key]

    if not trigger_definition.get("is_testable", False):
        return {
            "success": False,
            "message": "This trigger cannot be tested",
            "sample_event": None,
            "events": [],
        }

    executor = resolve_trigger_executor(trigger_definition)

    try:
        events = executor.run(
            service=service,
            trigger_key=trigger_key,
            connection=connection,
            trigger_instance=trigger_instance,
            mode="test",
            # TODO: Use appropriate cursor
            since_cursor=None,
            limit=10
        )
    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "message": str(e),
            "sample_event": None,
            "events": [],
        }

    if not events:
        return {
            "integration": trigger_instance.integration.id,
            "trigger": trigger_key,
            "success": True,
            "occurred_at": timezone.now(),
            "message": "No events found yet",
            "sample_event": None,
            "events": [],
        }
    
    # TODO: Add event condition matching logic

    serialized_events = [serialize_event(event) for event in events]

    return {
        "integration": trigger_instance.integration.id,
        "trigger": trigger_key,
        "success": True,
        "occurred_at": timezone.now(),
        "message": "Trigger tested successfully",
        "sample_event": serialized_events[0],
        "events": serialized_events,
    }

def event_matches_trigger(event, trigger_instance):
    config = trigger_instance.config or {}

    for field, expected in config.items():
        actual = event.payload.get(field)

        if actual is None:
            print(f"Actual is NONE for {field}")
            return False

        if isinstance(expected, str):
            if expected.lower() not in str(actual).lower():
                print(f"{expected} is not {actual}. ID: {event.event_id}")
                return False
            else:
                print("String field matches!!")

        elif isinstance(expected, bool):
            if actual is not expected:
                return False

        else:
            if actual != expected:
                print(f"{actual} != {expected}")
                return False

    print("MATCH FOUND")

    return True

def run_trigger_live(trigger_instance):
    print("This is RUN TRIGGER LIVE")
    print("This is the trigger instance ---> ", trigger_instance)
    # NOTE: Trigger should be configured with necessary question. This means I should probably enforce connection existence before activating trigger
    service = INTEGRATION_REGISTRY[trigger_instance.integration.id](trigger_instance.connection)
    trigger_definition = service.TRIGGERS[trigger_instance.trigger_key]
    executor = resolve_trigger_executor(trigger_definition)

    events = executor.run(
        service=service,
        trigger_key=trigger_instance.trigger_key,
        connection=trigger_instance.connection,
        trigger_instance=trigger_instance,
        mode="live",
        since_cursor=trigger_instance.last_run_at,
        limit=50
    )
    print("EVENTS FAPPED. ABOUT TO PROCESS EVENTS!!")
    process_events(events)


def persist_event(raw_event):
    try:
        with transaction.atomic():
            return EventRecord.objects.create(
                event_id=raw_event.event_id,
                external_id=raw_event.source_id,
                integration=raw_event.integration,
                trigger=raw_event.trigger,
                payload=raw_event.data,
                occurred_at=raw_event.occurred_at,
            )
    except IntegrityError:
        return EventRecord.objects.get(
            integration=raw_event.integration,
            external_id=raw_event.source_id
        )
