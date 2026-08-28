from abstract.scraper import BaseScraper
from core.dto import ResponseDTO


class Scraper(BaseScraper):
    """Fetches Python job listings from The Job."""

    SITE_NAME = "TheJob"
    URL = "https://thejob.tech/api/job?query=python&jobLocation=Remote&&page=1"
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/144.0.0.0 Safari/537.36"
        )
    }

    def _request(self) -> ResponseDTO:
        """Send a GET request to the The Job job listings page."""

        return self._client.fetch(self.URL, headers=self.HEADERS)
