"""WordPress.org API client."""

from __future__ import annotations

from typing import Any, Dict, Optional, Iterator

from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.streams import RESTStream


class WordPressOrgAPIStream(RESTStream):
    """WordPress.org API stream class."""

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        return self.config.get("api_url", "https://api.wordpress.org")

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed."""
        headers = {}
        if self.config.get("user_agent"):
            headers["User-Agent"] = self.config.get("user_agent")
        return headers

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        return params

    def parse_response(self, response: Any) -> Iterator[dict]:
        """Parse the response and return an iterator of result records."""
        yield from extract_jsonpath(self.records_jsonpath, input=response.json())