from abc import ABC, abstractmethod


class Tool(ABC):
    @property
    @abstractmethod
    def id(self) -> str: ...

    @property
    @abstractmethod
    def description(self) -> str: ...

    @abstractmethod
    def __call__(self, **kwds): ...
