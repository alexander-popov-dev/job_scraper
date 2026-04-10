from dataclasses import dataclass
from datetime import datetime

from core.enums import SiteName
from core.exceptions import HTTPError


@dataclass
class ResponseDTO:
    """Unified response container returned by all HTTP client implementations."""

    text: str
    status_code: int
    reason: str

    def raise_for_status(self) -> None:
        """Raise an HTTPError if the status code indicates a client or server error."""
        if self.status_code >= 400:
            raise HTTPError(f'HTTP {self.status_code}: {self.reason}')


@dataclass
class SiteDTO:
    """Represents a configured scraping target loaded from the database."""

    id: int
    name: SiteName
    url: str
    proxy: str | None


@dataclass
class JobDTO:
    """Represents a single job listing parsed from a site."""

    url: str
    title: str
    description: str
    salary: str
    company: str
    city: str
    published_at: datetime
