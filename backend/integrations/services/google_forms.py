from django.conf import settings
from .base import BaseIntegrationService, GoogleBaseService

import requests
import json
import urllib.parse


class GoogleFormsService(GoogleBaseService):
    id = "google_forms"
    name = "Google Forms"
    description = "Connect to Google Forms to receive responses."
    oauth_enabled = True
    webhook_supported = True

    TRIGGERS = {
        "new_response": {
            "name": "New Response",
            "description": "Triggered when a new response on a form is received"
        }
    }

    ACTIONS = {}

    @classmethod
    def get_scopes(cls) -> list[str]:
        return [
            "https://www.googleapis.com/auth/forms.body.readonly",
            "https://www.googleapis.com/auth/forms.responses.readonly"
        ]
    
    def perform_action(self, action_id, connection, payload):
        return super().perform_action(action_id, connection, payload)

    # def test_connection(self):
    #     headers = {"Authorization": f"Bearer {self.secrets['access_token']}"}
    #     # TODO: Use non-static values for form ids
    #     form_id = "1UXlc3Ndi1ZleBjOGZr2ffH-4j41iXNnTda2H-PXpaDE"
    #     response = requests.get(f"https://forms.googleapis.com/v1/forms/{form_id}", headers=headers)
    #     response.raise_for_status()
    #     return response.json()