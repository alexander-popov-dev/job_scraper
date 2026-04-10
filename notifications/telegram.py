import logging

import requests

import settings

logger = logging.getLogger(__name__)

_TELEGRAM_TIMEOUT = 10


class TelegramManager:
    """Sends notifications to a configured Telegram channel."""

    @staticmethod
    def send_report(message: str) -> None:
        """Send a MarkdownV2 message to the Telegram channel; logs errors on failure."""
        if not (settings.TELEGRAM_BOT and settings.TELEGRAM_CHANNEL):
            return

        url = f'https://api.telegram.org/bot{settings.TELEGRAM_BOT}/sendMessage'
        payload = {
            'chat_id': settings.TELEGRAM_CHANNEL,
            'text': message,
            'parse_mode': 'MarkdownV2',
        }

        try:
            response = requests.post(url, data=payload, timeout=_TELEGRAM_TIMEOUT)
            if response.status_code != 200:
                logger.error(f'Telegram send failed: {response.status_code} {response.text}')
        except requests.RequestException as e:
            logger.error(f'Telegram request error: {e}')
