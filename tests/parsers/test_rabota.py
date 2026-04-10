import json
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from core.exceptions import ParsingError
from sites.rabota.parser import Parser

UTC = ZoneInfo('UTC')


def make_payload(items: list) -> str:
    return json.dumps({'data': {'publishedVacancies': {'items': items}}})


ACTIVE_ITEM = {
    'id': 456,
    'title': 'Python Developer',
    'description': 'Build scalable services',
    'isActive': True,
    'company': {'id': 10, 'name': 'TechCorp'},
    'salary': {'amountFrom': 1000, 'amountTo': 3000},
    'city': {'name': 'Kyiv'},
    'sortDate': '2026-03-12T10:00:00+02:00',
}

INACTIVE_ITEM = {**ACTIVE_ITEM, 'id': 457, 'isActive': False}
NO_SALARY_ITEM = {**ACTIVE_ITEM, 'id': 458, 'salary': {}}
NO_COMPANY_ITEM = {**ACTIVE_ITEM, 'id': 459, 'company': None}


class TestRabotaParser:
    def setup_method(self):
        self.parser = Parser()

    def test_parses_active_job(self):
        jobs = self.parser.parse(make_payload([ACTIVE_ITEM]))
        assert len(jobs) == 1

    def test_skips_inactive_jobs(self):
        jobs = self.parser.parse(make_payload([ACTIVE_ITEM, INACTIVE_ITEM]))
        assert len(jobs) == 1

    def test_parses_url(self):
        jobs = self.parser.parse(make_payload([ACTIVE_ITEM]))
        assert jobs[0].url == 'https://robota.ua/company10/vacancy456'

    def test_parses_title(self):
        jobs = self.parser.parse(make_payload([ACTIVE_ITEM]))
        assert jobs[0].title == 'Python Developer'

    def test_parses_description(self):
        jobs = self.parser.parse(make_payload([ACTIVE_ITEM]))
        assert jobs[0].description == 'Build scalable services'

    def test_parses_company(self):
        jobs = self.parser.parse(make_payload([ACTIVE_ITEM]))
        assert jobs[0].company == 'TechCorp'

    def test_company_defaults_to_dash_when_none(self):
        jobs = self.parser.parse(make_payload([NO_COMPANY_ITEM]))
        assert jobs[0].company == '-'

    def test_parses_city(self):
        jobs = self.parser.parse(make_payload([ACTIVE_ITEM]))
        assert jobs[0].city == 'Kyiv'

    def test_parses_salary_range(self):
        jobs = self.parser.parse(make_payload([ACTIVE_ITEM]))
        assert jobs[0].salary == '1000 - 3000'

    def test_salary_defaults_to_dash_when_missing(self):
        jobs = self.parser.parse(make_payload([NO_SALARY_ITEM]))
        assert jobs[0].salary == '-'

    def test_published_at_is_utc_aware(self):
        jobs = self.parser.parse(make_payload([ACTIVE_ITEM]))
        assert jobs[0].published_at.utcoffset().total_seconds() == 0

    def test_published_at_correct_value(self):
        jobs = self.parser.parse(make_payload([ACTIVE_ITEM]))
        # 10:00 UTC+2 → 08:00 UTC
        assert jobs[0].published_at == datetime(2026, 3, 12, 8, 0, tzinfo=UTC)

    def test_empty_list_for_no_items(self):
        assert self.parser.parse(make_payload([])) == []

    def test_raises_parsing_error_on_invalid_json(self):
        with pytest.raises(Exception):
            self.parser.parse('not json')

    def test_raises_parsing_error_on_missing_field(self):
        bad_item = {'id': 1, 'isActive': True}  # missing required fields
        with pytest.raises(ParsingError, match=r'\[RobotaUA\]'):
            self.parser.parse(make_payload([bad_item]))
