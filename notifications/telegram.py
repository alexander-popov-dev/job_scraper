import logging
import time

import requests

import settings

logger = logging.getLogger(__name__)

_TELEGRAM_TIMEOUT = 10
_RATE_LIMIT_RETRIES = 3


class TelegramManager:
    """Sends notifications to a configured Telegram channel."""

    @staticmethod
    def send_message(message: str, group_id: int | None = None) -> None:
        """Send a MarkdownV2 message to the Telegram channel; retries on 429, logs errors on failure."""
        if not (settings.TELEGRAM_BOT and settings.TELEGRAM_CHANNEL):
            return

        url = f'https://api.telegram.org/bot{settings.TELEGRAM_BOT}/sendMessage'
        payload = {
            'chat_id': settings.TELEGRAM_CHANNEL,
            'text': message,
            'parse_mode': 'MarkdownV2',
        }

        if group_id:
            payload['message_thread_id'] = group_id

        for attempt in range(_RATE_LIMIT_RETRIES):
            try:
                response = requests.post(url, data=payload, timeout=_TELEGRAM_TIMEOUT)
                if response.status_code == 200:
                    return
                if response.status_code == 429:
                    retry_after = response.json().get('parameters', {}).get('retry_after', 5)
                    logger.warning(f'Telegram rate limit hit, retrying in {retry_after}s')
                    time.sleep(retry_after)
                    continue
                logger.error(f'Telegram send failed: {response.status_code} {response.text}')
                return
            except requests.RequestException as e:
                logger.error(f'Telegram request error: {e}')
                return
