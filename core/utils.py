import re
from datetime import datetime
from zoneinfo import ZoneInfo

_KYIV_TZ = ZoneInfo('Europe/Kyiv')
_UTC_TZ = ZoneInfo('UTC')

_MARKDOWN_SPECIAL = re.compile(r'([_*\[\]()~`>#+=|{}.!\\-])')


def kyiv_to_utc(dt: datetime) -> datetime:
    """Convert a datetime to UTC, assuming Kyiv timezone if naive."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=_KYIV_TZ)
    return dt.astimezone(_UTC_TZ)


def escape_markdown(text: str | None) -> str:
    """Escape all Telegram MarkdownV2 special characters in *text*."""
    return _MARKDOWN_SPECIAL.sub(r'\\\1', text or '')
