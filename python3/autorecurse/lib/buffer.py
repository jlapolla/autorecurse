from abc import abstractmethod
from typing import TypeVar
from autorecurse.lib.iterator import Iterator


T = TypeVar('T')


class Buffer(Iterator[T]):
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


class StringBuffer(Buffer[str]):

    def __init__(self) -> None:
        super().__init__()
        self._string = None # type: str
        self._is_at_start = None # type: bool
        self._is_at_end = None # type: bool
        self._current_index = None # type: int

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


del T


