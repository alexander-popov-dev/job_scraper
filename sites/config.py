"""Registry mapping each SiteName to its concrete scraper, parser, and repository."""

from abstract.dto import ScraperConfigDTO
from core.enums import SiteName
from database.repository import JobsRepository
from sites import djinni, dou, rabota, work_ua, the_job

SCRAPER_REGISTRY: dict[SiteName, ScraperConfigDTO] = {
    SiteName.DOU: ScraperConfigDTO(
        site=SiteName.DOU,
        scraper=dou.Scraper,
        parser=dou.Parser,
        repo=JobsRepository,
    ),
    SiteName.DJINNI: ScraperConfigDTO(
        site=SiteName.DJINNI,
        scraper=djinni.Scraper,
        parser=djinni.Parser,
        repo=JobsRepository,
    ),
    SiteName.ROBOTA_UA: ScraperConfigDTO(
        site=SiteName.ROBOTA_UA,
        scraper=rabota.Scraper,
        parser=rabota.Parser,
        repo=JobsRepository,
    ),
    SiteName.WORK_UA: ScraperConfigDTO(
        site=SiteName.WORK_UA,
        scraper=work_ua.Scraper,
        parser=work_ua.Parser,
        repo=JobsRepository,
    ),
    SiteName.THE_JOB: ScraperConfigDTO(
        site=SiteName.THE_JOB,
        scraper=the_job.Scraper,
        parser=the_job.Parser,
        repo=JobsRepository,
    ),
}
