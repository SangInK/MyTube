from requests import post

import google.oauth2.credentials
import googleapiclient.discovery
import google.auth.transport.requests as google_requests

from .GoogleUserService import GoogleUserService


class CredentialsService:
    def __init__(self, credentials):
        self._set_credentials(credentials)

    def _set_credentials(self, credentials):
        self.credentials = google.oauth2.credentials.Credentials(**credentials)
        # self._refresh_credentials()

    def _refresh_credentials(self):
        self.set_google_user(access_token=self.credentials.token)

        if self.google_user.is_valid():
            self.credentials.refresh(google_requests.Request())
            self._update_google_user()

    def _update_google_user(self):
        if (
            self.google_user.is_valid()
            and self.google_user.data["access_token"] != self.credentials.token
            and self.google_user.data["refresh_token"] != self.credentials.refresh_token
        ):
            self.google_user.update_user(
                access_token=self.google_user.data["access_token"],
                refresh_token=self.google_user.data["refresh_token"],
            )

    def set_google_user(self, access_token):
        self.google_user = GoogleUserService(access_token=access_token)
        self._update_google_user()

    def credentials_to_dict(self):
        return {
            "token": self.credentials.token,
            "refresh_token": self.credentials.refresh_token,
            "token_uri": self.credentials.token_uri,
            "client_id": self.credentials.client_id,
            "client_secret": self.credentials.client_secret,
            "scopes": self.credentials.scopes,
        }

    def rovoke_credentials(self):
        self.set_google_user(self.credentials.token)
        self._refresh_credentials()

        url = "https://oauth2.googleapis.com/revoke"
        data = {"token": self.credentials.token}
        headers = {"content-type": "application/x-www-form-urlencoded"}

        return post(url, data=data, headers=headers, timeout=10)

    def get_youtube(self):
        self._refresh_credentials()

        youtube = googleapiclient.discovery.build(
            "youtube", "v3", credentials=self.credentials
        )

        return youtube
