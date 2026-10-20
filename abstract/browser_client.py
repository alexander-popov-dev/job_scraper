from abc import ABC, abstractmethod
from typing import Self


class BaseBrowserClient(ABC):
    def __init__(
        self,
        proxy: str | dict | None = None,
        provider = None,
    ) -> None:
        self._proxy = proxy
        self._provider = provider

    @abstractmethod
    def start(self) -> None: ...

    @abstractmethod
    def close(self) -> None: ...

    def __enter__(self) -> Self:
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
