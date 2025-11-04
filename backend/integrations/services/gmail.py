from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64

from .base import GoogleBaseService


class GmailService(GoogleBaseService):
    id = "gmail"
    name = "Google Gmail"
    description = "Send and read emails using Gmail API"

    @classmethod
    def get_scopes(cls) -> list[str]:
        return [
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.send",
        ]

    def __init__(self, connection=None):
        super().__init__(connection)
        self.credentials = self.build_credentials()
        self.service = build("gmail", "v1", credentials=self.credentials)

    def send_email(self, to: str, subject: str, body: str):
        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        result = (
            self.service.users()
            .messages()
            .send(userId="me", body={"raw": raw})
            .execute()
        )
        return result
    
    # def test_connection(self):
    #     """Try to get user profile to confirm validity."""
    #     try:
    #         print(self.service.users().getProfile(userId="me").execute())
    #         return True
    #     except Exception:
    #         return False
    