import json
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from core.exceptions import ParsingError
from sites.the_job.parser import Parser

UTC = ZoneInfo('UTC')


def make_payload(items: list) -> str:
    return json.dumps({'data': items})


VALID_ITEM = {
    'url': 'https://thejob.com/vacancies/1',
    'title': 'Python Developer',
    'summary': 'Build scalable services',
    'salaryMin': 1000,
    'salaryMax': 3000,
    'salaryCurrency': 'USD',
    'companyName': 'TechCorp',
    'countryName': 'Ukraine',
    'createdAt': '2026-03-12T10:00:00+02:00',
}

NO_SALARY_ITEM = {
    **VALID_ITEM,
    'url': 'https://thejob.com/vacancies/2',
    'salaryMin': 0,
    'salaryMax': 0,
    'salaryCurrency': '',
}


class TestTheJobParser:
    def setup_method(self):
        self.parser = Parser()

    def test_returns_correct_number_of_jobs(self):
        jobs = self.parser.parse(make_payload([VALID_ITEM]))
        assert len(jobs) == 1

    def test_parses_url(self):
        jobs = self.parser.parse(make_payload([VALID_ITEM]))
        assert jobs[0].url == 'https://thejob.com/vacancies/1'

    def test_parses_title(self):
        jobs = self.parser.parse(make_payload([VALID_ITEM]))
        assert jobs[0].title == 'Python Developer'

    def test_parses_description(self):
        jobs = self.parser.parse(make_payload([VALID_ITEM]))
        assert jobs[0].description == 'Build scalable services'

    def test_parses_company(self):
        jobs = self.parser.parse(make_payload([VALID_ITEM]))
        assert jobs[0].company == 'TechCorp'

    def test_parses_city(self):
        jobs = self.parser.parse(make_payload([VALID_ITEM]))
        assert jobs[0].city == 'Ukraine'

    def test_parses_salary(self):
        jobs = self.parser.parse(make_payload([VALID_ITEM]))
        assert jobs[0].salary == '1000 - 3000 USD'

    def test_published_at_is_utc_aware(self):
        jobs = self.parser.parse(make_payload([VALID_ITEM]))
        assert jobs[0].published_at.utcoffset().total_seconds() == 0

    def test_published_at_correct_value(self):
        jobs = self.parser.parse(make_payload([VALID_ITEM]))
        # 10:00 UTC+2 → 08:00 UTC
        assert jobs[0].published_at == datetime(2026, 3, 12, 8, 0, tzinfo=UTC)

    def test_empty_list_for_no_items(self):
        assert self.parser.parse(make_payload([])) == []

    def test_raises_parsing_error_on_missing_field(self):
        bad_item = {'title': 'No URL here'}
        with pytest.raises(ParsingError, match=r'\[TheJob\]'):
            self.parser.parse(make_payload([bad_item]))

    def test_raises_on_invalid_json(self):
        with pytest.raises(Exception):
            self.parser.parse('not json')

    def test_multiple_jobs_parsed(self):
        item2 = {**VALID_ITEM, 'url': 'https://thejob.com/vacancies/2', 'title': 'Django Dev'}
        jobs = self.parser.parse(make_payload([VALID_ITEM, item2]))
        assert len(jobs) == 2
        assert jobs[1].title == 'Django Dev'
