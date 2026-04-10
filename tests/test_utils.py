from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from core.utils import escape_markdown, kyiv_to_utc

KYIV = ZoneInfo('Europe/Kyiv')
UTC = ZoneInfo('UTC')


class TestKyivToUtc:
    def test_naive_datetime_treated_as_kyiv_and_converted(self):
        # March 12 midnight Kyiv (UTC+2) → March 11 22:00 UTC
        result = kyiv_to_utc(datetime(2026, 3, 12, 0, 0))
        assert result == datetime(2026, 3, 11, 22, 0, tzinfo=UTC)

    def test_naive_datetime_result_is_utc_aware(self):
        result = kyiv_to_utc(datetime(2026, 3, 12, 0, 0))
        assert result.utcoffset().total_seconds() == 0

    def test_aware_utc_datetime_stays_unchanged(self):
        aware = datetime(2026, 3, 12, 10, 0, tzinfo=UTC)
        result = kyiv_to_utc(aware)
        assert result == aware

    def test_aware_kyiv_datetime_converted_to_utc(self):
        kyiv_dt = datetime(2026, 3, 12, 10, 0, tzinfo=KYIV)
        result = kyiv_to_utc(kyiv_dt)
        # 10:00 Kyiv (UTC+2) = 08:00 UTC
        assert result == datetime(2026, 3, 12, 8, 0, tzinfo=UTC)

    def test_aware_iso_with_offset_converted_correctly(self):
        from dateutil.parser import parse
        dt = parse('2026-03-12T10:00:00+02:00')
        result = kyiv_to_utc(dt)
        assert result == datetime(2026, 3, 12, 8, 0, tzinfo=UTC)


class TestEscapeMarkdown:
    def test_escapes_dot(self):
        assert escape_markdown('hello.world') == r'hello\.world'

    def test_escapes_asterisk(self):
        assert escape_markdown('a*b') == r'a\*b'

    def test_escapes_parentheses(self):
        assert escape_markdown('(test)') == r'\(test\)'

    def test_escapes_brackets(self):
        assert escape_markdown('[link]') == r'\[link\]'

    def test_escapes_underscore(self):
        assert escape_markdown('snake_case') == r'snake\_case'

    def test_escapes_dash(self):
        assert escape_markdown('a-b') == r'a\-b'

    def test_escapes_exclamation(self):
        assert escape_markdown('Hello!') == r'Hello\!'

    def test_plain_text_unchanged(self):
        assert escape_markdown('Hello World') == 'Hello World'

    def test_none_returns_empty_string(self):
        assert escape_markdown(None) == ''

    def test_empty_string_returns_empty_string(self):
        assert escape_markdown('') == ''

    def test_multiple_special_chars(self):
        result = escape_markdown('$3,000 - $5,000!')
        assert '\\!' in result
        assert '\\-' in result
