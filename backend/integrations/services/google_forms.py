from typing import Any, Dict
from googleapiclient.discovery import build
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
            "type": "poll",
            "is_testable": True,
            "config_schema": {
                "form_id": {
                    "type": "string",
                    "label": "Form ID",
                    "required": True,
                    "help_text": "The ID of the Google Form to watch."
                }
            },
            "fetch": "fetch_new_responses",
            "normalize": "normalize_new_response",
            "sample_event": "sample_new_response",
        }
    }

    ACTIONS = {}

    @classmethod
    def get_scopes(cls) -> list[str]:
        return cls.SCOPES

    def build_client(self, credentials):
        return build("forms", "v1", credentials=credentials)
    
    def perform_action(self, action_id, connection, payload):
        return super().perform_action(action_id, connection, payload)
    
    def connect(self, config, secrets) -> Dict[str, Any]:
        return self.exchange_code(secrets["authorization_code"])
    
    # ----- Trigger: New Responses -----
    def fetch_new_responses(self, client, *, since_cursor, limit):
        """
        Fetch new Google Form responses since the last cursor.
        """

        form_id = self.trigger_instance.config["form_id"]

        response = client.forms().responses().list(
            formId=form_id,
            pageSize=limit,
        ).execute()

        new_responses = []

        for item in response.get("responses", []):
            
            submitted_at = datetime.fromisoformat(
                item["lastSubmittedTime"].replace("Z", "+00:00")
            )

            if since_cursor and submitted_at <= since_cursor:
                continue

            new_responses.append(item)

        return new_responses

    def normalize_new_response(self, payload):
        return build_event(
            integration="google_forms",
            trigger="new_response",
            source_id=payload["responseId"],
            occurred_at=datetime.fromisoformat(
                payload["lastSubmittedTime"].replace("Z", "+00:00")
            ),
            data={
                # TODO: Add form_id to the data
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