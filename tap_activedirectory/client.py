"""REST client handling, including ActivedirectoryStream base class."""

import requests
from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from memoization import cached

from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.streams import RESTStream

from tap_activedirectory.auth import OAuth2Authenticator
import re


SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class ActivedirectoryStream(RESTStream):
    """Activedirectory stream class."""


    url_base = "https://graph.microsoft.com/v1.0/"

    records_jsonpath = "$.value[*]"

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
            return re.search("skiptoken=(.*)&", response.json().get("@odata.nextLink"))
        return None

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["skiptoken"] = next_page_token
        return params