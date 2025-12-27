from typing import Any, Dict
from datetime import datetime
from django.conf import settings
from django.utils import timezone

from .base import BaseIntegrationService, GoogleBaseService
from integrations.registry import register_integration
from core.events.factory import build_event


@register_integration
class GoogleFormsService(GoogleBaseService):
    SCOPES = [
        "https://www.googleapis.com/auth/forms.body.readonly",
        "https://www.googleapis.com/auth/forms.responses.readonly"
    ]

    id = "google_forms"
    name = "Google Forms"
    description = "Connect to Google Forms to receive responses."

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
        return cls.SCOPES
    
    def perform_action(self, action_id, connection, payload):
        return super().perform_action(action_id, connection, payload)
    
    def connect(self, config, secrets) -> Dict[str, Any]:
         print("I AM CONNECTING!!!!")
         return self.exchange_code(secrets["authorization_code"])
    
    # ----- Trigger: New Response -----

    def normalize_new_response(self, payload):
        return build_event(
            integration="google_forms",
            trigger="new_response",
            source_id=payload["id"],
            occurred_at=datetime.fromtimestamp(
                int(payload["createTime"]) / 1000,
                tz=timezone.utc
            ),
            data={
                "response_id": payload["responseId"],
                "submitted_at": payload["createTime"],
                "answers": payload["answers"]
                },
            raw=payload
        )

    def sample_new_response(self):
        return build_event(
            integration="google_forms",
            trigger="new_response",
            source_id="response_id_1010101010",
            occurred_at=datetime.now(),
            data={
                "response_id": "response_id_1010101010",
                "submitted_at": datetime.now(),
                "answers": {
                    "Question": "This is some random answer to some random question."
                }
            },
            raw={
                "formId": "form_id_1010101010",
                "responseId": "response_id_1010101010",
                "createTime": datetime.now(),
                "lastSubmittedTime": datetime.now(),
                "respondentEmail": "randomperson@email.com",
                "answers": {
                    "Question": "This is some random answer to some random question."
                }
            }
        )