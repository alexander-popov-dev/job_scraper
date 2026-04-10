from abc import ABC, abstractmethod

from core.dto import SiteDTO, JobDTO


class BaseJobsRepository(ABC):
    """Abstract interface for persisting job listings."""

    @abstractmethod
    def save(self, jobs: list[JobDTO]) -> list[JobDTO]:
        """Persist new jobs and return only the newly inserted ones."""
        ...


class BaseSitesRepository(ABC):
    """Abstract interface for retrieving scraping site configuration."""

    @abstractmethod
    def get_enabled(self) -> list[SiteDTO]:
        """Return all sites that are currently enabled for scraping."""
        ...


class BaseSessionsRepository(ABC):
    """Abstract interface for tracking scraping session lifecycle."""

    @abstractmethod
    def create(self, site_id: int) -> int:
        """Create a new session record and return its ID."""
        ...

    @abstractmethod
    def complete(self, session_id: int, jobs_found: int) -> None:
        """Mark a session as completed with the number of new jobs found."""
        ...

    @abstractmethod
    def fail(self, session_id: int, error: str) -> None:
        """Mark a session as failed and record the error message."""
        ...


class BaseRawRepository(ABC):
    """Abstract interface for storing and cleaning up raw HTTP responses."""

    @abstractmethod
    def save(self, session_id: int, content: str) -> None:
        """Persist the raw response body linked to a scraping session."""
        ...

    @abstractmethod
    def cleanup(self, older_than_days: int) -> int:
        """Delete raw responses older than the given number of days."""
        ...
