from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import redirect

from integrations.registry import get_integration_service
from automations.models import Connection, Integration, Workspace

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
