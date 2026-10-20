import logging
import re
from datetime import datetime, timedelta

from abstract.parser import BaseParser
from core.dto import JobDTO

logger = logging.getLogger(__name__)


class Parser(BaseParser):
    """Parses job listings from the LinkedIn response."""

    JOB_ID_PATTERN = re.compile(
        r'"jobId":"(\d+)"',
    )

    def parse(self, content: str) -> list[JobDTO]:
        """Parse job listings from the LinkedIn response."""

        content = self._normalize_content(content)

        job_ids = self._extract_job_ids(content)

        logger.info("Found %s LinkedIn jobs", len(job_ids))

        jobs: list[JobDTO] = []

        for job_id in job_ids:
            job = self._parse_job(
                content=content,
                job_id=job_id,
            )

            if job is not None:
                jobs.append(job)

        logger.info("Parsed %s LinkedIn jobs", len(jobs))

        return jobs

    def _parse_job(
        self,
        content: str,
        job_id: str,
    ) -> JobDTO | None:
        """Parse a single job listing."""

        chunk = self._get_job_chunk(
            content=content,
            job_id=job_id,
        )

        if chunk is None:
            logger.warning(
                "Job card not found: %s",
                job_id,
            )
            return None

        title = self._extract_title(chunk)

        if not title:
            logger.warning(
                "Job title not found: %s",
                job_id,
            )
            return None

        company, city = self._extract_company_and_city(chunk)

        return JobDTO(
            url=f"https://www.linkedin.com/jobs/view/{job_id}/",
            title=title,
            description="",
            salary="",
            company=company,
            city=city,
            published_at=self._extract_updated_at(chunk, job_id),
        )

    def _get_job_chunk(
            self,
            content: str,
            job_id: str,
    ) -> str | None:
        """Get the payload section belonging to a job card."""

        marker = f"JobSearchResultsPage_A11yLabel{job_id}"

        start = content.find(marker)

        if start == -1:
            return None

        next_marker = re.search(
            r"JobSearchResultsPage_A11yLabel(?!"
            + re.escape(job_id)
            + r")\d+",
            content[start + len(marker):],
        )

        if next_marker:
            end = start + len(marker) + next_marker.start()
        else:
            end = len(content)

        return content[start:end]

    @staticmethod
    def _extract_title(chunk: str) -> str | None:
        """Extract the job title."""

        match = re.search(
            r'"stringValue":"([^"]+)"',
            chunk,
        )

        if not match:
            return None

        title = match.group(1).strip()

        title = re.sub(
            r"\s+\(Verified job\)$",
            "",
            title,
        )

        return title

    @staticmethod
    def _extract_company_and_city(
        chunk: str,
    ) -> tuple[str, str]:
        """Extract company and location."""

        values = re.findall(
            r'"children":\["([^"]+)"\]',
            chunk,
        )

        values = [
            value.strip()
            for value in values
            if value.strip() not in {"$"}
        ]

        if len(values) < 2:
            return "", ""

        company = values[0]
        location = values[1]

        return company, location

    @staticmethod
    def _extract_updated_at(
            chunk: str,
            job_id: str,
    ) -> datetime:
        """Extract LinkedIn relative posting date."""

        match = re.search(
            r'Posted\s+(\d+)\s+'
            r'(minute|minutes|hour|hours|day|days|'
            r'week|weeks|month|months|year|years)'
            r'(?:\s+ago)?',
            chunk,
        )

        if not match:
            raise ValueError(
                f"Job posting date not found: {job_id}",
            )

        return Parser._parse_relative_date(
            f"{match.group(1)} {match.group(2)}",
        )

    @staticmethod
    def _parse_relative_date(value: str) -> datetime:
        """Convert LinkedIn relative date to datetime."""

        value = value.lower().strip()

        today = datetime.now().replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        if value in {"just now", "now"}:
            return today

        match = re.fullmatch(
            r"(\d+)\s+"
            r"(minute|minutes|hour|hours|day|days|"
            r"week|weeks|month|months|year|years)"
            r"(?:\s+ago)?",
            value,
        )

        if not match:
            raise ValueError(
                f"Unsupported LinkedIn relative date: {value!r}",
            )

        amount = int(match.group(1))
        unit = match.group(2)

        if unit.startswith(("minute", "hour")):
            return today

        if unit.startswith("day"):
            return today - timedelta(days=amount)

        if unit.startswith("week"):
            return today - timedelta(weeks=amount)

        if unit.startswith("month"):
            return today - timedelta(days=amount * 30)

        if unit.startswith("year"):
            return today - timedelta(days=amount * 365)

        raise ValueError(
            f"Unsupported LinkedIn date unit: {unit!r}",
        )

    @staticmethod
    def _extract_job_ids(content: str) -> list[str]:
        """Extract unique job IDs."""

        return list(
            dict.fromkeys(
                Parser.JOB_ID_PATTERN.findall(content),
            )
        )

    @staticmethod
    def _normalize_content(content: str) -> str:
        """Normalize escaped JSON strings."""

        return content.replace('\\"', '"')