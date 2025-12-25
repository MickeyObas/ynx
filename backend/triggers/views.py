from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone

from automations.models import Trigger, Connection
from triggers.services import run_trigger_test
from integrations.registry import INTEGRATION_REGISTRY



@api_view(['POST'])
def test_trigger(request, pk):
    trigger = Trigger.objects.get(id=pk)
    service = INTEGRATION_REGISTRY[trigger.integration.id](trigger.connection)
    result = run_trigger_test(
        service=service,
        trigger_key=trigger.trigger_key,
        trigger_instance=trigger,
        connection=trigger.connection,
    )
    trigger.last_tested_at = timezone.now()
    trigger.save()
    if not result.get("success"):
        return Response(result, status=400)
    return Response(result)