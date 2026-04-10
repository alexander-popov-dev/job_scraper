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

    def parse(self, content: str) -> list[JobDTO]:
        """Extract job listings from the Djinni HTML page."""
        content = json.loads(content)
        jobs = []

        for item in content['data']:
            try:
                jobs.append(JobDTO(
                    url=item['url'],
                    title=item['title'],
                    description=item['summary'],
                    salary=f"{item.get('salaryMin', 0) } - {item.get('salaryMax', 0)} {item.get('salaryCurrency', '')}",
                    company=item['companyName'],
                    city=item.get('countryName', ''),
                    published_at=kyiv_to_utc(parse(item['createdAt'])),
                ))
            except Exception as e:
                raise ParsingError(f'[TheJob] Parsing error: {e}')

        return jobs

    @staticmethod
    def _get_or_default(value: str | None, default: str = '-') -> str:
        """Return the stripped value or a default string if None."""
        return value.strip() if value else default
