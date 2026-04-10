from abstract.scraper import BaseScraper
from core.dto import ResponseDTO


class Scraper(BaseScraper):
    """Fetches Python job listings from Djinni."""

    SITE_NAME = 'TheJob'
    URL = 'https://thejob.tech/api/job?query&techs=Python&jobLocation&employmentType&page=1&company'

    def _request(self) -> ResponseDTO:
        """Send a GET request to the Djinni job listings page."""
        return self._client.fetch(self.URL)
