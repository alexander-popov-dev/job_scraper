from abstract.scraper import BaseScraper
from core.dto import ResponseDTO


class Scraper(BaseScraper):
    """Fetches Python job listings from Djinni."""

    SITE_NAME = 'Djinni'
    URL = (
        'https://djinni.co/jobs/?'
        'all_keywords=Python%20&'
        'search_type=basic-search&'
        'primary_keyword=Python&'
        'exp_level=1y&'
        'exp_level=2y&'
        'exp_level=3y&'
        'english_level=no_english&'
        'english_level=basic&'
        'english_level=pre&'
        'english_level=intermediate'
    )

    def _request(self) -> ResponseDTO:
        """Send a GET request to the Djinni job listings page."""
        return self._client.fetch(self.URL)
