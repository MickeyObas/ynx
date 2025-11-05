from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from django.shortcuts import redirect

from integrations.services.google_forms import GoogleFormsService
from ..models import Integration, Connection, Workspace

import requests
from integrations.registry import get_integration_service


@api_view(['GET'])
def connection_test(self, connection_id):
    connection = Connection.objects.get(id=connection_id)
    service = get_integration_service(connection.integration.id, connection)
    print(service.test_connection())
    if service.test_connection():
        return Response({'status': 'Up and running!'})
    return Response({'status': 'Error. Connection not working!'}, status=400)
