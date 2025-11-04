# integrations/registry.py
from typing import Dict
from integrations.services.google_forms import GoogleFormsService, GoogleFormsServicee
from integrations.services.gmail import GmailService

INTEGRATION_REGISTRY: Dict[str, type] = {
    GoogleFormsServicee.id: GoogleFormsServicee,
    GmailService.id: GmailService
}


def get_integration_service(integration_id, connection=None):
    """
    Return the service class for the given integration ID.
    """
    service_cls = INTEGRATION_REGISTRY.get(integration_id)
    if not service_cls:
        raise ValueError(f"Integration '{integration_id}' not found.")
    return service_cls(connection)
