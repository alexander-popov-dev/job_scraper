from abstract.http_client import BaseHTTPClient
from abstract.scraper import BaseScraper
from clients.curl_client import CurlClient
from core.dto import ResponseDTO, SiteDTO


class Scraper(BaseScraper):
    """Fetches Python job listings from The Job."""

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/144.0.0.0 Safari/537.36"
        )
    }

    def __init__(self, site_config: SiteDTO, client: BaseHTTPClient | None = None):
        super().__init__(site_config, client=client or CurlClient(proxy=site_config.proxy))

    def _request(self) -> ResponseDTO:
        """Send a GET request to The Job job listings page."""

        return self._client.fetch(self._site_config.url, headers=self.HEADERS)
