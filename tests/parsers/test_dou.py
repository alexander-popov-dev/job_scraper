from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from core.exceptions import ParsingError
from sites.dou.parser import Parser

UTC = ZoneInfo('UTC')

VALID_HTML = """
<html><body>
<div id="vacancyListId">
  <ul>
    <li>
      <div class="title"><a href="https://jobs.dou.ua/vacancies/1/">Python Developer</a></div>
      <div class="sh-info">Build scalable backend services</div>
      <strong><a href="#">TechCorp</a></strong>
      <span class="cities">Київ</span>
      <span class="salary">$3 000</span>
      <div class="date">12 Березня 2026</div>
    </li>
    <li>
      <div class="title"><a href="https://jobs.dou.ua/vacancies/2/">Django Dev</a></div>
      <div class="sh-info">Backend role</div>
      <strong><a href="#">StartupCo</a></strong>
      <span class="cities">Львів</span>
      <div class="date">5 Лютого 2026</div>
    </li>
  </ul>
</div>
</body></html>
"""

EMPTY_HTML = '<html><body><div id="vacancyListId"><ul></ul></div></body></html>'


class TestDouParser:
    def setup_method(self):
        self.parser = Parser()

    def test_returns_correct_number_of_jobs(self):
        jobs = self.parser.parse(VALID_HTML)
        assert len(jobs) == 2

    def test_parses_url(self):
        jobs = self.parser.parse(VALID_HTML)
        assert jobs[0].url == 'https://jobs.dou.ua/vacancies/1/'

    def test_parses_title(self):
        jobs = self.parser.parse(VALID_HTML)
        assert jobs[0].title == 'Python Developer'

    def test_parses_description(self):
        jobs = self.parser.parse(VALID_HTML)
        assert jobs[0].description == 'Build scalable backend services'

    def test_parses_company(self):
        jobs = self.parser.parse(VALID_HTML)
        assert jobs[0].company == 'TechCorp'

    def test_parses_city(self):
        jobs = self.parser.parse(VALID_HTML)
        assert 'Київ' in jobs[0].city

    def test_parses_salary(self):
        jobs = self.parser.parse(VALID_HTML)
        assert jobs[0].salary == '$3 000'

    def test_salary_defaults_to_dash_when_missing(self):
        jobs = self.parser.parse(VALID_HTML)
        assert jobs[1].salary == '-'

    def test_published_at_is_utc_aware(self):
        jobs = self.parser.parse(VALID_HTML)
        assert jobs[0].published_at.utcoffset().total_seconds() == 0

    def test_published_at_correct_value(self):
        jobs = self.parser.parse(VALID_HTML)
        # "12 Березня 2026" → March 12 midnight Kyiv (UTC+2) → March 11 22:00 UTC
        assert jobs[0].published_at == datetime(2026, 3, 11, 22, 0, tzinfo=UTC)

    def test_ukrainian_month_february_parsed(self):
        jobs = self.parser.parse(VALID_HTML)
        # "5 Лютого 2026" → February 5 Kyiv → UTC
        assert jobs[1].published_at.month == 2
        assert jobs[1].published_at.day == 4  # Feb 5 midnight Kyiv → Feb 4 22:00 UTC

    def test_empty_list_returned_for_no_vacancies(self):
        assert self.parser.parse(EMPTY_HTML) == []

    def test_raises_parsing_error_on_malformed_item(self):
        bad_html = '<div id="vacancyListId"><ul><li>no title here</li></ul></div>'
        with pytest.raises(ParsingError, match=r'\[DOU\]'):
            self.parser.parse(bad_html)
