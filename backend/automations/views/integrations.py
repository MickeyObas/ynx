from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.conf import settings
from django.shortcuts import redirect

from integrations.services.google_forms import GoogleFormsService
from automations.models import Integration, Connection, Workspace
from automations.serializers import IntegrationSerializer, IntegrationThinSerializer

import requests
from integrations.registry import get_integration_service


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def connection_test(request, connection_id):
    connection = Connection.objects.get(id=connection_id)

    service = get_integration_service(connection.integration.id, connection)
    print(service.test_connection())
    if service.test_connection():
        return Response({'status': 'Up and running!'})
    
    return Response({'status': 'Error. Connection not working!'}, status=400)


@api_view(['GET'])
def integration_detail(request, integration_id):
    integration = Integration.objects.get(id=integration_id)
    serializer = IntegrationSerializer(integration)
    return Response(serializer.data)


@api_view(['GET'])
def integration_list(request):
    integrations = Integration.objects.all()
    serializer = IntegrationThinSerializer(integrations, many=True)
    return Response(serializer.data)