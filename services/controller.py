from abstract.dto import ScraperConfigDTO, ProviderConfigDTO
from core.dto import JobDTO, SiteDTO


class ScrapingController:
    """Orchestrates the fetch → parse → save pipeline for a single site."""

    def __init__(
            self,
            scraper_config: ScraperConfigDTO,
            site_config: SiteDTO,
    ) -> None:
        """Initialize scraper, parser, and repository from the given config."""
        self._scraper = scraper_config.scraper(site_config=site_config)
        self._parser = scraper_config.parser()
        self._repo = scraper_config.repo()

    def fetch(self) -> str:
        """Fetch raw HTML or JSON content from the target site."""
        return self._scraper.fetch()

    def parse(self, content: str) -> list[JobDTO]:
        """Parse raw content into a list of job DTOs."""
        return self._parser.parse(content=content)

    def save(self, jobs: list[JobDTO]) -> list[JobDTO]:
        """Persist jobs and return only the newly inserted ones."""
        return self._repo.save(jobs=jobs)
