import pytest

from core.dto import ResponseDTO
from core.exceptions import HTTPError


class TestResponseDTO:
    def test_raise_for_status_2xx_does_not_raise(self):
        ResponseDTO(text='ok', status_code=200, reason='OK').raise_for_status()

    def test_raise_for_status_399_does_not_raise(self):
        ResponseDTO(text='', status_code=399, reason='').raise_for_status()

    def test_raise_for_status_400_raises_http_error(self):
        with pytest.raises(HTTPError, match='HTTP 400'):
            ResponseDTO(text='', status_code=400, reason='Bad Request').raise_for_status()

    def test_raise_for_status_404_raises_http_error(self):
        with pytest.raises(HTTPError, match='HTTP 404'):
            ResponseDTO(text='', status_code=404, reason='Not Found').raise_for_status()

    def test_raise_for_status_500_raises_http_error(self):
        with pytest.raises(HTTPError, match='HTTP 500'):
            ResponseDTO(text='', status_code=500, reason='Internal Server Error').raise_for_status()

    def test_http_error_is_subclass_of_scraping_error(self):
        from core.exceptions import ScrapingError
        assert issubclass(HTTPError, ScrapingError)
