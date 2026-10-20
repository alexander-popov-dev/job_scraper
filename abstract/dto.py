from dataclasses import dataclass

from core.enums import SiteName
from abstract.parser import BaseParser
from abstract.repository import BaseJobsRepository
from abstract.scraper import BaseScraper


@dataclass
class ScraperConfigDTO:
    """Binds a site identifier with its scraper, parser, and repository implementations."""

    site: SiteName
    scraper: type[BaseScraper]
    parser: type[BaseParser]
    repo: type[BaseJobsRepository]


@dataclass
class ProviderConfigDTO:
    """Binds a site identifier with its scraper, parser, and repository implementations."""

    provider: str
    api_key: str
    login: str | None
    password: str | None
    folder_id: str | None
    profile_id: str
