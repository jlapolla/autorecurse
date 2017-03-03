from abc import ABCMeta, abstractmethod
from typing import TypeVar, Generic
import typing


"""
Abstract base classes for ANTLR 4.5.1-1 runtime.

Based on the Java runtime source code.

https://github.com/antlr/antlr4/tree/4.5.1-1/runtime/Java/src/org/antlr/v4/runtime
"""


class IntStream(metaclass=ABCMeta):

    EOF = -1
    UNKNOWN_SOURCE_NAME = '<unknown>'

    @property
    @abstractmethod
    def index(self) -> int:
        pass

    @property
    @abstractmethod
    def size(self) -> int:
        pass

    def getSourceName(self) -> str:
        return IntStream.UNKNOWN_SOURCE_NAME

    @abstractmethod
    def mark(self) -> int:
        pass

    @abstractmethod
    def release(self, marker: int) -> None:
        pass

    @abstractmethod
    def LA(self, offset: int) -> int:
        pass

    @abstractmethod
    def consume(self) -> None:
        pass

    @abstractmethod
    def seek(self, index: int) -> None:
        pass


class CharStream(IntStream):

    @abstractmethod
    def getText(self, start: int, stop: int) -> str:
        pass


