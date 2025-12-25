from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from automations.models import Trigger, Connection



@api_view(['POST'])
def test_trigger(request, pk):
    trigger = Trigger.objects.get(id=pk)
    # result = run_trigger_test()
    pass