from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from automations.models import Connection, Integration
from automations.serializers import ConnectionSerializer, ConnectionDisplaySerializer
from integrations.registry import get_integration_service


class ConnectionInitiate(APIView):
    """POST /workspaces/<workspace_pk>/connections/initiate/"""
    permission_classes = [IsAuthenticated]

    def post(self, request, workspace_pk):
        data = request.data.copy()
        data["workspace_id"] = workspace_pk

        # Return existing connection if one already exists for this integration
        existing = Connection.objects.filter(
            workspace_id=workspace_pk,
            integration_id=data.get("integration_id"),
        ).first()
        if existing:
            return Response({"connection_id": str(existing.id)})

        serializer = ConnectionSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        connection = serializer.save()

        # Uncomment when auth flow is ready:
        # service = get_integration_service(connection.integration.id, connection)
        # auth_url = service.get_auth_url(connection.id)

        return Response({
            "connection_id": str(connection.id),
            # "auth_url": auth_url,
        }, status=status.HTTP_201_CREATED)