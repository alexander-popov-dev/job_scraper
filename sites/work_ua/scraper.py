from abstract.http_client import BaseHTTPClient
from abstract.scraper import BaseScraper
from clients.curl_client import CurlClient
from core.dto import ResponseDTO, SiteDTO


class Scraper(BaseScraper):
    """Fetches Python remote job listings from Work.ua."""

    def __init__(self, site_config: SiteDTO, client: BaseHTTPClient | None = None):
        super().__init__(site_config, client=client or CurlClient())

    def _request(self) -> ResponseDTO:
        """Send a GET request to the Work.ua job listings page."""
        return self._client.fetch(url=self._site_config.url)
