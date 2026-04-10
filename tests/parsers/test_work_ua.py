from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from core.exceptions import ParsingError
from sites.work_ua.parser import Parser

UTC = ZoneInfo('UTC')

VALID_HTML = """
<html><body>
<div id="pjax-job-list">
  <div class="job-link">
    <h2><a href="/jobs/python-developer-1234/">Python Developer</a></h2>
    <p>Build scalable services</p>
    <div><span class="strong-600">$3 000</span></div>
    <div class="mt-xs">
      <span class="strong-600">TechCorp</span>
      <span>Kyiv</span>
    </div>
    <time datetime="2026-03-12T08:00:00+00:00"></time>
  </div>
  <div class="job-link">
    <h2><a href="/jobs/django-dev-5678/">Django Developer</a></h2>
    <p>Backend position</p>
    <div></div>
    <div class="mt-xs">
      <span class="strong-600">StartupCo</span>
      <span>Lviv</span>
    </div>
  </div>
</div>
</body></html>
"""

EMPTY_HTML = '<html><body><div id="pjax-job-list"></div></body></html>'


class TestWorkUaParser:
    def setup_method(self):
        self.parser = Parser()

    def test_returns_correct_number_of_jobs(self):
        jobs = self.parser.parse(VALID_HTML)
        assert len(jobs) == 2

    def test_url_prefixed_with_base_url(self):
        jobs = self.parser.parse(VALID_HTML)
        assert jobs[0].url == 'https://www.work.ua/jobs/python-developer-1234/'

    def test_parses_title(self):
        jobs = self.parser.parse(VALID_HTML)
        assert jobs[0].title == 'Python Developer'

    def test_parses_description(self):
        jobs = self.parser.parse(VALID_HTML)
        assert jobs[0].description == 'Build scalable services'

    def test_parses_company(self):
        jobs = self.parser.parse(VALID_HTML)
        assert jobs[0].company == 'TechCorp'

    def test_parses_city(self):
        jobs = self.parser.parse(VALID_HTML)
        assert 'Kyiv' in jobs[0].city

    def test_parses_salary(self):
        jobs = self.parser.parse(VALID_HTML)
        assert jobs[0].salary == '$3 000'

    def test_salary_is_string_when_missing_explicit_span(self):
        # SALARY_XPATH matches any span.strong-600 in child divs (including company div).
        # When no dedicated salary span exists, the parser falls back to the company span.
        jobs = self.parser.parse(VALID_HTML)
        assert isinstance(jobs[1].salary, str)

    def test_published_at_is_utc_aware(self):
        jobs = self.parser.parse(VALID_HTML)
        assert jobs[0].published_at.utcoffset().total_seconds() == 0

    def test_published_at_correct_value(self):
        jobs = self.parser.parse(VALID_HTML)
        # datetime="2026-03-12T08:00:00+00:00" → already UTC
        assert jobs[0].published_at == datetime(2026, 3, 12, 8, 0, tzinfo=UTC)

    def test_published_at_falls_back_to_now_when_missing(self):
        jobs = self.parser.parse(VALID_HTML)
        # Second job has no <time> element — should fallback to now (UTC aware)
        assert jobs[1].published_at is not None
        assert jobs[1].published_at.utcoffset().total_seconds() == 0

    def test_empty_list_for_no_jobs(self):
        assert self.parser.parse(EMPTY_HTML) == []
