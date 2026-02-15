from typing import Any, Dict
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.utils import parseaddr
import base64, json
from datetime import datetime, timezone as p_timezone
from email.mime.multipart import MIMEMultipart
from google.auth.exceptions import RefreshError


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
                "sender": {
                    "type": "string",
                    "label": "Sender",
                    "required": True,
                    "default": False,
                    "help_text": "The sender of the email."
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
            "key": "send_email",
            "name": "Send Email",
            "description": "Send an email message via Gmail",
            "category": "messaging",

            "config_schema": {
                "to": {
                    "type": "string",
                    "label": "Recipient Email",
                    "required": True,
                    "placeholder": "recipient@example.com",
                    "description": "Email address of the recipient"
                },
                "subject": {
                    "type": "string",
                    "label": "Subject",
                    "required": True,
                    "placeholder": "Hello from Automation"
                },
                "body": {
                    "type": "text",
                    "label": "Email Body",
                    "required": True,
                    "placeholder": "Write your message here"
                },
                "cc": {
                    "type": "string",
                    "label": "CC",
                    "required": False,
                    "placeholder": "cc@example.com"
                },
                "bcc": {
                    "type": "string",
                    "label": "BCC",
                    "required": False,
                    "placeholder": "bcc@example.com"
                }
            },
            "sample_config": {
                "to": "test@example.com",
                "subject": "Test Email",
                "body": "This is a test email from the automation system"
            }
        }
    }

    def build_client(self, credentials):
        return build("gmail", "v1", credentials=credentials)

    def perform_action(self, action_id, *, config, connection, context):
        action_map = {
            "send_email": self.send_email
        }
        if action_id not in action_map:
            raise ValueError(f"Unknown action: {action_id}")
        return action_map[action_id](
            config=config,
            connection=connection
        )

    def __init__(self, connection=None):
        super().__init__(connection)
        self.credentials = self.build_credentials()
        self.service = build("gmail", "v1", credentials=self.credentials)

    def connect(self, config, secrets) -> Dict[str, Any]:
        return self.exchange_code(secrets["authorization_code"])

    def _headers_to_dict(self, headers):
        headers_as_dict = {
            h["name"]: h["value"] for h in headers
        }
        return headers_as_dict

    # ----- Trigger: New Emails -----
    def fetch_new_emails(self, client, *, since_cursor, limit):
        response = client.users().messages().list(
            userId="me",
            maxResults=limit,
            labelIds=["INBOX"],
            includeSpamTrash=False,
        ).execute()

        messages = []

        for item in response.get("messages", []):
            message_id = item["id"]

            metadata = client.users().messages().get(
                userId="me",
                id=message_id,
                format="metadata",
                metadataHeaders=["Date"],
            ).execute()

            internal_date = datetime.fromtimestamp(
                int(metadata["internalDate"])/ 1000,
                tz=p_timezone.utc
)
            # if since_cursor and internal_date <= since_cursor:
            #     continue

            full_message = client.users().messages().get(
                userId="me",
                id=message_id,
                format="full",
            ).execute()

            messages.append(full_message)

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
                tz=p_timezone.utc
            ),
            data={
                "subject": headers.get("subject"),
                "sender": headers.get("from"),
                "snippet": payload["snippet"]
            },
            raw=payload
        )

    def sample_new_email(self):
        pass


    # ----- Action: Send Email -----
    def send_email(self, *, config, connection, event=None, mode="live"):
        """
        Execute Gmail 'send_email' action.

        config: validated action config
        connection: OAuth credentials / token object
        event: triggering event payload (optional)
        mode: 'test' or 'live'
        """
        
        to_email = config["to"]
        subject = config["subject"]
        body = config["body"]
        cc = config.get("cc")
        bcc = config.get("bcc")

        message = MIMEMultipart()
        message["To"] = to_email
        message["Subject"] = subject

        if cc:
            message["Cc"] = cc
        if bcc:
            message["Bcc"] = bcc

        message.attach(MIMEText(body, "plain"))

        raw_message = base64.urlsafe_b64encode(
            message.as_bytes()
        ).decode("utf-8")

        client = self.get_client(connection)

        if mode == "test":
            return {
                "status": "skipped",
                "reason": "Test mode",
                "to": to_email,
                "subject": subject
            }

        try:
            response = client.users().messages().send(
                userId="me",
                body={"raw": raw_message}
            ).execute()
        # Catch specific error/exception
        except RefreshError:
            raise Exception("Gmail connection expired. Re-authentication required.")

        return {
            "status": "sent",
            "message_id": response.get("id")
        }
