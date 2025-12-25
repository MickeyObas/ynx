from __future__ import annotations
import json, time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import requests
from datetime import timedelta, timezone, datetime

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request

from core.settings import GOOGLE_CLIENT_CONFIG
from automations.models import Connection


class BaseIntegrationService(ABC):
    """
    Abstract base for all integration services.
    """

    id: str | None = None
    name: str | None = None
    description: str = ""
    oauth_enabled: bool = False
    webhook_supported: bool = False
    
    TRIGGERS = {}
    ACTIONS = {}

    def __init__(self, connection: Optional["Connection"] = None):
        """
        Each integration can receive an optional Connection object (workspace-specific auth/config)
        """
        self.connection = connection
        
    @property
    def secrets(self):
        if not self.connection:
            return {}
        return self.connection.secrets or {}
    
    @secrets.setter
    def secrets(self, value):
        if not self.connection:
            raise RuntimeError
        self.connection.secrets = value
        self.connection.save(update_fields=["secrets"])

    @abstractmethod
    def get_client(self, connection):
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """Checks if the connection credentials are valid."""
        pass

    @abstractmethod
    def perform_action(self, action_id, connection, payload):
        pass

    def connect(self, config, secrets) -> Dict[str, Any]:
        """
        Called during user connection setup.
        Could perform OAuth or API key validation.
        Returns data to store in connection.secrets/config.
        """
        print("DEFAULT ATTTEMPT TO CONNECT")
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
        print("HEADERS ----> ", headers)
        response = requests.get(url, headers=headers, params=params)

        if response.status_code in (400, 401, 403) and retry:
            print("Token expired. Attempting refresh...")
            print(response.text)
            self.refresh_token()
            new_token = self.secrets.get("access_token")
            if new_token:
                headers['Authorization'] = f"Bearer {new_token}"
                response = requests.get(url, headers=headers, params=params)

        response.raise_for_status()
        return response.json()
    
    def get_auth_url(self, **kwargs):
        pass

    @classmethod
    def as_dict(cls):
        return {
            "id": cls.id,
            "name": cls.name,
            "description": cls.description,
            "triggers": cls.TRIGGERS,
            "actions": cls.ACTIONS,
        }


class GoogleBaseService(BaseIntegrationService):
    """
    Base for all Google integrations (Gmail, Forms, Sheets, etc.)
    Handles shared OAuth and credential logic.
    """

    SCOPES = []

    oauth_enabled = True
    GOOGLE_API_BASE = "https://www.googleapis.com"
    GOOGLE_CLIENT_CONFIG = GOOGLE_CLIENT_CONFIG

    def __init__(self, connection: Optional["Connection"] = None):
        super().__init__(connection)
        self.client_config = GOOGLE_CLIENT_CONFIG

    @classmethod
    def get_scopes(cls) -> list[str]:
        return cls.SCOPES

    @classmethod
    def get_auth_url(cls, connection_id: str) -> str:
        """Generate the Google OAuth consent screen URL."""
        flow = Flow.from_client_config(
            cls.GOOGLE_CLIENT_CONFIG,
            scopes=cls.get_scopes(),
            redirect_uri="http://localhost:8000/api/integrations/oauth/google/callback/",
        )
        state = json.dumps({"connection_id": str(connection_id)})
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
    
    def get_client(self, connection):
        if connection.status != "active":
            raise RuntimeError("Connection is not active")
        
        creds = self.build_credentials()

        if creds.expired and creds.refresh_token:
            creds.refresh(Request())

            connection.secrets.update({
                "access_token": creds.token,
                "expires_at": int(time.time() + creds.expiry.timestamp())
            })
            connection.save(update_fields=["secrets"])

        return self.build_client(creds)

    def build_credentials(self) -> Credentials:
        """Builds a google Credentials object from stored secrets."""
        return Credentials(
            token=self.secrets.get("access_token"),
            refresh_token=self.secrets.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_config["web"]["client_id"],
            client_secret=self.client_config["web"]["client_secret"],
            scopes=self.get_scopes()
        )

    def build_client(self, credentials):
        raise NotImplementedError

    # ---- Common OAuth utilities ----
    def refresh_token(self) -> None:
        """Refresh access token when expired."""
        print("Actually refreshing the token!!!")
        refresh_token = self.secrets.get("refresh_token")
        if not refresh_token:
            print("No refreh token")
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

        secrets = self.secrets
        secrets["access_token"] = tokens["access_token"]

        if "expires_in" in tokens:
            print("Tokens refreshed")
            expiry_time = datetime.utcnow() + timedelta(seconds=tokens["expires_in"])
            secrets["expiry"] = expiry_time.replace(microsecond=0).isoformat() 

        self.secrets = secrets

    def test_connection(self) -> bool:
        """Try a simple request to confirm credentials are valid."""

        try:
            print("TESTING GOOGLE CONNECTION")
            self.http_get(f"{self.GOOGLE_API_BASE}/oauth2/v3/tokeninfo")
            return True
        except Exception as e:
            print(e)
            return False