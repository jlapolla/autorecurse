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


T = TypeVar('T')
class Fifo(Buffer[T]):
    """
    A first-in first-out buffer.

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
    - Push = Client calls push
    - Shift = Client calls shift

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
    - Push
      - S -> S
      - I -> I # push never changes current_item
      - E -> E
      - SE -> S
      - EE -> E
    - Shift
      - S -> S
      - S -> SE
      - I -> I # shift does not change current_item in this case
      - I -> S # happens when shift removes current_item from the buffer
      - I -> SE
      - E -> E
      - E -> EE

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
    - push: S I E SE EE
    - shift: S I E

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
    """

    @abstractmethod
    def push(self, item: T) -> None:
        pass

    @abstractmethod
    def shift(self) -> None:
        pass

class LinkedFifo(Fifo[T]):

    class LinkElement(Generic[T]):

        @staticmethod
        def make(content: T) -> 'LinkElement':
            instance = LinkElement()
            LinkElement._setup(instance, content)
            return instance

        @staticmethod
        def _setup(instance: 'LinkElement', content: T) -> None:
            instance._content = content
            instance._next = None

        @property
        def content(self) -> T:
            return self._content

        @property
        def next(self) -> 'LinkElement':
            return self._next

        @next.setter
        def next(self, value: 'LinkElement') -> None:
            self._next = value

    @staticmethod
    def make() -> 'LinkedFifo':
        instance = LinkedFifo()
        LinkedFifo._setup(instance)
        return instance

    @staticmethod
    def _setup(instance: 'LinkedFifo') -> None:
        instance._to_SE()

    @property
    def current_item(self) -> T:
        return self._current_element.content

    @property
    def has_current_item(self) -> bool:
        return self._current_element is not None

    @property
    def is_at_start(self) -> bool:
        return not (self.has_current_item or self.is_at_end)

    @property
    def is_at_end(self) -> bool:
        return self._is_at_end

    def move_to_next(self) -> None:
        if not self.is_empty:
            if self.is_at_start: # State S
                # S -> I
                self._current_index = self._current_index + 1
                self._current_element = self._start_element
                self._to_I()
            else: # State I
                if self._current_item.next is not None:
                    # I -> I
                    self._current_index = self._current_index + 1
                    self._current_element = self._current_element.next
                    self._to_I()
                else:
                    # I -> E
                    self._to_E()
        else: # State SE
            # SE -> EE
            self._to_EE()

    def move_to_end(self) -> None:
        if not self.is_empty: # State S, I, or E
            # S -> E
            # I -> E
            # E -> E
            self._to_E()
        else: # State SE or EE
            # SE -> EE
            # EE -> EE
            self._to_EE()

    @property
    def count(self) -> int:
        return self._count

    @property
    def current_index(self) -> int:
        return self._current_index

    @property
    def is_empty(self) -> bool:
        return self._end_element is None

    def move_to_start(self) -> None:
        if not self.is_empty: # State S, I, or E
            # S -> S
            # I -> S
            # E -> S
            self._to_S()
        else: # State SE or EE
            # SE -> SE
            # EE -> SE
            self._to_SE()

    def push(self, item: T) -> None:
        element = LinkElement.make(item)
        if not self.is_empty:
            if self.is_at_start: # State S
                # S -> S
                self._do_push(element)
                self._to_S()
            elif self.has_current_item: # State I
                # I -> I
                self._do_push(element)
                self._to_I()
            else: # State E
                # E -> E
                self._do_push(element)
                self._to_E()
        else:
            if self.is_at_start: # State SE
                # SE -> S
                self._do_empty_push(element)
                self._to_S()
            else: # State EE
                # EE -> E
                self._do_empty_push(element)
                self._to_E()

    def _do_push(self, element: LinkElement[T]) -> None:
        self._count = self._count + 1
        self._end_element.next = element
        self._end_element = element

    def _do_empty_push(self, element: LinkElement[T]) -> None:
        self._count = self._count + 1
        self._start_element = element
        self._end_element = element

    def shift(self) -> None:
        if self.is_at_start: # State S
            if self._start_element.next is not None:
                # S -> S
                self._do_shift()
                self._to_S()
            else:
                # S -> SE
                self._to_SE()
        elif self.has_current_item: # State I
            if self._current_element is not self._start_element:
                # I -> I
                self._current_index = self._current_index - 1
                self._do_shift()
                self._to_I()
            else:
                if self._start_element.next is not None:
                    # I -> S
                    self._do_shift()
                    self._to_S()
                else:
                    # I -> SE
                    self._to_SE()
        else: # State E
            if self._start_element.next is not None:
                # E -> E
                self._do_shift()
                self._to_E()
            else:
                # E -> EE
                self._to_EE()

    def _do_shift(self) -> None:
        self._count = self._count - 1
        self._start_element = self._start_element.next

    def _to_S(self) -> None:
        self._current_index = -1
        self._current_element = None
        self._is_at_end = False

    def _to_I(self) -> None:
        self._is_at_end = False

    def _to_E(self) -> None:
        self._current_index = self.count
        self._current_element = None
        self._is_at_end = True

    def _to_SE(self) -> None:
        self._count = 0
        self._start_element = None
        self._end_element = None
        self._to_S()

    def _to_EE(self) -> None:
        self._count = 0
        self._start_element = None
        self._end_element = None
        self._to_E()


class FifoWrapper(Fifo[T]):

    @property
    def current_item(self) -> T:
        return self.inner_object.current_item

    @property
    def has_current_item(self) -> bool:
        return self.inner_object.has_current_item

    @property
    def is_at_start(self) -> bool:
        return self.inner_object.is_at_start

    @property
    def is_at_end(self) -> bool:
        return self.inner_object.is_at_end

    def move_to_next(self) -> None:
        self.inner_object.move_to_next()

    def move_to_end(self) -> None:
        self.inner_object.move_to_end()

    @property
    def count(self) -> int:
        return self.inner_object.count

    @property
    def current_index(self) -> int:
        return self.inner_object.current_index

    @property
    def is_empty(self) -> bool:
        return self.inner_object.is_empty

    def move_to_start(self) -> None:
        self.inner_object.move_to_start()

    def move_to_index(self, index: int) -> None:
        self.inner_object.move_to_index(index)

    def push(self, item: T) -> None:
        self.inner_object.push(item)

    def shift(self) -> None:
        self.inner_object.shift()

    @property
    @abstractmethod
    def inner_object(self) -> Fifo[T]:
        pass


class FifoGlobalIndexWrapper(FifoWrapper[T]):
    """
    ## Call State Validity

    - current_global_index (getter): I
    - move_to_global_index: S I E
    """

    @staticmethod
    def make(fifo: Fifo[T]) -> 'FifoGlobalIndexWrapper':
        instance = FifoGlobalIndexWrapper()
        FifoGlobalIndexWrapper._setup(instance, fifo)
        return instance

    @staticmethod
    def _setup(instance: 'FifoGlobalIndexWrapper', fifo: Fifo[T]) -> None:
        instance._fifo = fifo
        instance._start_index = 0

    def shift(self) -> None:
        self._start_index = self._start_index + 1
        super().shift()

    @property
    def inner_object(self) -> Fifo[T]:
        return self._fifo

    @property
    def current_global_index(self) -> int:
        return self._start_index + self.inner_object.current_index

    def move_to_global_index(self, index: int) -> None:
        local_index = index - self._start_index
        self.inner_object.move_to_index(local_index)

del T


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


