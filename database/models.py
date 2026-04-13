from sqlalchemy import Column, BigInteger, String, DateTime, Text, Boolean, ForeignKey, Integer, UniqueConstraint, Index, text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Sites(Base):
    """Stores scraping target sites with their configuration."""

    __tablename__ = 'sites'

    id = Column(BigInteger, primary_key=True, unique=True)
    name = Column(String, nullable=False, unique=True)
    url = Column(Text, nullable=False)
    proxy = Column(Text, nullable=True)
    enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))

    sessions = relationship('ScrapingSession', back_populates='site')


class ScrapingSession(Base):
    """Tracks the lifecycle of a single scraping run for one site."""

    __tablename__ = 'scraping_sessions'

    id = Column(BigInteger, primary_key=True, unique=True)
    site_id = Column(BigInteger, ForeignKey('sites.id'), nullable=False)
    status = Column(String, nullable=False)
    jobs_found = Column(Integer, nullable=True)
    error = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=False)
    finished_at = Column(DateTime(timezone=True), nullable=True)

    site = relationship('Sites', back_populates='sessions')
    raw_response = relationship('RawResponse', back_populates='session', uselist=False)


class RawResponse(Base):
    """Stores the raw HTTP response body for debugging failed or unexpected parses."""

    __tablename__ = 'raw_responses'

    id = Column(BigInteger, primary_key=True, unique=True)
    session_id = Column(BigInteger, ForeignKey('scraping_sessions.id'), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)

    session = relationship('ScrapingSession', back_populates='raw_response')


class Jobs(Base):
    """Stores deduplicated job listings collected across all sites."""

    __tablename__ = 'jobs'
    __table_args__ = (
        UniqueConstraint('url', 'published_at', name='uq_jobs_url_published_at'),
        Index('uq_jobs_url_null_published_at', 'url', unique=True,
              postgresql_where=text('published_at IS NULL')),
    )

    id = Column(BigInteger, primary_key=True, unique=True)
    url = Column(Text, nullable=True)
    title = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    salary = Column(Text, nullable=True)
    city = Column(Text, nullable=True)
    company = Column(Text, nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
