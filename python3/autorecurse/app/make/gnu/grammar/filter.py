from autorecurse.lib.line import Line
from autorecurse.lib.stream import Condition
from autorecurse.lib.iterator import *
import re


class FileSectionFilter(Condition[Line]):
    """
    Outputs the lines between _START_LINE and _END_LINE, when used with
    a ConditionFilter.

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
        if value.content == FileSectionFilter._START_LINE.content:
            self._do_transition(FileSectionFilter._START)
        elif value.content == FileSectionFilter._END_LINE.content:
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


class InformationalCommentFilter(Condition[Line]):
    """
    Skips informational comments, when used with a
    ConditionFilter.

    ## Transition System Definition

    ### States

    - Y = Printing <- INITIAL
    - N = No printing

    ### Transition Labels

    - Informational = Recieve Line matching _INFORMATIONAL_RE
    - Line = Recieve Line not matching _INFORMATIONAL_RE

    ### Transitions Grouped by Label

    - Informational
      - Y -> N
      - N -> N
    - Line
      - Y -> Y
      - N -> Y
    """

    _INFORMATIONAL_RE = re.compile(r'^#  ')

    @staticmethod
    def make() -> 'InformationalCommentFilter':
        instance = InformationalCommentFilter()
        InformationalCommentFilter._setup(instance)
        return instance

    @staticmethod
    def _setup(instance: 'InformationalCommentFilter') -> None:
        instance._printing = True

    def _set_current_item(self, value: Line) -> None:
        if InformationalCommentFilter._INFORMATIONAL_RE.match(value.content) is not None:
            self._printing = False
        else:
            self._printing = True

    current_item = property(None, _set_current_item)

    @property
    def condition(self) -> bool:
        return self._printing

del InformationalCommentFilter._set_current_item


