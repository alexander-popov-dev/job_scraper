import logging
from datetime import datetime, timezone

from dateutil.parser import parse
from parsel import Selector

from abstract.parser import BaseParser
from core.dto import JobDTO
from core.exceptions import ParsingError
from core.utils import kyiv_to_utc

logger = logging.getLogger(__name__)


class Parser(BaseParser):
    """Parses job listings from the Work.ua HTML response."""

    BASE_URL = 'https://www.work.ua'
    JOB_LIST_XPATH = '//div[@id="pjax-job-list"]//div[contains(@class, "job-link")]'
    URL_XPATH = './/h2//@href'
    TITLE_XPATH = './/h2/a/text()'
    DESCRIPTION_XPATH = './p/text()'
    COMPANY_XPATH = './/div[@class="mt-xs"]//span[@class="strong-600"]/text()'
    CITY_XPATH = './/div[@class="mt-xs"]/span[2]/text()'
    SALARY_XPATH = './div/span[@class="strong-600"]/text()'
    PUBLISHED_XPATH = './/time/@datetime'

    def parse(self, content: str) -> list[JobDTO]:
        """Extract job listings from the Work.ua HTML page."""
        tree = Selector(text=content)
        jobs = []

        for item in tree.xpath(self.JOB_LIST_XPATH):
            try:
                salary = item.xpath(self.SALARY_XPATH).get()
                published_raw = item.xpath(self.PUBLISHED_XPATH).get()

                jobs.append(JobDTO(
                    url=f'{self.BASE_URL}{item.xpath(self.URL_XPATH).get().strip()}',
                    title=item.xpath(self.TITLE_XPATH).get().strip(),
                    description=item.xpath(self.DESCRIPTION_XPATH).get().strip(),
                    salary=salary.strip() if salary else '-',
                    company=item.xpath(self.COMPANY_XPATH).get().strip(),
                    city=item.xpath(self.CITY_XPATH).get(),
                    published_at=(
                        kyiv_to_utc(parse(published_raw))
                        if published_raw
                        else None
                    ),
                ))
            except Exception as e:
                raise ParsingError(f'[WorkUA] Parsing error: {e}')

        return jobs
