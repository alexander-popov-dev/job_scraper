import requests

from abstract.client import BaseClient
from core.dto import ResponseDTO

DEFAULT_TIMEOUT = 30


class RequestsClient(BaseClient):
    """HTTP client implementation backed by the `requests` library."""

    def __init__(self, proxy: str | None = None):
        """Initialize with an optional proxy applied to all requests."""
        self._proxies = {'http': proxy, 'https': proxy} if proxy else None

    def fetch(self, url: str, method: str = 'GET', **kwargs) -> ResponseDTO:
        """Execute an HTTP request using `requests.request` and return a ResponseDTO."""
        kwargs.setdefault('timeout', DEFAULT_TIMEOUT)
        r = requests.request(method, url, proxies=self._proxies, **kwargs)
        return ResponseDTO(text=r.text, status_code=r.status_code, reason=r.reason or '')
