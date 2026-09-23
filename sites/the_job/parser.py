import json
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

    BASE_URL = 'https://thejob.tech/jobs'
    JOB_LIST_XPATH = '//script[@id="__NUXT_DATA__"]/text()'

    def parse(self, content: str) -> list[JobDTO]:
        """Extract job listings from the Djinni HTML page."""

        tree = Selector(text=content)
        jobs = []
        raw_data = tree.xpath(self.JOB_LIST_XPATH).get().strip()
        json_data = json.loads(raw_data)

        start_data_index = None

        for i in json_data:
            if isinstance(i, dict) and i.get('data') and i.get('pagination'):
                start_data_index = i['data']
                break

        for i in json_data[start_data_index]:
            item = json_data[i]

            try:
                jobs.append(JobDTO(
                    url=f'{self.BASE_URL}/{json_data[item["slug"]]}',
                    title=json_data[item['title']],
                    description=json_data[item['summary']],
                    salary='-',
                    company=json_data[item['companyName']],
                    city=json_data[item['countryName']],
                    published_at=kyiv_to_utc(parse(json_data[item['updatedAt']])),
                ))
            except Exception as e:
                raise ParsingError(f'[TheJob] Parsing error: {e}')

        return jobs

    @staticmethod
    def _get_or_default(value: str | None, default: str = '-') -> str:
        """Return the stripped value or a default string if None."""
        return value.strip() if value else default
