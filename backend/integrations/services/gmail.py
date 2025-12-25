from typing import Any, Dict
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64

from .base import GoogleBaseService
from integrations.registry import register_integration


@register_integration
class GmailService(GoogleBaseService):
    SCOPES = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send",
    ]

    id = "gmail"
    name = "Google Gmail"
    description = "Send and read emails using Gmail API"

    TRIGGERS = {
        "new_email": {
            "name": "New Email",
            "description": "Triggered when a new email is received in the inbox",
            "type": "polling",
            "is_testable": True,
            "config_schema": {
                "label": {
                    "type": "string",
                    "label": "Gmail Label",
                    "required": False,
                    "help_text": "Only trigger for emails with this Gmail label (e.g. INBOX, UNREAD, STARRED). Leave empty for all emails."
                },
                "from_email": {
                    "type": "string",
                    "label": "From Email",
                    "required": False,
                    "help_text": "Only trigger when the email is sent from this address."
                },
                "subject_contains": {
                    "type": "string",
                    "label": "Subject Contains",
                    "required": False,
                    "help_text": "Only trigger when the email subject contains this text."
                },
                "include_attachments": {
                    "type": "boolean",
                    "label": "Include Attachments",
                    "required": False,
                    "default": False,
                    "help_text": "Whether to include attachments in the trigger payload."
                }
            },
            "fetch": "fetch_new_emails",
            "normalize": "normalize_new_email",
            "sample_event": "sample_new_email"
        }
    }

    ACTIONS = {
        "send_email": {
            "name": "Send Email",
            "description": "Send an email message"
        }
    }

    def build_client(self, credentials):
        return build("gmail", "v1", credentials=credentials)

    def perform_action(self, action_id, connection, payload):
        action_map = {
            "send_email": self.send_email
        }
        if action_id not in action_map:
            raise ValueError(f"Unknown action: {action_id}")
        return action_map[action_id](connection, payload)

    def __init__(self, connection=None):
        super().__init__(connection)
        self.credentials = self.build_credentials()
        self.service = build("gmail", "v1", credentials=self.credentials)

    def connect(self, config, secrets) -> Dict[str, Any]:
        print("I AM CONNECTING!!!!")
        return self.exchange_code(secrets["authorization_code"])

    def send_email(self, connection, payload):
        message = MIMEText(payload.body)
        message["to"] = payload.to
        message["subject"] = payload.subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        result = (
            self.service.users()
            .messages()
            .send(userId="me", body={"raw": raw})
            .execute()
        )
        return result
    
    def get_client(self, connection):
        return super().get_client(connection)

    # ----- Trigger: New Emails -----

    def fetch_new_emails(self, client, limit, since):
        response = client.messages().list(userId="me", maxResults=limit).execute()
        return response["messages"]

    def normalize_new_email(self, payload):
        return {
            # "response_id": payload["responseId"],
            # "submitted_at": payload["timestamp"],
            "id": payload["id"],
        }

    def sample_new_email(self):
        pass