class ScrapingError(Exception):
    """Raised when fetching content from a site fails."""


class HTTPError(ScrapingError):
    """Raised when an HTTP response indicates a client or server error."""

    def __init__(self, message: str, status_code: int, retryable: bool = True):
        super().__init__(message)
        self.status_code = status_code
        self.retryable = retryable


class ParsingError(Exception):
    """Raised when a parser cannot extract data from the site response."""
