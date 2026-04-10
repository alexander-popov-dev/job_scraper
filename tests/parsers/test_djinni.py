from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from core.exceptions import ParsingError
from sites.djinni.parser import Parser

UTC = ZoneInfo('UTC')

VALID_HTML = """
<html><body>
<main id="jobs_main">
  <div id="job-item-123">
    <a class="job_item_link" href="/jobs/python-dev-123">link</a>
    <h2>Python Developer</h2>
    <span class="js-truncated-text"><p>Build scalable services</p><li>Remote work</li></span>
    <span class="small text-gray-800 opacity-75 font-weight-500">TechCorp</span>
    <span class="location-text">Kyiv</span>
    <span class="text-success text-nowrap">$3 000</span>
    <div class="d-flex align-items-center gap-1 fs-5 text-secondary">
      <span data-toggle="tooltip" title="12/03/2026">12 Mar</span>
    </div>
  </div>
  <div id="job-item-456">
    <a class="job_item_link" href="/jobs/django-dev-456">link</a>
    <h2>Django Developer</h2>
    <span class="js-truncated-text"></span>
    <span class="location-text">Remote</span>
    <div class="d-flex align-items-center gap-1 fs-5 text-secondary">
      <span data-toggle="tooltip" title="01/03/2026">01 Mar</span>
    </div>
  </div>
</main>
</body></html>
"""

EMPTY_HTML = '<html><body><main id="jobs_main"></main></body></html>'


class TestDjinniParser:
    def setup_method(self):
        self.parser = Parser()

    def test_returns_correct_number_of_jobs(self):
        jobs = self.parser.parse(VALID_HTML)
        assert len(jobs) == 2

    def test_url_prefixed_with_base_url(self):
        jobs = self.parser.parse(VALID_HTML)
        assert jobs[0].url == 'https://djinni.co/jobs/python-dev-123'

    def test_parses_title(self):
        jobs = self.parser.parse(VALID_HTML)
        assert jobs[0].title == 'Python Developer'

    def test_parses_company(self):
        jobs = self.parser.parse(VALID_HTML)
        assert jobs[0].company == 'TechCorp'

    def test_company_defaults_to_dash_when_missing(self):
        jobs = self.parser.parse(VALID_HTML)
        assert jobs[1].company == '-'

    def test_parses_city(self):
        jobs = self.parser.parse(VALID_HTML)
        assert 'Kyiv' in jobs[0].city

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
        # "12/03/2026" dayfirst=True → March 12 midnight Kyiv (UTC+2) → March 11 22:00 UTC
        assert jobs[0].published_at == datetime(2026, 3, 11, 22, 0, tzinfo=UTC)

    def test_empty_list_for_no_jobs(self):
        assert self.parser.parse(EMPTY_HTML) == []
