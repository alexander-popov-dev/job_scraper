from datetime import datetime, timezone
from unittest.mock import MagicMock, patch, call

import pytest

from celery_app.tasks import run_scraping, scrape_site
from core.dto import JobDTO, SiteDTO
from core.enums import SiteName
from core.exceptions import ScrapingError, ParsingError


@pytest.fixture
def dou_site():
    return SiteDTO(id=1, name=SiteName.DOU, url='https://jobs.dou.ua/', proxy=None)


@pytest.fixture
def djinni_site():
    return SiteDTO(id=2, name=SiteName.DJINNI, url='https://djinni.co/', proxy=None)


@pytest.fixture
def sample_job():
    return JobDTO(
        url='https://dou.ua/job/1',
        title='Python Developer',
        description='Great role',
        salary='$3000',
        company='TechCorp',
        city='Kyiv',
        published_at=datetime(2026, 3, 12, 8, 0, tzinfo=timezone.utc),
    )


class TestRunScraping:
    def test_dispatches_scrape_site_for_each_enabled_site(self, dou_site, djinni_site):
        with (
            patch('celery_app.tasks.RawResponsesRepository') as mock_raw,
            patch('celery_app.tasks.SitesRepository') as mock_sites,
            patch('celery_app.tasks.scrape_site') as mock_task,
        ):
            mock_raw.return_value.cleanup.return_value = 0
            mock_sites.return_value.get_enabled.return_value = [dou_site, djinni_site]

            run_scraping()

            assert mock_task.apply_async.call_count == 2
            mock_task.apply_async.assert_any_call(kwargs={'site_name': SiteName.DOU})
            mock_task.apply_async.assert_any_call(kwargs={'site_name': SiteName.DJINNI})

    def test_skips_site_not_in_registry(self, dou_site):
        unknown = SiteDTO(id=99, name=SiteName.DOU, url='', proxy=None)
        with (
            patch('celery_app.tasks.RawResponsesRepository'),
            patch('celery_app.tasks.SitesRepository') as mock_sites,
            patch('celery_app.tasks.scrape_site') as mock_task,
            patch('celery_app.tasks.SCRAPER_REGISTRY', {}),
        ):
            mock_sites.return_value.get_enabled.return_value = [unknown]

            run_scraping()

            mock_task.apply_async.assert_not_called()

    def test_dispatch_failure_does_not_stop_remaining_sites(self, dou_site, djinni_site):
        with (
            patch('celery_app.tasks.RawResponsesRepository'),
            patch('celery_app.tasks.SitesRepository') as mock_sites,
            patch('celery_app.tasks.scrape_site') as mock_task,
            patch('celery_app.tasks.tg'),
        ):
            mock_sites.return_value.get_enabled.return_value = [dou_site, djinni_site]
            mock_task.apply_async.side_effect = [Exception('broker down'), None]

            run_scraping()

            assert mock_task.apply_async.call_count == 2

    def test_cleans_up_old_raw_responses(self):
        with (
            patch('celery_app.tasks.RawResponsesRepository') as mock_raw,
            patch('celery_app.tasks.SitesRepository') as mock_sites,
            patch('celery_app.tasks.scrape_site'),
        ):
            mock_sites.return_value.get_enabled.return_value = []

            run_scraping()

            mock_raw.return_value.cleanup.assert_called_once_with(older_than_days=7)


class TestScrapeSite:
    def test_happy_path_completes_session(self, dou_site, sample_job):
        with (
            patch('celery_app.tasks.SitesRepository') as mock_sites,
            patch('celery_app.tasks.ScrapingSessionsRepository') as mock_sessions,
            patch('celery_app.tasks.RawResponsesRepository') as mock_raw,
            patch('celery_app.tasks.ScrapingController') as mock_ctrl_cls,
            patch('celery_app.tasks.tg'),
            patch('time.sleep'),
        ):
            mock_sites.return_value.get_by_name.return_value = dou_site
            mock_sessions.return_value.create.return_value = 42
            ctrl = mock_ctrl_cls.return_value
            ctrl.fetch.return_value = '<html>'
            ctrl.parse.return_value = [sample_job]
            ctrl.save.return_value = [sample_job]

            scrape_site(SiteName.DOU)

            mock_sessions.return_value.complete.assert_called_once_with(session_id=42, jobs_found=1)
            mock_raw.return_value.save.assert_called_once_with(session_id=42, content='<html>')

    def test_sends_telegram_notification_for_each_new_job(self, dou_site, sample_job):
        job2 = JobDTO(**{**sample_job.__dict__, 'url': 'https://dou.ua/job/2'})
        with (
            patch('celery_app.tasks.SitesRepository') as mock_sites,
            patch('celery_app.tasks.ScrapingSessionsRepository') as mock_sessions,
            patch('celery_app.tasks.RawResponsesRepository'),
            patch('celery_app.tasks.ScrapingController') as mock_ctrl_cls,
            patch('celery_app.tasks.tg') as mock_tg,
            patch('time.sleep'),
        ):
            mock_sites.return_value.get_by_name.return_value = dou_site
            mock_sessions.return_value.create.return_value = 1
            ctrl = mock_ctrl_cls.return_value
            ctrl.fetch.return_value = '<html>'
            ctrl.parse.return_value = [sample_job, job2]
            ctrl.save.return_value = [sample_job, job2]

            scrape_site(SiteName.DOU)

            assert mock_tg.send_report.call_count == 2

    def test_unknown_site_name_returns_early_without_creating_session(self):
        with (
            patch('celery_app.tasks.SitesRepository') as mock_sites,
            patch('celery_app.tasks.ScrapingSessionsRepository') as mock_sessions,
        ):
            mock_sites.return_value.get_by_name.return_value = None

            scrape_site('nonexistent')

            mock_sessions.return_value.create.assert_not_called()

    def test_scraping_error_fails_session_and_reraises(self, dou_site):
        with (
            patch('celery_app.tasks.SitesRepository') as mock_sites,
            patch('celery_app.tasks.ScrapingSessionsRepository') as mock_sessions,
            patch('celery_app.tasks.RawResponsesRepository'),
            patch('celery_app.tasks.ScrapingController') as mock_ctrl_cls,
            patch('celery_app.tasks.tg'),
        ):
            mock_sites.return_value.get_by_name.return_value = dou_site
            mock_sessions.return_value.create.return_value = 7
            mock_ctrl_cls.return_value.fetch.side_effect = ScrapingError('network error')

            with pytest.raises(ScrapingError):
                scrape_site(SiteName.DOU)

            mock_sessions.return_value.fail.assert_called_once_with(
                session_id=7, error='network error'
            )

    def test_parsing_error_fails_session_and_reraises(self, dou_site):
        with (
            patch('celery_app.tasks.SitesRepository') as mock_sites,
            patch('celery_app.tasks.ScrapingSessionsRepository') as mock_sessions,
            patch('celery_app.tasks.RawResponsesRepository') as mock_raw,
            patch('celery_app.tasks.ScrapingController') as mock_ctrl_cls,
            patch('celery_app.tasks.tg'),
        ):
            mock_sites.return_value.get_by_name.return_value = dou_site
            mock_sessions.return_value.create.return_value = 8
            mock_raw.return_value.save.return_value = None
            ctrl = mock_ctrl_cls.return_value
            ctrl.fetch.return_value = '<html>'
            ctrl.parse.side_effect = ParsingError('bad html')

            with pytest.raises(ParsingError):
                scrape_site(SiteName.DOU)

            mock_sessions.return_value.fail.assert_called_once_with(
                session_id=8, error='bad html'
            )

    def test_unexpected_exception_fails_session_and_reraises(self, dou_site):
        with (
            patch('celery_app.tasks.SitesRepository') as mock_sites,
            patch('celery_app.tasks.ScrapingSessionsRepository') as mock_sessions,
            patch('celery_app.tasks.RawResponsesRepository'),
            patch('celery_app.tasks.ScrapingController') as mock_ctrl_cls,
            patch('celery_app.tasks.tg'),
        ):
            mock_sites.return_value.get_by_name.return_value = dou_site
            mock_sessions.return_value.create.return_value = 9
            mock_ctrl_cls.return_value.fetch.side_effect = RuntimeError('unexpected')

            with pytest.raises(RuntimeError):
                scrape_site(SiteName.DOU)

            mock_sessions.return_value.fail.assert_called_once()

    def test_no_new_jobs_sends_no_telegram_notifications(self, dou_site):
        with (
            patch('celery_app.tasks.SitesRepository') as mock_sites,
            patch('celery_app.tasks.ScrapingSessionsRepository') as mock_sessions,
            patch('celery_app.tasks.RawResponsesRepository'),
            patch('celery_app.tasks.ScrapingController') as mock_ctrl_cls,
            patch('celery_app.tasks.tg') as mock_tg,
        ):
            mock_sites.return_value.get_by_name.return_value = dou_site
            mock_sessions.return_value.create.return_value = 1
            ctrl = mock_ctrl_cls.return_value
            ctrl.fetch.return_value = '<html>'
            ctrl.parse.return_value = []
            ctrl.save.return_value = []

            scrape_site(SiteName.DOU)

            mock_tg.send_report.assert_not_called()
            mock_sessions.return_value.complete.assert_called_once_with(session_id=1, jobs_found=0)
