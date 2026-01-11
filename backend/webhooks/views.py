from rest_framework.decorators import api_view

from integrations.registry import INTEGRATION_REGISTRY
from triggers.services import resolve_trigger_executor
from triggers.services import process_events


@api_view(["POST"])
def webhook_view(request, integration_key, trigger_key):
    service = INTEGRATION_REGISTRY[integration_key]
    trigger_definition = service.TRIGGERS[trigger_key]

    executor = resolve_trigger_executor(trigger_definition)

    events = executor.run(
        service=service,
        trigger_key=trigger_key,
        payload=request.data,
        mode="live",
        trigger_instance=None,
        connection=None, 
        limit=None,
        since_cursor=None
    )

    process_events(events)
