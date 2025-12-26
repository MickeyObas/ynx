from integrations.registry import INTEGRATION_REGISTRY
import traceback

from django.utils import timezone

class PollingTriggerExecutor:
    def run(self, *, service, trigger_key, trigger_instance, connection, payload=None, mode="test", limit=5):
        trigger = service.TRIGGERS[trigger_key]
        client = service.get_client(connection)
        since = None
        if mode == "live":
            since = trigger_instance.last_run_at

        raw_items = getattr(service, trigger["fetch"])(
            client=client,
            since=since,
            limit=limit
        )

        filtered = getattr(service, trigger["apply_filters"])(raw_items, trigger_instance.config)

        events = [
            getattr(service, trigger["normalize"])(item)
            for item in filtered
        ]

        if mode == "live" and events:
            trigger_instance.last_run_at = max(
                e["occured_at"] for e in events
            )
            trigger_instance.save(update_fields=["last_run_at"])

        return events
    

class WebhookTriggerExecutor:
    def run(self, *, service, trigger_key, connection=None, trigger_instance=None, payload=None, mode="live", limit=None):
        trigger = service.TRIGGERS[trigger_key]

        if mode == "test":
            sample = getattr(service, trigger["sample_event"])()
            return [sample]

        event = getattr(service, trigger["normalize"])
        return [event]


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
            "raw_events": [],
        }

    executor = resolve_trigger_executor(trigger_definition)

    try:
        events = executor.run(
            service=service,
            trigger_key=trigger_key,
            connection=connection,
            trigger_instance=trigger_instance,
            mode="test",
            limit=200
        )
    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "message": str(e),
            "sample_event": None,
            "raw_events": [],
        }

    if not events:
        return {
            "integration": trigger_instance.integration.id,
            "trigger": trigger_key,
            "success": True,
            "occurred_at": timezone.now(),
            "message": "No events found yet",
            "sample_event": None,
            "raw_events": [],
        }

    return {
        "integration": trigger_instance.integration.id,
        "trigger": trigger_key,
        "success": True,
        "occurred_at": timezone.now(),
        "message": "Trigger tested successfully",
        "sample_event": events[0],
        "raw_events": events,
    }
