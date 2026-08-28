import logging
from abc import ABC, abstractmethod

from core.dto import ResponseDTO

logger = logging.getLogger(__name__)


class BaseClient(ABC):
    """Abstract client for fetching web content, independent of the underlying mechanism."""

    def __init__(self) -> None:
        logger.info(f"HTTP Client: {self.__class__.__name__}")

    def __enter__(self) -> 'BaseClient':
        """Support usage as a context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Close the client when exiting the context."""
        self.close()

    def close(self) -> None:
        """Release any resources held by the client. Override when needed."""

    @abstractmethod
    def fetch(self, url: str, **kwargs) -> ResponseDTO:
        """Fetch content from the given URL and return a unified ResponseDTO."""
        ...
