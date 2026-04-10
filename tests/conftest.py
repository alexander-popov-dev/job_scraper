from datetime import datetime, timezone

import pytest

from core.dto import JobDTO, SiteDTO
from core.enums import SiteName


@pytest.fixture
def sample_job():
    return JobDTO(
        url='https://example.com/job/1',
        title='Python Developer',
        description='Great job opportunity',
        salary='$3000',
        company='TechCorp',
        city='Kyiv',
        published_at=datetime(2026, 3, 12, 8, 0, tzinfo=timezone.utc),
    )


@pytest.fixture
def sample_site():
    return SiteDTO(
        id=1,
        name=SiteName.DOU,
        url='https://jobs.dou.ua/vacancies/',
        proxy=None,
    )
