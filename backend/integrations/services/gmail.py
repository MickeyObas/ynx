from typing import Any, Dict
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.utils import parseaddr
import base64, json
from datetime import datetime, timezone

from .base import GoogleBaseService
from integrations.registry import register_integration
from core.events.factory import build_event


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
            "type": "poll",
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
            "sample_event": "sample_new_email",
            "apply_filters": "apply_filters"
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

    def _headers_to_dict(self, headers):
        headers_as_dict = {
            h["name"]: h["value"] for h in headers
        }
        return headers_as_dict

    # ----- Trigger: New Emails -----

    def fetch_new_emails(self, client, limit, since):
        list_response = client.users().messages().list(
            userId="me", 
            maxResults=limit,
            includeSpamTrash=False,
            labelIds=["INBOX", "IMPORTANT"]
            ).execute()
        messages = []
        for message in list_response["messages"]:
            message_response = client.users().messages().get(
                userId="me",
                id=message["id"],
                format="full"
            ).execute()
            messages.append(message_response)
        return messages    
        
    def normalize_new_email(self, payload):
        headers = {
            h["name"].lower(): h["value"] for h in payload["payload"]["headers"]
        }

        return build_event(
            integration="gmail",
            trigger="new_email",
            source_id=payload["id"],
            occurred_at=datetime.fromtimestamp(
                int(payload["internalDate"]) / 1000,
                tz=timezone.utc
            ),
            data={
                "subject": headers.get("subject"),
                "sender": headers.get("from"),
                "snippet": payload["snippet"]
            },
            raw=payload
        )
        # return {
        #     # "response_id": payload["responseId"],
        #     # "submitted_at": payload["timestamp"],
        #     "source_id": payload["id"],
        #     "received_at": payload["internalDate"],
        #     "subject": headers.get("subject"),
        #     "sender": headers.get("from"),
        #     "snippet": payload["snippet"],
        #     "labelIds": payload["labelIds"]
        # }

    def apply_filters(self, items, config):
        filtered_items = items

        if "label" in config:
            filtered_items = [
                item for item in filtered_items
                if config["label"] in item.get("labelIds", [])
            ]
        
        if "from_email" in config:
            filtered_items = [
                item for item in filtered_items
                if parseaddr(self._headers_to_dict(item["payload"]["headers"]).get("From", ""))[1].lower() == config["from_email"].lower()
            ]

        if "subject_contains" in config:
            filtered_items = [
                item for item in filtered_items
                if config["subject_contains"].lower() in self._headers_to_dict(item["payload"]["headers"]).get("Subject")
            ]

        return filtered_items


    def sample_new_email(self):
        pass