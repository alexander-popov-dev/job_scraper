import logging
from abc import ABC, abstractmethod

from abstract.client import BaseClient
from clients.requests_client import RequestsClient
from core.dto import ResponseDTO
from core.exceptions import HTTPError, ScrapingError

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Base scraper — makes a single HTTP attempt and raises on failure.

    Retry logic lives in the Celery task (scrape_site) so workers are not
    blocked during backoff delays.
    """

    SITE_NAME: str = ''

    def __init__(self, proxy: str | None = None, client: BaseClient | None = None):
        """Use the injected client, or default to RequestsClient with the given proxy."""
        self._client = client or RequestsClient(proxy=proxy)

    def fetch(self) -> str:
        """Fetch page content once.

        Raises HTTPError for HTTP failures (retryable=False for 4xx except 429).
        Raises ScrapingError for network-level failures (always retryable).
        """
        response = None
        try:
            response = self._request()
            response.raise_for_status()
            return response.text
        except Exception as e:
            if response is not None:
                retryable = not (404 <= response.status_code < 500 and response.status_code != 429)
                raise HTTPError(
                    f'[{self.SITE_NAME}] HTTP {response.status_code}: {response.reason}',
                    status_code=response.status_code,
                    retryable=retryable,
                ) from e
            raise ScrapingError(f'[{self.SITE_NAME}] Request failed: {e}') from e

    @abstractmethod
    def _request(self) -> ResponseDTO:
        """Execute the request via self._client and return a ResponseDTO."""
        ...
