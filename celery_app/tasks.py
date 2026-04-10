import logging
import time
from datetime import datetime, timezone

from celery import shared_task

from core.exceptions import ScrapingError, ParsingError
from core.utils import escape_markdown
from database.repository import SitesRepository, ScrapingSessionsRepository, RawResponsesRepository
from notifications.telegram import TelegramManager
from services.controller import ScrapingController
from sites.config import SCRAPER_REGISTRY

logger = logging.getLogger(__name__)
tg = TelegramManager()

RAW_RESPONSE_RETENTION_DAYS = 7


@shared_task
def run_scraping() -> None:
    """Trigger scraping for all enabled sites and clean up old raw responses."""
    RawResponsesRepository().cleanup(older_than_days=RAW_RESPONSE_RETENTION_DAYS)

    enabled_sites = SitesRepository().get_enabled()
    for site in enabled_sites:
        if site.name not in SCRAPER_REGISTRY:
            logger.warning(f'No scraper registered for site: {site.name}')
            continue
        try:
            scrape_site.apply_async(kwargs={'site_name': site.name})
            logger.info(f'Dispatched scrape_site for {site.name}')
        except Exception as e:
            logger.error(f'Failed to dispatch scrape_site for {site.name}: {e}')
            tg.send_report(message=escape_markdown(str(e)))


@shared_task
def scrape_site(site_name: str) -> None:
    """Run the full scraping pipeline for a single site with session tracking."""
    sites_repo = SitesRepository()
    sessions_repo = ScrapingSessionsRepository()
    raw_repo = RawResponsesRepository()

    site = sites_repo.get_by_name(site_name)
    if site is None:
        logger.error(f'Site not found in DB: {site_name}')
        return

    config = SCRAPER_REGISTRY[site.name]
    session_id = sessions_repo.create(site_id=site.id)
    try:
        logger.info(f'Scraping {site.name} started')

        controller = ScrapingController(config=config, proxy=site.proxy)
        raw = controller.fetch()
        raw_repo.save(session_id=session_id, content=raw)

        jobs = controller.parse(raw)
        new_jobs = controller.save(jobs)
        sessions_repo.complete(session_id=session_id, jobs_found=len(new_jobs))

        for job in new_jobs:
            age = str(datetime.now(tz=timezone.utc) - job.published_at)
            message = (
                f'*{escape_markdown(site.name)}*\n\n'
                f'*{escape_markdown(job.title)}*\n'
                f'{escape_markdown(job.company)} \\| {escape_markdown(job.city)} \\| {escape_markdown(job.salary)}\n\n'
                f'{escape_markdown(job.description[:3000])}\n\n'
                f'Published: {escape_markdown(age)} ago\n'
                f'{escape_markdown(job.url)}'
            )
            tg.send_report(message=message)
            time.sleep(1)

        logger.info(f'Scraping {site.name} finished: {len(new_jobs)} new jobs')

    except (ScrapingError, ParsingError) as e:
        sessions_repo.fail(session_id=session_id, error=str(e))
        logger.error(f'[{site.name}] {e}')
        tg.send_report(message=f'\\[{escape_markdown(site.name)}\\] {escape_markdown(str(e))}')
        raise

    except Exception as e:
        sessions_repo.fail(session_id=session_id, error=str(e))
        logger.error(f'[{site.name}] Unexpected error: {e}')
        tg.send_report(message=f'\\[{escape_markdown(site.name)}\\] {escape_markdown(str(e))}')
        raise
