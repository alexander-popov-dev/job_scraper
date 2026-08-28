from abstract.client import BaseClient
from abstract.scraper import BaseScraper
from clients.curl_client import CurlClient
from core.dto import ResponseDTO


class Scraper(BaseScraper):
    """Fetches Python remote job listings from Work.ua."""

    SITE_NAME = 'WorkUA'
    URL = 'https://www.work.ua/jobs-remote-it-industry-it-python/'

    def __init__(self, proxy: str | None = None, client: BaseClient | None = None):
        super().__init__(proxy, client=client or CurlClient())

    def _request(self) -> ResponseDTO:
        """Send a GET request to the Work.ua job listings page."""
        return self._client.fetch(url=self.URL)
