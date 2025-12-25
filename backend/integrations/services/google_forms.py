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
            "is_testable": True,
            "config_schema": {
                "form_id": {
                    "type": "string",
                    "label": "Form ID",
                    "required": True,
                    "help_text": "The ID of the Google Form to watch."
                }
            },
            "normalize": "normalize_new_response",
            "sample_event": "sample_new_response",
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
    
    # ----- Trigger: New Response -----

    def normalize_new_response(self, payload):
        return {
            "response_id": payload["responseId"],
            "submitted_at": payload["timestamp"],
            "answers": payload["answers"],
        }

    def sample_new_response(self):
        return {
            "response_id": "test_123",
            "submitted_at": "2025-01-01T12:00:00Z",
            "answers": {
                "Email": "test@example.com"
            }
        }