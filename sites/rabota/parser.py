import json
import logging

from dateutil.parser import parse

from abstract.parser import BaseParser
from core.dto import JobDTO
from core.exceptions import ParsingError
from core.utils import kyiv_to_utc

logger = logging.getLogger(__name__)


class Parser(BaseParser):
    """Parses job listings from the Robota.ua GraphQL JSON response."""

    BASE_URL = 'https://robota.ua/company{company_id}/vacancy{vacancy_id}'

    def parse(self, content: str) -> list[JobDTO]:
        """Extract job listings from the Robota.ua GraphQL response."""
        json_data = json.loads(content)
        jobs = []

        for item in json_data['data']['publishedVacancies']['items']:
            try:
                if not item.get('isActive'):
                    continue

                vacancy_id = item['id']
                company = item.get('company') or {}
                company_id = company.get('id', 0)

                salary_data = item.get('salary') or {}
                amount_from = salary_data.get('amountFrom', 0)
                amount_to = salary_data.get('amountTo', 0)
                salary = f'{amount_from} - {amount_to}' if amount_from or amount_to else '-'

                jobs.append(JobDTO(
                    url=self.BASE_URL.format(company_id=company_id, vacancy_id=vacancy_id),
                    title=item['title'],
                    description=item['description'],
                    salary=salary,
                    company=company.get('name', '-'),
                    city=item['city']['name'],
                    published_at=kyiv_to_utc(parse(item['sortDate'])),
                ))
            except Exception as e:
                raise ParsingError(f'[RobotaUA] Parsing error: {e}')

        return jobs
