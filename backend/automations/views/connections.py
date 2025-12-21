from rest_framework import status, permissions, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, action

from django.utils import timezone

from automations.models import Connection, Integration, Workspace
from automations.serializers import ConnectionSerializer
from integrations.registry import INTEGRATION_REGISTRY, get_integration_service


class ConnectionViewset(viewsets.ModelViewSet):
    serializer_class = ConnectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        workspace_id = self.kwargs.get("workspace_pk")
        queryset = Connection.objects.filter(workspace_id=workspace_id)

        return queryset

    # TODO: Change path to initiate
    @action(detail=False, methods=["post"], url_path="connect")
    def initiate(self, request, **kwargs):
        data = request.data
        workspace_id = self.kwargs.get("workspace_pk")
        data["workspace_id"] = workspace_id
        serializer = ConnectionSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        connection = serializer.save()
        service = get_integration_service(connection.integration.id, connection)
        auth_url = service.get_auth_url(connection.id)
        return Response({
            "connection_id": str(connection.id),
            "auth_url": auth_url
        })
    
    def create(self, request, *args, **kwargs):
        print("Hello WORLD")
        workspace_id = self.kwargs.get("workspace_pk")
        data = request.data.copy()
        data["workspace_id"] = workspace_id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        connection = serializer.save()
        return Response(serializer.data, status=201)

