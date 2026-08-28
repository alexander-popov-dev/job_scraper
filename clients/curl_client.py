import logging

import curl_cffi

from abstract.client import BaseClient
from core.dto import ResponseDTO


logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30

class CurlClient(BaseClient):
    """HTTP client implementation backed by the `curl_cffi` library."""

    def __init__(self, proxy: str | None = None):
        """Initialize with an optional proxy applied to all requests."""
        self._proxy = proxy
        super().__init__()

    def fetch(self, url: str, method: str = 'GET', **kwargs) -> ResponseDTO:
        """Execute an HTTP request and return a ResponseDTO."""
        kwargs.setdefault('timeout', DEFAULT_TIMEOUT)

        if method == 'GET':
            r = curl_cffi.get(url, impersonate="chrome")
        else:
            raise ValueError('Unsupported HTTP method')

        return ResponseDTO(text=r.text, status_code=r.status_code, reason=r.reason or '')
