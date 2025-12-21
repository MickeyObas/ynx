from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import redirect
from django.utils import timezone

from integrations.registry import get_integration_service
from automations.models import Connection, Integration, Workspace
from automations.serializers import ConnectionSerializer

import json
import urllib.parse


@api_view(["GET"])
def start_oauth(request, integration_id, workspace_id):
    # service_name = request.query_params.get('service_name')

    service = get_integration_service(integration_id=integration_id)
    if not service:
        return Response({"error": "Integration not found"}, status=404)
    auth_url = service.get_auth_url(workspace_id=str(workspace_id), integration_id=integration_id)
    return redirect(auth_url)


@api_view(["GET"])
def oauth_callback(request, service_name):
    code = request.query_params.get("code")
    state = request.query_params.get('state') # connection ID
    connection = None

    if state:
        try:
            decoded_state = json.loads(urllib.parse.unquote(state))
            connection_id = decoded_state.get("connection_id")
            connection = Connection.objects.get(id=connection_id)
        except Exception as e:
            print(e)
            return Response({"error": "Failed to decode state"})
    
    service = get_integration_service(connection.integration.id, connection)
    new_secrets = service.connect(
        config=connection.config,
        secrets={"authorization_code": code}
    )
    if new_secrets:
        print("Received new secrets!!")
        connection.secrets = new_secrets
        connection.save(update_fields=["secrets"])

    if not service.test_connection():
        connection.status = Connection.Status.DISABLED
        connection.last_tested = timezone.now()
        connection.save(update_fields=["status", "last_tested"])
        return Response(
            {"error": "Connection test failed"},
            status=400
        )
    
    connection.status = Connection.Status.ACTIVE
    connection.last_tested = timezone.now()
    connection.save(update_fields=["status", "last_tested"])

    return Response(ConnectionSerializer(connection).data, status=201)


"""
@api_view(["GET"])
def oauth_callback(request, service_name):
    code = request.query_params.get("code")
    state = request.query_params.get('state')

    integration_id = None
    workspace_id = None

    if state:
        try:
            decoded_state = json.loads(urllib.parse.unquote(state))
            workspace_id = decoded_state.get("workspace_id")
            integration_id = decoded_state.get("integration_id")
        except Exception as e:
            print("Failed to decode state:", e)

    service = get_integration_service(integration_id=integration_id)
    if not service:
        return Response({"error": "Integration not found"}, status=404)
    tokens = service.exchange_code(code)

    integration = Integration.objects.get(id=integration_id)
    workspace = Workspace.objects.get(id=workspace_id)

    Connection.objects.create(
        workspace=workspace,
        integration=integration,
        display_name=f"{integration_id} connection",
        # config={"redirect_uri": service.redirect_uri},
        secrets=tokens,
    )

    return Response({"message": f"{integration_id} connected successfully!"})

"""
