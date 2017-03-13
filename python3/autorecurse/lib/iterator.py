from abc import ABCMeta, abstractmethod
from typing import  Generic, Iterable, TypeVar


T = TypeVar('T')
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


class ListIterator(Iterator[T]):

    @staticmethod
    def make(it: Iterable[T]) -> 'ListIterator':
        instance = ListIterator()
        ListIterator._setup(instance, it)
        return instance

    @staticmethod
    def _setup(instance: 'ListIterator', it: Iterable[T]) -> None:
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


del T_co
del T


