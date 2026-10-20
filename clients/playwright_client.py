import json
import logging
import time
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import Playwright, Browser, BrowserContext, Page, sync_playwright

from abstract.browser_client import BaseBrowserClient
from settings import HEADLESS

logger = logging.getLogger(__name__)


class PlaywrightClient(BaseBrowserClient):

    def __init__(
        self,
        proxy: str | dict | None = None,
        provider = None,
    ) -> None:
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None
        self._storage = Path(f"{self.__class__.__name__}-storage")
        super().__init__(proxy, provider)

    def start(self) -> None:
        self._playwright = sync_playwright().start()

        if self._provider:
            self._start_with_provider()
        else:
            self._start_local()

    def close(self) -> None:
        if self._provider:
            self._provider.stop()
        else:
            self._context.storage_state(path=self._storage)

        if self._browser:
            self._browser.close()

        if self._playwright:
            self._playwright.stop()

        logger.info("Playwright successfully stopped")

    def _start_with_provider(self) -> None:
        cdp = self._provider.start()

        self._browser = self._playwright.chromium.connect_over_cdp(cdp)

        if not self._browser.contexts:
            raise RuntimeError("No browser contexts found")

        self._context = self._browser.contexts[0]

        if not self._context.pages:
            raise RuntimeError("No pages found")

        self._page = self._context.pages[0]

        logger.info("Playwright over CDP successfully started")

    def _start_local(self) -> None:
        self._browser = self._playwright.chromium.launch(
            headless=HEADLESS,
            proxy=self._get_proxy(),
        )
        context_kwargs = {}
        if self._storage.exists():
            context_kwargs["storage_state"] = str(self._storage)
        self._context = self._browser.new_context(**context_kwargs)
        print(self._context.cookies())
        self._page = self._context.new_page()

        logger.info("Playwright successfully started")

    def _get_proxy(self) -> dict | None:
        if self._proxy is None:
            return None

        if isinstance(self._proxy, dict):
            return self._proxy

        parsed = urlparse(self._proxy)

        if not parsed.scheme or not parsed.hostname:
            raise ValueError(f"Invalid proxy: {self._proxy}")

        proxy = {
            "server": f"{parsed.scheme}://{parsed.hostname}",
        }

        if parsed.port is not None:
            proxy["server"] += f":{parsed.port}"

        if parsed.username:
            proxy["username"] = parsed.username

        if parsed.password:
            proxy["password"] = parsed.password

        return proxy

    def _get_page(self) -> Page:
        if self._page is None:
            raise RuntimeError("Playwright client is not started")

        return self._page

    def get_content(self, url: str) -> str:
        page = self._get_page()
        page.goto(url)
        time.sleep(30)
        page.reload()
        return page.content()[:1000]