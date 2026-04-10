from pathlib import Path
from decouple import Config, RepositoryEnv

_BASE = Path(__file__).parent
_env_file = _BASE / '.env.dev' if (_BASE / '.env.dev').exists() else _BASE / '.env'
config = Config(RepositoryEnv(_env_file))

DEBUG = config('DEBUG', cast=bool)

# In debug mode Celery executes tasks synchronously in the same process.
if DEBUG:
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True

POSTGRES_DB_CONNECTION_URL = config('POSTGRES_DB_CONNECTION_URL')
REDIS_DB_CONNECTION_URL = config('REDIS_DB_CONNECTION_URL')

CELERY_BROKER_URL = REDIS_DB_CONNECTION_URL
CELERY_RESULT_BACKEND = REDIS_DB_CONNECTION_URL
CELERY_RESULT_EXPIRES = 600

TELEGRAM_BOT = config('TELEGRAM_BOT')
TELEGRAM_CHANNEL = config('TELEGRAM_CHANNEL')
