from typing import Any, Dict
from django.conf import settings
from .base import BaseIntegrationService, GoogleBaseService
from integrations.registry import register_integration

import requests
import json
import urllib.parse


@register_integration
class GoogleFormsService(GoogleBaseService):
    id = "google_forms"
    name = "Google Forms"
    description = "Connect to Google Forms to receive responses."
    oauth_enabled = True
    webhook_supported = True

    TRIGGERS = {
        "new_response": {
            "name": "New Response",
            "description": "Triggered when a new response on a form is received",
            "type": "webhook",
            "config_schema": {
                "form_id": {
                    "type": "string",
                    "label": "Form ID",
                    "required": True,
                    "help_text": "The ID of the Google Form to watch."
                }
            }
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
    
    def connect(self, config, secrets) -> Dict[str, Any]:
         print("I AM CONNECTING!!!!")
         return self.exchange_code(secrets["authorization_code"])