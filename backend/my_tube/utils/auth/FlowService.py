import json
import os

from django.conf import settings

import google_auth_oauthlib.flow


class FlowService:
    """
    Google API를 사용하기 위해 Google 유저를 인증
    Google API의 보안 정보를 사용하여 Google 유저 인증 창의 url 반환
    """

    # google oauth2를 사용하여 인증할 때, 리다이렉트 처리할 url
    API_URI = "auth/redirect"

    GOOGLE_CLIENT_TYPE = "web"

    SCOPES = [
        "https://www.googleapis.com/auth/youtube",
        "https://www.googleapis.com/auth/youtube.channel-memberships.creator",
        "https://www.googleapis.com/auth/youtube.readonly",
    ]

    def __init__(self):
        self._set_config()

    def _set_config(self):
        """
        client_secret.json에 저장된 google api 관련 정보를 FlowService에 설정
        """

        self.config = {
            self.GOOGLE_CLIENT_TYPE: {
                "client_id": os.getenv("client_id", ""),
                "client_secret": os.getenv("client_secret", ""),
                "project_id": os.getenv("project_id", ""),
                "auth_uri": os.getenv("auth_uri", ""),
                "token_uri": os.getenv("token_uri", ""),
                "auth_provider_x509_cert_url": os.getenv(
                    "auth_provider_x509_cert_url", ""
                ),
                "redirect_uris": [f"{settings.BASE_BACKEND_URL}{self.API_URI}"],
                "javascript_origins": [],
            }
        }

    def set_flow(self, data):
        """
        Google 보안 정보를 사용하여 Google Flow 객체 생성
        """
        flow = google_auth_oauthlib.flow.Flow.from_client_config(**data)
        flow.redirect_uri = self.config["web"]["redirect_uris"][0]

        self._flow = flow

    def get_authorization_url(self):
        """
        Google Flow 객체를 사용하여 인증 화면 url 생성
        """
        authorization_url, state = self._flow.authorization_url(
            access_type="offline", include_granted_scopes="true", prompt="consent"
        )

        return authorization_url, state

    def set_token(self, code):
        """
        Google Flow 객체를 사용하여 Token 생성
        """
        self._flow.fetch_token(code=code)

    def get_credentials(self):
        """
        Google Flow 객체를 사용하여 생성된 인증서를 반환
        """
        credentials = self._flow.credentials

        return {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes,
        }
