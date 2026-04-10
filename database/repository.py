from datetime import datetime, timezone, timedelta

from sqlalchemy import create_engine, QueuePool
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import scoped_session, sessionmaker

import settings
from abstract.repository import BaseJobsRepository, BaseSitesRepository, BaseSessionsRepository, BaseRawRepository
from core.dto import SiteDTO, JobDTO
from core.enums import SiteName, SessionStatus
from database.models import Base, Jobs, Sites, ScrapingSession, RawResponse


class BaseRepository:
    """Shared SQLAlchemy connection pool used by all repositories."""

    _engine = None
    _SessionLocal = None

    @classmethod
    def initialize(cls) -> None:
        """Create the database engine and session factory on first use."""
        if BaseRepository._engine is None:
            BaseRepository._engine = create_engine(
                settings.POSTGRES_DB_CONNECTION_URL,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=5,
                pool_timeout=30,
                echo=False,
            )
            BaseRepository._SessionLocal = scoped_session(
                sessionmaker(bind=BaseRepository._engine, expire_on_commit=False)
            )

    @classmethod
    def _get_session(cls):
        """Return a database session, initializing the engine if needed."""
        if BaseRepository._SessionLocal is None:
            cls.initialize()
        return BaseRepository._SessionLocal()


class JobsRepository(BaseRepository, BaseJobsRepository):
    """PostgreSQL repository for job listings."""

    def save(self, jobs: list[JobDTO]) -> list[JobDTO]:
        """Insert new jobs, skip duplicates by URL, and return the inserted rows."""
        now = datetime.now(timezone.utc)

        values = [
            {
                'url': dto.url,
                'title': dto.title,
                'description': dto.description,
                'salary': dto.salary,
                'company': dto.company,
                'city': dto.city,
                'published_at': dto.published_at,
                'created_at': now,
                'updated_at': now,
            }
            for dto in jobs
        ]

        with self._get_session() as db:
            stmt = (
                insert(Jobs)
                .values(values)
                .on_conflict_do_nothing(index_elements=['url'])
                .returning(Jobs)
            )
            result = db.execute(stmt)
            db.commit()

            return [
                JobDTO(
                    url=row.url,
                    title=row.title,
                    description=row.description,
                    salary=row.salary,
                    company=row.company,
                    city=row.city,
                    published_at=row.published_at,
                )
                for row in result.scalars().all()
            ]


class SitesRepository(BaseRepository, BaseSitesRepository):
    """PostgreSQL repository for scraping site configuration."""

    def get_enabled(self) -> list[SiteDTO]:
        """Return all enabled sites as DTOs including proxy and ID."""
        with self._get_session() as db:
            rows = db.query(Sites).filter(Sites.enabled == True).all()
            return [
                SiteDTO(id=row.id, name=SiteName(row.name), url=row.url, proxy=row.proxy)
                for row in rows
            ]

    def get_by_name(self, name: str) -> SiteDTO | None:
        """Return a single site DTO by name, or None if not found."""
        with self._get_session() as db:
            row = db.query(Sites).filter(Sites.name == name).first()
            if row is None:
                return None
            return SiteDTO(id=row.id, name=SiteName(row.name), url=row.url, proxy=row.proxy)


class ScrapingSessionsRepository(BaseRepository, BaseSessionsRepository):
    """PostgreSQL repository for scraping session lifecycle tracking."""

    def create(self, site_id: int) -> int:
        """Open a new session for the given site and return its ID."""
        with self._get_session() as db:
            session = ScrapingSession(
                site_id=site_id,
                status=SessionStatus.STARTED,
                started_at=datetime.now(timezone.utc),
            )
            db.add(session)
            db.commit()
            return session.id

    def complete(self, session_id: int, jobs_found: int) -> None:
        """Close the session with a completed status and the count of new jobs."""
        with self._get_session() as db:
            db.query(ScrapingSession).filter(ScrapingSession.id == session_id).update({
                'status': SessionStatus.COMPLETED,
                'jobs_found': jobs_found,
                'finished_at': datetime.now(timezone.utc),
            })
            db.commit()

    def fail(self, session_id: int, error: str) -> None:
        """Close the session with a failed status and record the error message."""
        with self._get_session() as db:
            db.query(ScrapingSession).filter(ScrapingSession.id == session_id).update({
                'status': SessionStatus.FAILED,
                'error': error,
                'finished_at': datetime.now(timezone.utc),
            })
            db.commit()


class RawResponsesRepository(BaseRepository, BaseRawRepository):
    """PostgreSQL repository for raw HTTP responses used in debugging."""

    def save(self, session_id: int, content: str) -> None:
        """Persist the raw response body linked to the given session."""
        with self._get_session() as db:
            db.add(RawResponse(
                session_id=session_id,
                content=content,
                created_at=datetime.now(timezone.utc),
            ))
            db.commit()

    def cleanup(self, older_than_days: int = 7) -> int:
        """Delete raw responses older than the given number of days and return the count."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=older_than_days)
        with self._get_session() as db:
            deleted = db.query(RawResponse).filter(RawResponse.created_at < cutoff).delete()
            db.commit()
            return deleted
