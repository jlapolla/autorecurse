from abc import ABCMeta, abstractmethod
import io
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

    ## Call Validity

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

del T_co


T_contra = TypeVar('T_contra', contravariant=True)
class StreamCondition(Generic[T_contra], metaclass=ABCMeta):
    """
    Stateful stream evaluator.

    ## Transition System Definition

    ### States

    - S = Start condition
    - Y = Condition is True
    - N = Condition is False

    ### Transition Labels

    - Recieve = Client calls current_item (setter)

    ### Transitions Grouped by Label

    - Recieve
      - S -> Y
      - S -> N
      - Y -> Y
      - Y -> N
      - N -> Y
      - N -> N

    ## Call Validity

    For each method listed, client is allowed to call the method in the
    given states.

    - current_item (setter): S Y N
    - condition (getter): Y N

    ## Call Results

    For each state listed, calling the specified method will return the
    given result.

    - Y
      - condition (getter): True
    - N
      - condition (getter): False
    """

    @abstractmethod
    def _set_current_item(self, value: T_contra) -> None:
        pass

    current_item = property(None, _set_current_item)

    @property
    @abstractmethod
    def condition(self) -> bool:
        pass

del StreamCondition._set_current_item
del T_contra


class LineBreakError(Exception):

    def __init__(self, message: str = None) -> None:
        if message is None:
            super().__init__("String has multiple line breaks.")
        else:
            super().__init__(message)


class Line:

    @staticmethod
    def make(content: str) -> 'Line':
        instance = Line()
        Line._setup(instance, content)
        return instance

    @staticmethod
    def _setup(instance: 'Line', content: str) -> None:
        lines = content.splitlines()
        if len(lines) == 1:
            instance._content = lines[0]
        elif len(lines) == 0:
            instance._content = ''
        else:
            raise LineBreakError()

    @property
    def content(self) -> str:
        return self._content

    def __str__(self) -> str:
        return self.content

    def __eq__(self, other: 'Line') -> bool:
        return ((other.__class__ is self.__class__)
            and (self.content == other.content))

    def __hash__(self) -> int:
        return hash(self.content)


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


class FileLineIterator(Iterator[Line]):

    @staticmethod
    def make(fp: io.TextIOBase) -> 'FileLineIterator':
        instance = FileLineIterator()
        FileLineIterator._setup(instance, fp)
        return instance

    @staticmethod
    def _setup(instance: 'FileLineIterator', fp: io.TextIOBase) -> None:
        instance._file = fp
        instance._line = None
        instance._is_at_end = False

    @property
    def current_item(self) -> Line:
        return self._line

    @property
    def has_current_item(self) -> bool:
        return self._line is not None

    @property
    def is_at_start(self) -> bool:
        return not (self.has_current_item or self.is_at_end)

    @property
    def is_at_end(self) -> bool:
        return self._is_at_end

    def move_to_next(self) -> None:
        line = self._file.readline()
        if len(line) == 0: # End of file
            self._is_at_end = True
            self._line = None
        else:
            self._line = Line.make(line)


T = TypeVar('T')
class ConditionalSkipIterator(Iterator[T]):

    @staticmethod
    def make(iterator: Iterator[T], condition: StreamCondition[T]) -> 'ConditionalSkipIterator':
        instance = ConditionalSkipIterator()
        ConditionalSkipIterator._setup(instance, iterator, condition)
        return instance

    @staticmethod
    def _setup(instance: 'ConditionalSkipIterator', iterator: Iterator[T], condition: StreamCondition[T]) -> None:
        instance._iterator = iterator
        instance._condition = condition
        pass

    @property
    def current_item(self) -> T:
        return self._iterator.current_item

    @property
    def has_current_item(self) -> bool:
        return self._iterator.has_current_item

    @property
    def is_at_start(self) -> bool:
        return self._iterator.is_at_start

    @property
    def is_at_end(self) -> bool:
        return self._iterator.is_at_end

    def move_to_next(self) -> None:
        found_item = False
        self._iterator.move_to_next()
        while (found_item is False) and (not self.is_at_end):
            self._condition.current_item = self.current_item
            if self._condition.condition:
                found_item = True
            else:
                self._iterator.move_to_next()

del T


class EmptyLineFilter(StreamCondition[Line]):
    """
    Skips empty lines, when used with a ConditionalSkipIterator.

    ## Transition System Definition

    ### States

    - Y = Printing <- INITIAL
    - N = No printing

    ### Transition Labels

    - Empty = Recieve Line equal to _EMPTY_LINE
    - Line = Recieve Line not equal to _EMPTY_LINE

    ### Transitions Grouped by Label

    - Empty
      - Y -> N
      - N -> N
    - Line
      - Y -> Y
      - N -> Y
    """

    _EMPTY_LINE = Line.make('')

    @staticmethod
    def make() -> 'EmptyLineFilter':
        instance = EmptyLineFilter()
        EmptyLineFilter._setup(instance)
        return instance

    @staticmethod
    def _setup(instance: 'EmptyLineFilter') -> None:
        instance._printing = True

    def _set_current_item(self, value: Line) -> None:
        if value == EmptyLineFilter._EMPTY_LINE:
            self._printing = False
        else:
            self._printing = True

    current_item = property(None, _set_current_item)

    @property
    def condition(self) -> bool:
        return self._printing

del EmptyLineFilter._set_current_item


class FileSectionFilter(StreamCondition[Line]):
    """
    Outputs the lines between _START_LINE and _END_LINE, when used with
    a ConditionalSkipIterator.

    ## Transition System Definition

    ### States

    - N = No printing <- INITIAL
    - Y = Printing
    - B = Before printing

    ### Transition Labels

    - Start = Recieve Line equal to _START_LINE
    - End = Recieve Line equal to _END_LINE
    - Line = Recieve Line not equal to _START_LINE or _END_LINE

    ### Transitions Grouped by Label

    - Start
      - N -> B
      - Y -> Y
      - B -> Y
    - End
      - N -> N
      - Y -> N
      - B -> N
    - Line
      - N -> N
      - Y -> Y
      - B -> Y
    """

    _START_LINE = Line.make('# Files')
    _END_LINE = Line.make('# files hash-table stats:')

    # States
    _NO_PRINTING = 0
    _PRINTING = 1
    _BEFORE_PRINTING = 2

    # Transition Labels
    _START = 0
    _END = 1
    _LINE = 2

    # Keys are tuples of (state, transition_label)
    _TRANSITIONS = {
            (_NO_PRINTING, _START): _BEFORE_PRINTING,
            (_PRINTING, _START): _PRINTING,
            (_BEFORE_PRINTING, _START): _PRINTING,
            (_NO_PRINTING, _END): _NO_PRINTING,
            (_PRINTING, _END): _NO_PRINTING,
            (_BEFORE_PRINTING, _END): _NO_PRINTING,
            (_NO_PRINTING, _LINE): _NO_PRINTING,
            (_PRINTING, _LINE): _PRINTING,
            (_BEFORE_PRINTING, _LINE): _PRINTING
            }

    @staticmethod
    def make() -> 'FileSectionFilter':
        instance = FileSectionFilter()
        FileSectionFilter._setup(instance)
        return instance

    @staticmethod
    def _setup(instance: 'FileSectionFilter') -> None:
        instance._state = FileSectionFilter._NO_PRINTING

    def _set_current_item(self, value: Line) -> None:
        if value == FileSectionFilter._START_LINE:
            self._do_transition(FileSectionFilter._START)
        elif value == FileSectionFilter._END_LINE:
            self._do_transition(FileSectionFilter._END)
        else:
            self._do_transition(FileSectionFilter._LINE)

    current_item = property(None, _set_current_item)

    @property
    def condition(self) -> bool:
        return self._state == FileSectionFilter._PRINTING

    def _do_transition(self, transition_label: int) -> None:
        self._state = FileSectionFilter._TRANSITIONS[(self._state, transition_label)]

del FileSectionFilter._set_current_item


