import logging
import time
from abc import ABC, abstractmethod

from abstract.client import BaseClient
from clients.requests_client import RequestsClient
from core.dto import ResponseDTO
from core.exceptions import ScrapingError

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Base scraper with built-in retry logic and exponential backoff."""

    SITE_NAME: str = ''
    MAX_RETRIES: int = 5
    RETRY_DELAY: int = 15

    def __init__(self, proxy: str | None = None, client: BaseClient | None = None):
        """Use the injected client, or default to RequestsClient with the given proxy."""
        self._client = client or RequestsClient(proxy=proxy)

    def fetch(self) -> str:
        """Fetch page content, retrying up to MAX_RETRIES times with exponential backoff."""
        for attempt in range(1, self.MAX_RETRIES + 1):
            response = None
            try:
                response = self._request()
                response.raise_for_status()
                return response.text
            except Exception as e:
                delay = self.RETRY_DELAY * (2 ** (attempt - 1))
                if response is not None:
                    logger.warning(
                        f'[{self.SITE_NAME}] Attempt {attempt} failed. '
                        f'Status: {response.status_code}. Reason: {response.reason}. Error: {e}. '
                        f'Retrying in {delay}s'
                    )
                else:
                    logger.warning(
                        f'[{self.SITE_NAME}] Attempt {attempt} failed. Error: {e}. '
                        f'Retrying in {delay}s'
                    )
                if attempt < self.MAX_RETRIES:
                    time.sleep(delay)

        raise ScrapingError(
            f'[{self.SITE_NAME}] Failed to retrieve response after {self.MAX_RETRIES} attempts'
        )

    @abstractmethod
    def _request(self) -> ResponseDTO:
        """Execute the request via self._client and return a ResponseDTO."""
        ...
