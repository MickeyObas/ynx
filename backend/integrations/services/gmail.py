from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64

from .base import GoogleBaseService


class GmailService(GoogleBaseService):
    id = "gmail"
    name = "Google Gmail"
    description = "Send and read emails using Gmail API"

    TRIGGERS = {
        "new_email": {
            "name": "New Email",
            "description": "Triggered when a new email is received"
        }
    }

    ACTIONS = {
        "send_email": {
            "name": "Send Email",
            "description": "Send an email message"
        }
    }

    @classmethod
    def get_scopes(cls) -> list[str]:
        return [
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.send",
        ]
    
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