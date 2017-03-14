from antlr4 import Token
from abc import ABCMeta, abstractmethod
from io import StringIO
from typing import Tuple


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


class TokenStream(IntStream):

    @abstractmethod
    def get(self, index: int) -> Token:
        pass

    def getText(self, interval: Tuple[int, int] = None) -> str:
        if interval is not None:
            index = interval[0]
            stop_index = interval[1] + 1
            with StringIO() as strbuffer:
                while index != stop_index:
                    strbuffer.write(self.get(index).text)
                    index = index + 1
                return strbuffer.getvalue()
        else:
            return self.getText((0, self._total_stream_size))

    @abstractmethod
    def LT(self, offset: int) -> Token:
        pass

    @property
    @abstractmethod
    def _total_stream_size(self) -> int:
        pass


class TokenSource(metaclass=ABCMeta):

    @abstractmethod
    def nextToken(self) -> Token:
        pass


