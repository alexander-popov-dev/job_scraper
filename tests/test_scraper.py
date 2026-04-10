from unittest.mock import MagicMock, call, patch

import pytest

from abstract.scraper import BaseScraper
from core.dto import ResponseDTO
from core.exceptions import ScrapingError


def make_response(status: int = 200) -> ResponseDTO:
    return ResponseDTO(
        text='page content',
        status_code=status,
        reason='OK' if status == 200 else 'Error',
    )


class StubScraper(BaseScraper):
    """Concrete scraper for testing with a controllable _request side effect."""

    SITE_NAME = 'TestSite'
    MAX_RETRIES = 3
    RETRY_DELAY = 1

    def __init__(self, side_effects: list):
        super().__init__(client=MagicMock())
        self._effects = iter(side_effects)

    def _request(self) -> ResponseDTO:
        effect = next(self._effects)
        if isinstance(effect, Exception):
            raise effect
        return effect


class TestBaseScraper:
    def test_success_on_first_attempt_returns_text(self):
        scraper = StubScraper([make_response(200)])
        assert scraper.fetch() == 'page content'

    def test_recovers_after_one_failed_attempt(self):
        scraper = StubScraper([make_response(500), make_response(200)])
        with patch('time.sleep'):
            result = scraper.fetch()
        assert result == 'page content'

    def test_recovers_after_network_exception(self):
        scraper = StubScraper([ConnectionError('timeout'), make_response(200)])
        with patch('time.sleep'):
            result = scraper.fetch()
        assert result == 'page content'

    def test_raises_scraping_error_after_all_retries_exhausted(self):
        scraper = StubScraper([make_response(500)] * 3)
        with patch('time.sleep'), pytest.raises(ScrapingError, match='TestSite'):
            scraper.fetch()

    def test_raises_scraping_error_after_repeated_exceptions(self):
        scraper = StubScraper([ConnectionError()] * 3)
        with patch('time.sleep'), pytest.raises(ScrapingError):
            scraper.fetch()

    def test_exponential_backoff_sleep_durations(self):
        scraper = StubScraper([make_response(500)] * 3)
        with patch('time.sleep') as mock_sleep, pytest.raises(ScrapingError):
            scraper.fetch()
        # RETRY_DELAY=1: attempt 1 → sleep(1), attempt 2 → sleep(2), attempt 3 → no sleep
        assert mock_sleep.call_args_list == [call(1), call(2)]

    def test_no_sleep_on_last_attempt(self):
        scraper = StubScraper([make_response(500)] * 3)
        with patch('time.sleep') as mock_sleep, pytest.raises(ScrapingError):
            scraper.fetch()
        assert mock_sleep.call_count == scraper.MAX_RETRIES - 1

    def test_proxy_passed_to_default_client(self):
        from clients.requests_client import RequestsClient
        with patch.object(RequestsClient, '__init__', return_value=None) as mock_init:
            BaseScraper.__abstractmethods__ = frozenset()
            scraper = BaseScraper(proxy='http://proxy:8080')  # type: ignore[abstract]
            mock_init.assert_called_once_with(proxy='http://proxy:8080')
