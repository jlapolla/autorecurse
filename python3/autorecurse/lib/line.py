from autorecurse.lib.iterator import Iterator
from autorecurse.lib.stream import Condition
from io import TextIOBase
from typing import cast


class LineBreakError(Exception):

    def __init__(self, message: str = None) -> None:
        if message is None:
            super().__init__('String has multiple line breaks.')
        else:
            super().__init__(message)


class Line:

    def __init__(self) -> None:
        super().__init__()
        self._content = None # type: str
        self._line_number = None # type: int

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
        instance._line_number = None

    @staticmethod
    def make_with_line_number(content: str, line_number: int) -> 'Line':
        instance = Line()
        Line._setup_with_line_number(instance, content, line_number)
        return instance

    @staticmethod
    def _setup_with_line_number(instance: 'Line', content: str, line_number: int) -> None:
        Line._setup(instance, content)
        instance._line_number = line_number

    @property
    def content(self) -> str:
        return self._content

    @property
    def has_line_number(self) -> bool:
        return self._line_number is not None

    @property
    def line_number(self) -> int:
        """
        ## Specification Domain

        - self.has_line_number is True
        """
        return self._line_number

    def __str__(self) -> str:
        return self.content

    def __eq__(self, other: object) -> bool:
        if (other.__class__ is self.__class__):
            right = cast(Line, other)
            if (self.content == right.content) and (self.has_line_number is right.has_line_number):
                if self.has_line_number:
                    if self.line_number == right.line_number:
                        return True
                else:
                    return True
        return False

    def __hash__(self) -> int:
        if self.has_line_number:
            return hash((self.content, self.line_number))
        else:
            return hash(self.content)


class FileLineIterator(Iterator[Line]):

    def __init__(self) -> None:
        super().__init__()
        self._line = None # type: Line
        self._is_at_end = None # type: bool
        self._file = None # type: TextIOBase

    @staticmethod
    def make(fp: TextIOBase) -> 'FileLineIterator':
        instance = FileLineIterator()
        FileLineIterator._setup(instance, fp)
        return instance

    @staticmethod
    def _setup(instance: 'FileLineIterator', fp: TextIOBase) -> None:
        instance._file = fp
        instance._to_S()

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
        if self.is_at_start: # State S
            line = self._file.readline()
            if len(line) != 0:
                # S -> I
                self._line = Line.make_with_line_number(line, 1)
                self._to_I()
            else: # End of file
                # S -> E
                self._to_E()
        else: # State I
            line = self._file.readline()
            if len(line) != 0:
                # I -> I
                self._line = Line.make_with_line_number(line, self._line.line_number + 1)
                self._to_I()
            else: # End of file
                # I -> E
                self._to_E()

    def _to_S(self) -> None:
        self._line = None
        self._is_at_end = False

    def _to_I(self) -> None:
        self._is_at_end = False

    def _to_E(self) -> None:
        self._line = None
        self._is_at_end = True


class LineToCharIterator(Iterator[str]):

    EOL_LF = '\n'

    def __init__(self) -> None:
        super().__init__()
        self._index = None # type: int
        self._eol = None # type: str
        self._source = None # type: Iterator[Line]

    @staticmethod
    def make(source: Iterator[Line]) -> Iterator[str]:
        instance = LineToCharIterator()
        LineToCharIterator._setup(instance, source)
        return instance

    @staticmethod
    def _setup(instance: 'LineToCharIterator', source: Iterator[Line]) -> None:
        instance._source = source
        instance._index = 0
        instance._eol = LineToCharIterator.EOL_LF

    @property
    def current_item(self) -> str:
        # State I
        if self._index < len(self._content):
            return self._content[self._index]
        else:
            return self._eol[self._index - len(self._content)]

    @property
    def _content(self) -> str:
        # State I
        return self._source.current_item.content

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
            self._move_to_next_non_blank_line()
        else: # State I
            if self._index + 1 != self._current_length:
                # I -> I
                self._index = self._index + 1
            else:
                # I -> I
                # I -> E
                self._index = 0
                self._move_to_next_non_blank_line()

    @property
    def _current_length(self) -> int:
        if self.is_at_start: # State S
            return 0
        elif self.has_current_item: # State I
            return len(self._content) + len(self._eol)
        else: # State E
            return 0

    def _move_to_next_non_blank_line(self) -> None:
        # State S or I
        self._source.move_to_next()
        while (self._current_length == 0) and (not self.is_at_end):
            self._source.move_to_next()

    def move_to_end(self) -> None:
        self._source.move_to_end()


class EmptyLineFilter(Condition[Line]):
    """
    Skips empty lines, when used with a ConditionFilter.

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

    def __init__(self) -> None:
        super().__init__()
        self._printing = None # type: bool

    @staticmethod
    def make() -> 'EmptyLineFilter':
        instance = EmptyLineFilter()
        EmptyLineFilter._setup(instance)
        return instance

    @staticmethod
    def _setup(instance: 'EmptyLineFilter') -> None:
        instance._printing = True

    def _set_current_item(self, value: Line) -> None:
        if value.content == EmptyLineFilter._EMPTY_LINE.content:
            self._printing = False
        else:
            self._printing = True

    current_item = property(None, _set_current_item)

    @property
    def condition(self) -> bool:
        return self._printing

del EmptyLineFilter._set_current_item


