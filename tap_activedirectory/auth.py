import json
from datetime import datetime
from typing import Any, Dict, Optional

import requests
from singer_sdk.authenticators import APIAuthenticatorBase
from singer_sdk.streams import Stream as RESTStreamBase


class OAuth2Authenticator(APIAuthenticatorBase):
    def __init__(
        self,
        stream: RESTStreamBase,
        config_file: Optional[str] = None,
        auth_endpoint: Optional[str] = None,
    ) -> None:
        super().__init__(stream=stream)
        self._auth_endpoint = auth_endpoint
        self._config_file = config_file
        self._tap = stream._tap

    @property
    def auth_headers(self) -> dict:
        if not self.is_token_valid():
            self.update_access_token()
        result = super().auth_headers
        result["Authorization"] = f"Bearer {self._tap._config.get('access_token')}"
        return result

    @property
    def oauth_request_body(self) -> dict:
        """Define the OAuth request body for the hubspot API."""
        return {
            "client_id": self.config.get("client_id"),
            "grant_type": "refresh_token",
            "scope": "People.Read%20People.Read.All%20SecurityEvents.Read.All%20User.Read%20User.Read.All",
            "refresh_token": self.config.get("refresh_token"),
            "client_secret": self.config.get("client_secret")
        }

    def is_token_valid(self) -> bool:
        access_token = self._tap._config.get("access_token")
        now = round(datetime.utcnow().timestamp())
        expires_in = self._tap.config.get("expires_in")
        if  expires_in is not None:
            expires_in = int(expires_in)
        if not access_token:
            return False
        if not expires_in:
            return False
        return not ((expires_in - now) < 120)

    def update_access_token(self) -> None:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        token_response = requests.post(
            self._auth_endpoint, data=self.oauth_request_body, headers=headers
        )

        if (
            token_response.json().get("error_description")
            == "Rate limit exceeded: access_token not expired"
        ):
            return None

        try:
            token_response.raise_for_status()
            self.logger.info("OAuth authorization attempt was successful.")
        except Exception as ex:
            raise RuntimeError(
                f"Failed OAuth login, response was '{token_response.json()}'. {ex}"
            )
        token_json = token_response.json()
        self.access_token = token_json["access_token"]

        self._tap._config["access_token"] = token_json["access_token"]
        self._tap._config["refresh_token"] = token_json["refresh_token"]
        now = round(datetime.utcnow().timestamp())
        self._tap._config["expires_in"] = int(token_json["expires_in"]) + now

        with open(self._tap.config_file, "w") as outfile:
            json.dump(self._tap._config, outfile, indent=4)

