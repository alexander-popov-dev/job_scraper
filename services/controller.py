from abstract.dto import ScraperConfigDTO
from core.dto import JobDTO


class ScrapingController:
    """Orchestrates the fetch → parse → save pipeline for a single site."""

    def __init__(self, config: ScraperConfigDTO, proxy: str | None = None):
        """Initialize scraper, parser, and repository from the given config."""
        self._scraper = config.scraper(proxy=proxy)
        self._parser = config.parser()
        self._repo = config.repo()

    def fetch(self) -> str:
        """Fetch raw HTML or JSON content from the target site."""
        return self._scraper.fetch()

    def parse(self, content: str) -> list[JobDTO]:
        """Parse raw content into a list of job DTOs."""
        return self._parser.parse(content=content)

    def save(self, jobs: list[JobDTO]) -> list[JobDTO]:
        """Persist jobs and return only the newly inserted ones."""
        return self._repo.save(jobs=jobs)
