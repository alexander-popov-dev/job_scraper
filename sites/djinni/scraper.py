from abstract.scraper import BaseScraper
from core.dto import ResponseDTO


class Scraper(BaseScraper):
    """Fetches Python job listings from Djinni."""

    def _request(self) -> ResponseDTO:
        """Send a GET request to the Djinni job listings page."""
        return self._client.fetch(url=self._site_config.url)
