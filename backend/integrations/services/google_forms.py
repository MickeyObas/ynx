from django.conf import settings
from .base import BaseIntegrationService, GoogleBaseService

import requests
import json
import urllib.parse

class GoogleFormsService(BaseIntegrationService):
    id = "google_forms"
    name = "Google Forms"
    description = "Connect to Google Forms to receive responses."
    oauth_enabled = True
    webhook_supported = True

    client_id = settings.GOOGLE_CLIENT_ID
    client_secret = settings.GOOGLE_CLIENT_SECRET
    redirect_uri = f"{settings.GOOGLE_REDIRECT_BASE}/google/callback/"

    def get_auth_url(self, workspace_id=None, integration_id=None):
        base = "https://accounts.google.com/o/oauth2/v2/auth"
        scope = "https://www.googleapis.com/auth/forms.body.readonly"
        state_data = {
            "workspace_id": workspace_id,
            "integration_id": integration_id
        }
        state = urllib.parse.quote(json.dumps(state_data))

        url = (
            f"{base}?client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&response_type=code&access_type=offline"
            f"&scope={scope}&prompt=consent"
            f"&state={state}"
        )

        return url

    def exchange_code_for_token(self, code):
        url = "https://oauth2.googleapis.com/token"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
        }
        res = requests.post(url, data=payload)
        res.raise_for_status()
        data = res.json()

        return {
            "access_token": data["access_token"],
            "refresh_token": data.get("refresh_token"),
            "expires_at": data.get("expires_in"),
        }

    def test_connection(self):
        headers = {"Authorization": f"Bearer {self.secrets['access_token']}"}
        # TODO: Use non-static values for form ids
        form_id = "1UXlc3Ndi1ZleBjOGZr2ffH-4j41iXNnTda2H-PXpaDE"
        response = requests.get(f"https://forms.googleapis.com/v1/forms/{form_id}", headers=headers)
        response.raise_for_status()
        return response.json()


class GoogleFormsServicee(GoogleBaseService):
    id = "google_forms"
    name = "Google Forms"
    description = "Connect to Google Forms to receive responses."
    oauth_enabled = True
    webhook_supported = True

    @classmethod
    def get_scopes(cls) -> list[str]:
        return [
            "https://www.googleapis.com/auth/forms.body.readonly",
            "https://www.googleapis.com/auth/forms.responses.readonly"
        ]
    
    # def test_connection(self):
    #     headers = {"Authorization": f"Bearer {self.secrets['access_token']}"}
    #     # TODO: Use non-static values for form ids
    #     form_id = "1UXlc3Ndi1ZleBjOGZr2ffH-4j41iXNnTda2H-PXpaDE"
    #     response = requests.get(f"https://forms.googleapis.com/v1/forms/{form_id}", headers=headers)
    #     response.raise_for_status()
    #     return response.json()