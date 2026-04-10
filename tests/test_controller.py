from unittest.mock import MagicMock

import pytest

from abstract.dto import ScraperConfigDTO
from core.dto import JobDTO
from core.enums import SiteName
from services.controller import ScrapingController


@pytest.fixture
def mocks():
    scraper = MagicMock()
    parser = MagicMock()
    repo = MagicMock()
    scraper_cls = MagicMock(return_value=scraper)
    parser_cls = MagicMock(return_value=parser)
    repo_cls = MagicMock(return_value=repo)
    config = ScraperConfigDTO(
        site=SiteName.DOU,
        scraper=scraper_cls,
        parser=parser_cls,
        repo=repo_cls,
    )
    return config, scraper, parser, repo, scraper_cls


class TestScrapingController:
    def test_scraper_instantiated_with_proxy(self, mocks):
        config, _, _, _, scraper_cls = mocks
        ScrapingController(config=config, proxy='http://proxy:8080')
        scraper_cls.assert_called_once_with(proxy='http://proxy:8080')

    def test_scraper_instantiated_without_proxy(self, mocks):
        config, _, _, _, scraper_cls = mocks
        ScrapingController(config=config, proxy=None)
        scraper_cls.assert_called_once_with(proxy=None)

    def test_fetch_delegates_to_scraper(self, mocks):
        config, scraper, _, _, _ = mocks
        scraper.fetch.return_value = '<html>jobs</html>'
        ctrl = ScrapingController(config=config)
        assert ctrl.fetch() == '<html>jobs</html>'
        scraper.fetch.assert_called_once()

    def test_parse_delegates_to_parser(self, mocks):
        config, _, parser, _, _ = mocks
        jobs = [MagicMock(spec=JobDTO)]
        parser.parse.return_value = jobs
        ctrl = ScrapingController(config=config)
        result = ctrl.parse('<html>jobs</html>')
        assert result == jobs
        parser.parse.assert_called_once_with(content='<html>jobs</html>')

    def test_save_delegates_to_repo(self, mocks):
        config, _, _, repo, _ = mocks
        jobs = [MagicMock(spec=JobDTO)]
        new_jobs = [MagicMock(spec=JobDTO)]
        repo.save.return_value = new_jobs
        ctrl = ScrapingController(config=config)
        result = ctrl.save(jobs)
        assert result == new_jobs
        repo.save.assert_called_once_with(jobs=jobs)

    def test_save_returns_only_new_jobs(self, mocks):
        config, _, _, repo, _ = mocks
        all_jobs = [MagicMock(), MagicMock(), MagicMock()]
        new_jobs = [all_jobs[0]]
        repo.save.return_value = new_jobs
        ctrl = ScrapingController(config=config)
        result = ctrl.save(all_jobs)
        assert result == new_jobs
        assert len(result) == 1
