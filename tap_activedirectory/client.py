"""REST client handling, including ActivedirectoryStream base class."""

import requests
from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from memoization import cached

from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.streams import RESTStream

from tap_activedirectory.auth import OAuth2Authenticator
import re
from singer_sdk.exceptions import FatalAPIError, RetriableAPIError


SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class ActivedirectoryStream(RESTStream):
    """Activedirectory stream class."""


    url_base = "https://graph.microsoft.com"

    records_jsonpath = "$.value[*]"
    add_params = None

    @property
    def authenticator(self) -> OAuth2Authenticator:
        oauth_url = f"https://login.microsoftonline.com/{self.config.get('tenant')}/oauth2/token"
        return OAuth2Authenticator(self, self.config, auth_endpoint=oauth_url)

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed."""
        headers = {}
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config.get("user_agent")
        return headers

    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any]
    ) -> Optional[Any]:
        """Return a token for identifying next page or None if no more pages."""
        if response.json().get("@odata.nextLink"):
            next_page_token = re.findall("skiptoken=(.*)", response.json().get("@odata.nextLink"))
            if next_page_token:
                return next_page_token
        return None

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["$skiptoken"] = next_page_token
        if self.add_params:
            params.update(self.add_params)
        return params
    
    def validate_response(self, response: requests.Response) -> None:
        if (
            response.status_code in self.extra_retry_statuses
            or 500 <= response.status_code < 600
        ):
            msg = self.response_error_message(response)
            raise RetriableAPIError(msg, response)
        elif 400 <= response.status_code < 500 and response.status_code not in [403]:
            msg = self.response_error_message(response)
            raise FatalAPIError(msg)