import logging
logging.basicConfig(level=logging.INFO)

from celery_app.tasks import scrape_site, run_scraping
from core.enums import SiteName
from database.repository import SitesRepository
from sites.config import SCRAPER_REGISTRY

if __name__ == '__main__':
    # run_scraping.apply_async()
    enabled_sites = SitesRepository().get_enabled()
    for site in enabled_sites:
        if site.name == SiteName.DOU:
            scrape_site.apply_async(kwargs={'site_name': site.name})
            break
