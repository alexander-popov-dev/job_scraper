from enum import StrEnum


class CeleryQueue(StrEnum):
    MAIN = 'main'
    SCRAPING = 'scraping'


class SiteName(StrEnum):
    DOU = 'DOU'
    DJINNI = 'Djinni'
    ROBOTA_UA = 'RobotaUA'
    WORK_UA = 'WorkUA'
    THE_JOB = 'TheJob'


class SessionStatus(StrEnum):
    STARTED = 'started'
    COMPLETED = 'completed'
    FAILED = 'failed'
