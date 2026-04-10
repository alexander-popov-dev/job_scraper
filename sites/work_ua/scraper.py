from abstract.scraper import BaseScraper
from core.dto import ResponseDTO


class Scraper(BaseScraper):
    """Fetches Python remote job listings from Work.ua."""

    SITE_NAME = 'WorkUA'
    URL = 'https://www.work.ua/jobs-remote-it-industry-it-python/'

    def _request(self) -> ResponseDTO:
        """Send a GET request to the Work.ua job listings page."""
        return self._client.fetch(self.URL)
