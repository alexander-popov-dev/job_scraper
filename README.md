# Work Scraper

Automated job scraper for Ukrainian job boards with Telegram notifications for new listings.

## What it does

Every 5 minutes Celery Beat triggers a task that:
1. Fetches the list of enabled sites from the database
2. Dispatches a separate `scrape_site` task for each site
3. Parses job listings and saves new ones to PostgreSQL
4. Sends each new job to a Telegram channel in MarkdownV2 format

Duplicates are filtered at the database level via partial unique indexes (`url + published_at`).

## Supported sites

| Site | Directory |
|------|-----------|
| DOU | `sites/dou/` |
| Djinni | `sites/djinni/` |
| Rabota.ua | `sites/rabota/` |
| Work.ua | `sites/work_ua/` |
| The Job | `sites/the_job/` |

## Stack

- **Python 3.11**
- **Celery 5** — task queues (`main`, `scraping`)
- **Redis** — broker and result backend
- **PostgreSQL** — storage for jobs, sessions, raw responses
- **SQLAlchemy 2 + Alembic** — ORM and migrations
- **Requests + Parsel** — HTTP client and XPath/CSS parsing
- **Telegram Bot API** — notifications

## Project structure

```
work_scraper/
├── abstract/           # Base classes (BaseScraper, BaseParser, BaseRepository)
├── celery_app/         # Celery config and tasks (tasks.py)
├── clients/            # HTTP client (RequestsClient, 30s timeout)
├── core/
│   ├── dto.py          # ResponseDTO, SiteDTO, JobDTO
│   ├── enums.py        # CeleryQueue, SiteName, SessionStatus
│   ├── exceptions.py   # ScrapingError, ParsingError, HTTPError
│   └── utils.py        # kyiv_to_utc(), escape_markdown()
├── database/
│   ├── models.py       # SQLAlchemy models
│   └── repository.py   # Jobs, Sites, ScrapingSessions, RawResponses repositories
├── migrations/         # Alembic migrations
├── notifications/
│   └── telegram.py     # TelegramManager (MarkdownV2, retry on 429)
├── services/
│   └── controller.py   # ScrapingController (fetch → parse → save)
├── sites/              # Site-specific scrapers and parsers
├── settings.py         # Config via python-decouple
├── Dockerfile
└── docker-compose.yaml
```

## Configuration

Create a `.env` file in the project root:

```env
DEBUG=False
POSTGRES_DB_CONNECTION_URL=postgresql://user:password@host:5432/dbname
REDIS_DB_CONNECTION_URL=redis://:password@host:6379/0
TELEGRAM_BOT=<bot_token>
TELEGRAM_CHANNEL=<channel_id>
```

> For local development you can use `.env.dev` — it takes precedence over `.env`.  
> When `DEBUG=True`, Celery tasks run synchronously in the same process (`TASK_ALWAYS_EAGER`).

## Running with Docker

```bash
docker compose up --build
```

Starts three containers:

| Container | Command |
|-----------|---------|
| `job-scraper-migrate` | `alembic upgrade head` (runs once, then exits) |
| `job-scraper-worker` | Celery worker (queues `main`, `scraping`) |
| `job-scraper-beat` | Celery Beat (task scheduler) |

## Running locally

```bash
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Worker (separate terminal)
celery -A celery_app.config worker --loglevel=info -Q main,scraping

# Beat (separate terminal)
celery -A celery_app.config beat --loglevel=info
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Task architecture

```
Celery Beat
    └── run_scraping()              ← every 5 minutes
            └── scrape_site(site_name)   ← per enabled site
                    ├── fetch()      → saves raw HTML to RawResponses (7-day TTL)
                    ├── parse()      → returns list of JobDTO
                    ├── save()       → INSERT ... ON CONFLICT DO NOTHING
                    └── send_message() → Telegram for each new job
```

### Retry logic

- **Scraper**: up to 5 attempts with exponential backoff (15s → 30s → 60s → 120s → 240s)
- **Telegram**: up to 3 attempts on HTTP 429, respecting `retry_after` from the response

## Database

| Table | Purpose |
|-------|---------|
| `sites` | Site configuration (url, proxy, enabled flag) |
| `jobs` | Job listings, unique on `(url, published_at)` |
| `scraping_sessions` | Run log per site (status, new job count, errors) |
| `raw_responses` | Raw HTML responses for debugging (auto-cleaned after 7 days) |

## Adding a new site

1. Create a directory `sites/<site_name>/`
2. Implement a scraper (extend `BaseScraper`)
3. Implement a parser (extend `BaseParser`)
4. Implement a repository (extend `BaseJobsRepository`) or reuse `JobsRepository`
5. Register a `ScraperConfigDTO` in `sites/config.py`
6. Add a record to the `sites` table via an Alembic migration or manually