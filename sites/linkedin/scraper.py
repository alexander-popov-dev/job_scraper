from abstract.scraper import BaseScraper
from core.dto import ResponseDTO


class Scraper(BaseScraper):
    """Fetches Python remote job listings from LinkedIn."""

    def _request(self) -> ResponseDTO:
        """Send a GET request to the LinkedIn job listings page."""
        headers = {'Cookie': self._site_config.cookie}
        return self._client.fetch(url=self._site_config.url, headers=headers)
