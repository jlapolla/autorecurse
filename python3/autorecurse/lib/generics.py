import sys
import re
from abc import ABCMeta, abstractmethod
from typing import TypeVar, Generic
import typing


T_co = TypeVar('T_co', covariant=True)
class Iterator(Generic[T_co], metaclass=ABCMeta):
    """
    A stream of items.

    ## Transition System Definition

    ### States

    - S = Start
    - I = Intermediate
    - E = End

    ### Transition Labels

    - Next = Client calls move_to_next
    - End = Client calls move_to_end

    ### Transitions Grouped by Label

    - Next
      - S -> I
      - S -> E
      - I -> I
      - I -> E
    - End
      - S -> E
      - I -> E
      - E -> E

    ## Call State Validity

    For each method listed, client is allowed to call the method in the
    given states.

    - current_item (getter): I
    - has_current_item (getter): S I E
    - is_at_start (getter): S I E
    - is_at_end (getter): S I E
    - move_to_next: S I
    - move_to_end: S I E

    ## Call Results

    For each state listed, calling the specified method will return the
    given result.

    - S
      - has_current_item (getter): False
      - is_at_start (getter): True
      - is_at_end (getter): False
    - I
      - has_current_item (getter): True
      - is_at_start (getter): False
      - is_at_end (getter): False
    - E
      - has_current_item (getter): False
      - is_at_start (getter): False
      - is_at_end (getter): True
    """

    @property
    @abstractmethod
    def current_item(self) -> T_co:
        pass

    @property
    @abstractmethod
    def has_current_item(self) -> bool:
        pass

    @property
    @abstractmethod
    def is_at_start(self) -> bool:
        pass

    @property
    @abstractmethod
    def is_at_end(self) -> bool:
        pass

    @abstractmethod
    def move_to_next(self) -> None:
        pass

    def move_to_end(self) -> None:
        while not self.is_at_end:
            self.move_to_next()


class IteratorContext(Generic[T_co], metaclass=ABCMeta):

    @abstractmethod
    def __enter__(self) -> Iterator[T_co]:
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        pass


class BufferedIterator(Iterator[T_co]):
    """
    A buffered stream of items.

    ## Transition System Definition

    ### States

    - S = Start
    - I = Intermediate
    - E = End

    ### Transition Labels

    - Next = Client calls move_to_next
    - End = Client calls move_to_end

    ### Transitions Grouped by Label

    - Next
      - S -> I
      - S -> E
      - I -> I
      - I -> E
    - End
      - S -> E
      - I -> E
      - E -> E

    ## Call State Validity

    For each method listed, client is allowed to call the method in the
    given states.

    - current_item (getter): I
    - has_current_item (getter): S I E
    - is_at_start (getter): S I E
    - is_at_end (getter): S I E
    - new_bookmark: I
    - release_bookmark: S I E
    - move_to_next: S I
    - move_to_end: S I E
    - move_to_bookmark: S I E

    ## Call Argument Validity

    For each method listed, client is allowed to call the method with
    the given parameters.

    - move_to_bookmark(self, bookmark: int)
      - bookmark has not been released

    ## Call Results

    For each state listed, calling the specified method will return the
    given result.

    - S
      - has_current_item (getter): False
      - is_at_start (getter): True
      - is_at_end (getter): False
    - I
      - has_current_item (getter): True
      - is_at_start (getter): False
      - is_at_end (getter): False
    - E
      - has_current_item (getter): False
      - is_at_start (getter): False
      - is_at_end (getter): True

    ## Notes

    - release_bookmark is tolerant, and may be called with any int. Calling
      release_bookmark with an invalid int has no effect.
    """

    @abstractmethod
    def new_bookmark(self) -> int:
        pass

    @abstractmethod
    def release_bookmark(self, bookmark: int) -> None:
        pass

    @abstractmethod
    def move_to_bookmark(self, bookmark: int) -> None:
        pass


class Buffer(Iterator[T_co]):
    """
    A stream of items that can return to its start.

    ## Transition System Definition

    ### States

    - S = Start, Not empty
    - I = Intermediate, Not empty
    - E = End, Not empty
    - SE = Start, Empty
    - EE = End, Empty

    ### Transition Labels

    - Next = Client calls move_to_next
    - End = Client calls move_to_end
    - Start = Client calls move_to_start

    ### Transitions Grouped by Label

    - Next
      - S -> I
      - I -> I
      - I -> E
      - SE -> EE
    - End
      - S -> E
      - I -> E
      - E -> E
      - SE -> EE
      - EE -> EE
    - Start
      - S -> S
      - I -> S
      - E -> S
      - SE -> SE
      - EE -> SE

    ## Call State Validity

    For each method listed, client is allowed to call the method in the
    given states.

    - count (getter): S I E SE EE
    - current_index (getter): I
    - current_item (getter): I
    - has_current_item (getter): S I E SE EE
    - is_at_start (getter): S I E SE EE
    - is_at_end (getter): S I E SE EE
    - is_empty (getter): S I E SE EE
    - move_to_next: S I SE
    - move_to_end: S I E SE EE
    - move_to_start: S I E SE EE
    - move_to_index: S I E

    ## Call Argument Validity

    For each method listed, client is allowed to call the method with
    the given parameters.

    - move_to_index(self, index: int)
      - 0 <= index /\ index < self.count

    ## Call Results

    For each state listed, calling the specified method will return the
    given result.

    - S
      - has_current_item (getter): False
      - is_at_start (getter): True
      - is_at_end (getter): False
      - is_empty (getter): False
    - I
      - has_current_item (getter): True
      - is_at_start (getter): False
      - is_at_end (getter): False
      - is_empty (getter): False
    - E
      - has_current_item (getter): False
      - is_at_start (getter): False
      - is_at_end (getter): True
      - is_empty (getter): False
    - SE
      - has_current_item (getter): False
      - is_at_start (getter): True
      - is_at_end (getter): False
      - is_empty (getter): True
      - count (getter): 0
    - EE
      - has_current_item (getter): False
      - is_at_start (getter): False
      - is_at_end (getter): True
      - is_empty (getter): True
      - count (getter): 0

    ## Notes

    - The index of the first item (if any) is always 0.
      - In other words, if 'self.count > 0', then running
        'self.move_to_start(); self.move_to_next()' will cause
        'self.current_index' to return 0.
    """

    @property
    @abstractmethod
    def count(self) -> int:
        pass

    @property
    @abstractmethod
    def current_index(self) -> int:
        pass

    @property
    @abstractmethod
    def is_empty(self) -> bool:
        pass

    @abstractmethod
    def move_to_start(self) -> None:
        pass

    def move_to_index(self, index: int) -> None:
        if self.is_at_start: # State S
            self.move_to_next() # S -> I
            self.move_to_index(index)
        elif self.has_current_item: # State I
            if index >= self.current_index:
                diff = index - self.current_index
                while (diff != 0):
                    self.move_to_next()
                    diff = diff - 1
            else:
                self.move_to_start() # I -> S
                self.move_to_index(index)
        else: # State E
            self.move_to_start() # E -> S
            self.move_to_index(index)

del T_co


T = TypeVar('T')
class IteratorConcatenator(Iterator[T]):

    @staticmethod
    def make(source: Iterator[Iterator[T]]) -> 'IteratorConcatenator[T]':
        instance = IteratorConcatenator()
        IteratorConcatenator._setup(instance, source)
        return instance

    @staticmethod
    def _setup(instance: 'IteratorConcatenator[T]', source: Iterator[Iterator[T]]) -> None:
        instance._source = source
        IteratorConcatenator._init_current_iterator(instance)

    @staticmethod
    def _init_current_iterator(instance: 'IteratorConcatenator[T]') -> None:
        if instance._source.is_at_start: # State S (instance._source)
            instance._to_S()
        elif instance._source.has_current_item: # State I (instance._source)
            instance._current_iterator = instance._source.current_item
            if instance._current_iterator.is_at_start: # State S (instance._current_iterator)
                instance._current_iterator.move_to_next()
                IteratorConcatenator._init_current_iterator(instance)
            elif instance._current_iterator.has_current_item: # State I (instance._current_iterator)
                instance._to_I()
            else: # State E (instance._current_iterator)
                instance._move_to_next_non_empty_iterator()
        else: # State E (instance._source)
            instance._to_E()

    @property
    def current_item(self) -> T:
        return self._current_iterator.current_item

    @property
    def has_current_item(self) -> bool:
        return self._source.has_current_item

    @property
    def is_at_start(self) -> bool:
        return self._source.is_at_start

    @property
    def is_at_end(self) -> bool:
        return self._source.is_at_end

    def move_to_next(self) -> None:
        if self.is_at_start: # State S
            # S -> I
            # S -> E
            self._move_to_next_non_empty_iterator()
        else: # State I
            self._current_iterator.move_to_next()
            if self._current_iterator.is_at_end:
                # I -> I
                # I -> E
                self._move_to_next_non_empty_iterator()

    def _move_to_next_non_empty_iterator(self) -> None:
        # State S or I
        while True:
            self._current_iterator = None
            self._source.move_to_next()
            if self._source.is_at_end:
                self._to_E()
                break
            self._current_iterator = self._source.current_item
            self._current_iterator.move_to_next()
            if self._current_iterator.has_current_item:
                self._to_I()
                break

    def _to_S(self) -> None:
        self._current_iterator = None

    def _to_I(self) -> None:
        pass

    def _to_E(self) -> None:
        self._current_iterator = None

del T


T = TypeVar('T')
class ListIterator(Iterator[T]):

    @staticmethod
    def make(it: typing.Iterable[T]) -> 'ListIterator':
        instance = ListIterator()
        ListIterator._setup(instance, it)
        return instance

    @staticmethod
    def _setup(instance: 'ListIterator', it: typing.Iterable[T]) -> None:
        instance._list = list(it)
        instance._is_at_start = True

    @property
    def current_item(self) -> T:
        return self._list[0]

    @property
    def has_current_item(self) -> bool:
        return not (self.is_at_start or (len(self._list) == 0))

    @property
    def is_at_start(self) -> bool:
        return self._is_at_start

    @property
    def is_at_end(self) -> bool:
        return (not self.is_at_start) and (len(self._list) == 0)

    def move_to_next(self) -> None:
        if self.is_at_start:
            self._is_at_start = False
        else:
            self._list.pop(0)

    def move_to_end(self) -> None:
        self._is_at_start = False
        self._list.clear()

del T


class StringBuffer(Buffer[str]):

    @staticmethod
    def make(string: str) -> 'StringBuffer':
        instance = StringBuffer()
        StringBuffer._setup(instance, string)
        return instance

    @staticmethod
    def _setup(instance: 'StringBuffer', string: str) -> None:
        instance._string = string
        instance._to_S()

    @property
    def current_item(self) -> str:
        return self._string[self.current_index]

    @property
    def has_current_item(self) -> bool:
        return not (self.is_at_start or self.is_at_end or self.is_empty)

    @property
    def is_at_start(self) -> bool:
        return self._is_at_start

    @property
    def is_at_end(self) -> bool:
        return self._is_at_end

    def move_to_next(self) -> None:
        if not self.is_empty:
            if self.is_at_start: # State S
                # S -> I
                self._current_index = self._current_index + 1
                self._to_I()
            else: # State I
                if self.current_index + 1 != self.count:
                    # I -> I
                    self._current_index = self._current_index + 1
                    self._to_I()
                else:
                    # I -> E
                    self._to_E()
        else: # State SE
            # SE -> EE
            self._to_EE()

    def move_to_end(self) -> None:
        if not self.is_empty:
            # S -> E
            # I -> E
            # E -> E
            self._to_E()
        else:
            # SE -> EE
            # EE -> EE
            self._to_EE()

    @property
    def count(self) -> int:
        return len(self._string)

    @property
    def current_index(self) -> int:
        return self._current_index

    @property
    def is_empty(self) -> bool:
        return self.count == 0

    def move_to_start(self) -> None:
        if not self.is_empty:
            # S -> S
            # I -> S
            # E -> S
            self._to_S()
        else:
            # SE -> SE
            # EE -> SE
            self._to_SE()

    def move_to_index(self, index: int) -> None:
        # S -> I
        # I -> I
        # E -> I
        self._current_index = index
        self._to_I()

    def _to_S(self) -> None:
        self._current_index = -1
        self._is_at_start = True
        self._is_at_end = False

    def _to_I(self) -> None:
        self._is_at_start = False
        self._is_at_end = False

    def _to_E(self) -> None:
        self._current_index = self.count
        self._is_at_start = False
        self._is_at_end = True

    def _to_SE(self) -> None:
        self._to_S()

    def _to_EE(self) -> None:
        self._to_E()


