from __future__ import annotations


from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import requests
# from django.utils import timezone
from datetime import timedelta, timezone


class BaseIntegrationService(ABC):
    """
    Abstract base for all integration services.
    """

    id: str | None = None  # e.g. "google_forms"
    name: str | None = None
    description: str = ""
    oauth_enabled: bool = False
    webhook_supported: bool = False

    def __init__(self, connection: Optional["Connection"] = None):
        """
        Each integration can receive an optional Connection object (workspace-specific auth/config)
        """
        self.connection = connection
        self.config = connection.config if connection else {}
        self.secrets = connection.secrets if connection else {}

    @abstractmethod
    def test_connection(self) -> bool:
        """Checks if the connection credentials are valid."""
        pass

    def connect(self, **kwargs) -> Dict[str, Any]:
        """
        Called during user connection setup.
        Could perform OAuth or API key validation.
        Returns data to store in connection.secrets/config.
        """
        return {}

    def refresh_token(self) -> None:
        """Refresh tokens if applicable (OAuth)."""
        pass

    def handle_webhook(self, request):
        """Handle incoming webhooks (if supported)."""
        pass

    def get_resources(self, **kwargs):
        """Optional: list resources like forms, sheets, etc."""
        return []

    def http_get(self, url, headers=None, params=None, retry=True):
        """Helper for GET requests with token support."""
        headers = headers or {}
        if token := self.secrets.get("access_token"):
            headers["Authorization"] = f"Bearer {token}"
        
        response = requests.get(url, headers=headers, params=params)

        if response.status_code in (401, 403):
            print("TOKEN EXPIRED. ATTEMPTING REFRESH!!!")
            self.refresh_token()
            new_token = self.secrets.get("access_token")
            if new_token:
                headers['Authorization'] = f"Bearer {new_token}"
                response = requests.get(url, headers=headers, params=params)

        response.raise_for_status()
        return response.json()


from typing import Optional, Dict, Any
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from datetime import datetime
import json
import requests

from core.settings import GOOGLE_CLIENT_CONFIG


class GoogleBaseService(BaseIntegrationService):
    """
    Base for all Google integrations (Gmail, Forms, Sheets, etc.)
    Handles shared OAuth and credential logic.
    """

    oauth_enabled = True
    GOOGLE_API_BASE = "https://www.googleapis.com"
    GOOGLE_CLIENT_CONFIG = GOOGLE_CLIENT_CONFIG

    def __init__(self, connection: Optional["Connection"] = None):
        super().__init__(connection)
        self.client_config = GOOGLE_CLIENT_CONFIG

    # ---- OAuth ----
    @classmethod
    def get_scopes(cls) -> list[str]:
        """Each subclass overrides this."""
        return []

    @classmethod
    def get_auth_url(cls, workspace_id: str, integration_id: str) -> str:
        """Generate the Google OAuth consent screen URL."""
        flow = Flow.from_client_config(
            cls.GOOGLE_CLIENT_CONFIG,
            scopes=cls.get_scopes(),
            redirect_uri="http://localhost:8000/api/integrations/oauth/google/callback/",
        )
        # Pass both workspace_id + service_id in the state
        state = json.dumps({"workspace_id": workspace_id, "integration_id": integration_id})
        auth_url, _ = flow.authorization_url(
            access_type="offline", prompt="consent", state=state
        )
        return auth_url

    @classmethod
    def exchange_code(cls, code: str) -> dict:
        """Exchange authorization code for tokens."""
        flow = Flow.from_client_config(
            cls.GOOGLE_CLIENT_CONFIG,
            scopes=cls.get_scopes(),
            redirect_uri="http://localhost:8000/api/integrations/oauth/google/callback/",
        )
        flow.fetch_token(code=code)
        creds = flow.credentials

        return {
            "access_token": creds.token,
            "refresh_token": creds.refresh_token,
            "expiry": creds.expiry.isoformat() if creds.expiry else None,
        }

    def build_credentials(self) -> Credentials:
        """Builds a google Credentials object from stored secrets."""
        return Credentials(
            token=self.secrets.get("access_token"),
            refresh_token=self.secrets.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_config["web"]["client_id"],
            client_secret=self.client_config["web"]["client_secret"],
        )

    # ---- Common OAuth utilities ----
    def refresh_token(self) -> None:
        """Refresh access token when expired."""
        refresh_token = self.secrets.get("refresh_token")
        if not refresh_token:
            return

        data = {
            "client_id": self.client_config["web"]["client_id"],
            "client_secret": self.client_config["web"]["client_secret"],
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        r = requests.post("https://oauth2.googleapis.com/token", data=data)
        r.raise_for_status()
        tokens = r.json()
        self.secrets["access_token"] = tokens["access_token"]
        if "expires_in" in tokens:
            expiry_time = datetime.utcnow() + timedelta(seconds=tokens["expires_in"])
            self.secrets["expiry"] = expiry_time.replace(microsecond=0).isoformat() 

    def test_connection(self) -> bool:
        """Try a simple request to confirm credentials are valid."""

        try:
            print(self.http_get(f"{self.GOOGLE_API_BASE}/oauth2/v3/tokeninfo"))
            return True
        except Exception as e:
            print(e)
            return False