from rest_framework import status, permissions, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, action

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

    @action(detail=False, methods=["post"], url_path="connect")
    def connect(self, request, **kwargs):
        data = request.data
        data["workspace_id"] = self.kwargs.get("workspace_pk")
        serializer = ConnectionSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        connection = serializer.save()
        service = get_integration_service(connection.integration.id, connection)

        # Perform integration-specific connect logic
        new_secrets = service.connect(
            config=connection.config,
            secrets=connection.secrets
        )

        if new_secrets:
            connection.secrets = new_secrets
            connection.save(update_fields=["secrets"])

        if not service.test_connection():
            connection.status = Connection.Status.DISABLED
            connection.save(update_fields=["status"])
            return Response(
                {"error": "Connection test failed"},
                status=400
            )

        connection.status = Connection.Status.ACTIVE
        connection.save(update_fields=["status"])

        return Response(ConnectionSerializer(connection).data, status=201)
    
    def create(self, request, *args, **kwargs):
        print("Hello WORLD")
        workspace_id = self.kwargs.get("workspace_pk")
        data = request.data.copy()
        data["workspace_id"] = workspace_id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        connection = serializer.save()
        return Response(serializer.data, status=201)

