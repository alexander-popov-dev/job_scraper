import logging
from datetime import datetime

from dateutil.parser import parse
from parsel import Selector

from abstract.parser import BaseParser
from core.dto import JobDTO
from core.exceptions import ParsingError
from core.utils import kyiv_to_utc
from sites.dou.months_mapping import UKR_TO_ENG

logger = logging.getLogger(__name__)


class Parser(BaseParser):
    """Parses job listings from the DOU HTML response."""

    JOB_LIST_XPATH = '//div[@id="vacancyListId"]//li'
    URL_XPATH = './/div[@class="title"]/a/@href'
    TITLE_XPATH = './/div[@class="title"]/a/text()'
    DESCRIPTION_XPATH = './/div[@class="sh-info"]/text()'
    COMPANY_XPATH = './/strong/a/text()'
    CITY_XPATH = './/span[@class="cities"]/text()'
    SALARY_XPATH = './/span[@class="salary"]/text()'
    PUBLISHED_XPATH = './/div[@class="date"]/text()'

    def parse(self, content: str) -> list[JobDTO]:
        """Extract job listings from the DOU HTML page."""
        tree = Selector(text=content)
        jobs = []

        for item in tree.xpath(self.JOB_LIST_XPATH):
            try:
                salary = item.xpath(self.SALARY_XPATH).get()
                jobs.append(JobDTO(
                    url=item.xpath(self.URL_XPATH).get().strip(),
                    title=item.xpath(self.TITLE_XPATH).get().strip(),
                    description=item.xpath(self.DESCRIPTION_XPATH).get().strip(),
                    salary=salary.strip() if salary else '-',
                    company=item.xpath(self.COMPANY_XPATH).get().strip(),
                    city=item.xpath(self.CITY_XPATH).get(),
                    published_at=self._parse_date(item.xpath(self.PUBLISHED_XPATH).get()),
                ))
            except Exception as e:
                raise ParsingError(f'[DOU] Parsing error: {e}')

        return jobs

    def _parse_date(self, date_str: str) -> datetime:
        """Translate a Ukrainian month name to English and parse the date string."""
        date_lower = date_str.lower()
        for ukr, eng in UKR_TO_ENG.items():
            if ukr.lower() in date_lower:
                date_str = date_lower.replace(ukr.lower(), eng)
                break
        return kyiv_to_utc(parse(date_str))
