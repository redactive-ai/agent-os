from abc import ABC, abstractmethod
from typing import Any


class Tool(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def description(self) -> str: ...

    @abstractmethod
    async def __call__(self, **kwds) -> dict[str, Any]: ...


class ToolWithUserIdentity(Tool):
    @abstractmethod
    def get_user_signin_redirect(self) -> tuple[str, str]: ...
    """Returns (url, state)"""

    @abstractmethod
    def exchange_signin_code(self, signin_code: str, state: str) -> str: ...

    @abstractmethod
    async def __call__(self, access_token: str, **kwds) -> dict[str, Any]: ...
