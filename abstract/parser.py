from abc import ABC, abstractmethod

from core.dto import JobDTO


class BaseParser(ABC):
    """Base class for all site-specific job listing parsers."""

    @abstractmethod
    def parse(self, content: str) -> list[JobDTO]:
        """Parse raw HTML or JSON content and return a list of job DTOs."""
        ...
