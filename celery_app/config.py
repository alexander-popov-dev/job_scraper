from celery import Celery
from kombu import Queue

from core.enums import CeleryQueue

app = Celery('job_scraper', include=['celery_app.tasks'])
app.config_from_object('settings', namespace='CELERY')

app.conf.task_queues = (Queue(CeleryQueue.MAIN), Queue(CeleryQueue.SCRAPING))
app.conf.task_routes = {
    'celery_app.tasks.run_scraping': {'queue': CeleryQueue.MAIN},
    'celery_app.tasks.scrape_site': {'queue': CeleryQueue.SCRAPING},
}

app.conf.beat_schedule = {
    'run-scraping-every-5-minutes': {
        'task': 'celery_app.tasks.run_scraping',
        'schedule': 300,  # seconds
    },
}
