class ScrapingError(Exception):
    """Raised when fetching content from a site fails after all retries."""


class HTTPError(ScrapingError):
    """Raised when an HTTP response indicates a client or server error."""


class ParsingError(Exception):
    """Raised when a parser cannot extract data from the site response."""
