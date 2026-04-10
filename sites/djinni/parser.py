import logging

from dateutil.parser import parse
from parsel import Selector

from abstract.parser import BaseParser
from core.dto import JobDTO
from core.exceptions import ParsingError
from core.utils import kyiv_to_utc

logger = logging.getLogger(__name__)


class Parser(BaseParser):
    """Parses job listings from the Djinni HTML response."""

    BASE_URL = 'https://djinni.co'
    JOB_LIST_XPATH = '//main[@id="jobs_main"]//div[starts-with(@id, "job-item")]'
    URL_XPATH = './/a[starts-with(@class, "job_item")]/@href'
    TITLE_XPATH = './/h2/text()'
    DESCRIPTION_XPATH = './/span[@class="js-truncated-text"]/text()'
    COMPANY_XPATH = './/span[@class="small text-gray-800 opacity-75 font-weight-500"]/text()'
    CITY_XPATH = './/span[@class="location-text"]//text()'
    SALARY_XPATH = './/span[@class="text-success text-nowrap"]//text()'
    PUBLISHED_XPATH = './/div[@class="d-flex align-items-center gap-1 fs-5"]/span[@data-toggle="tooltip"]/@title'

    def parse(self, content: str) -> list[JobDTO]:
        """Extract job listings from the Djinni HTML page."""
        tree = Selector(text=content)
        jobs = []

        for item in tree.xpath(self.JOB_LIST_XPATH):
            try:
                jobs.append(JobDTO(
                    url=f'{self.BASE_URL}{item.xpath(self.URL_XPATH).get().strip()}',
                    title=item.xpath(self.TITLE_XPATH).get().strip(),
                    description=self._parse_description(item),
                    salary=self._get_or_default(item.xpath(self.SALARY_XPATH).get()),
                    company=self._get_or_default(item.xpath(self.COMPANY_XPATH).get()),
                    city=item.xpath(self.CITY_XPATH).get(),
                    published_at=kyiv_to_utc(
                        parse(item.xpath(self.PUBLISHED_XPATH).get(), dayfirst=True)
                    ),
                ))
            except Exception as e:
                raise ParsingError(f'[Djinni] Parsing error: {e}')

        return jobs

    def _parse_description(self, item: Selector) -> str:
        """Extract and format the job description as plain text."""
        parts = []
        for el in item.xpath(self.DESCRIPTION_XPATH).xpath('.//p | .//li'):
            text = ' '.join(' '.join(el.xpath('.//text()').getall()).split())
            if text:
                parts.append(f'• {text}' if el.root.tag == 'li' else text)
        return '\n'.join(parts).strip()

    @staticmethod
    def _get_or_default(value: str | None, default: str = '-') -> str:
        """Return the stripped value or a default string if None."""
        return value.strip() if value else default
