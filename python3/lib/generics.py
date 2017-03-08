import re
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
class FifoBase(Buffer[T]):

    @abstractmethod
    def push(self, item: T) -> None:
        pass


class Fifo(FifoBase[T]):
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
      - I -> I # never changes current_item
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
    def shift(self) -> None:
        pass


class ManagedFifo(FifoBase[T]):
    """
    A Fifo that uses garbage collection to remove items, instead of
    having the client make explicit calls to shift.

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
    - Collect = Client calls collect_garbage

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
    - Push # may automatically trigger Collect
      - S -> S
      - I -> I # never changes current_item
      - E -> E
      - E -> EE
      - SE -> S
      - EE -> E
      - EE -> EE
    - Collect
      - S -> S # has no effect
      - I -> I # preserves current_item and all items after
      - E -> E
      - E -> EE
      - SE -> SE # has no effect
      - EE -> EE # has no effect

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
    - collect_garbage: S I E SE EE
    - new_strong_reference: I
    - release_strong_reference: S I E SE EE

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

    - release_strong_reference is tolerant, and may be called with any
      int. Calling release_strong_reference with an invalid int has no
      effect.
    """

    @abstractmethod
    def collect_garbage(self) -> None:
        """
        Client code may call collect_garbage to force an immediate
        garbage collection.

        Implementations may call collect_garbage automatically when push
        is called.
        """
        pass

    @abstractmethod
    def new_strong_reference(self) -> int:
        """
        Returns a reference token that represents a strong reference to
        current_item. ManagedFifo will not remove current_item until all
        strong references to the item have been released.

        To release a reference token, client code must call
        release_strong_reference with the token.
        """
        pass

    @abstractmethod
    def release_strong_reference(self, ref_token: int) -> None:
        """
        Allows ManagedFifo to remove the referenced item.
        """
        pass


class LinkedFifo(Fifo[T]):

    class LinkElement(Generic[T]):

        @staticmethod
        def make(content: T) -> 'LinkedFifo.LinkElement':
            instance = LinkedFifo.LinkElement()
            LinkedFifo.LinkElement._setup(instance, content)
            return instance

        @staticmethod
        def _setup(instance: 'LinkedFifo.LinkElement', content: T) -> None:
            instance._content = content
            instance._next = None

        @property
        def content(self) -> T:
            return self._content

        @property
        def next(self) -> 'LinkedFifo.LinkElement':
            return self._next

        @next.setter
        def next(self, value: 'LinkedFifo.LinkElement') -> None:
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
                if self._current_element.next is not None:
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
        element = LinkedFifo.LinkElement.make(item)
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

    def _do_push(self, element: 'LinkedFifo.LinkElement[T]') -> None:
        self._count = self._count + 1
        self._end_element.next = element
        self._end_element = element

    def _do_empty_push(self, element: 'LinkedFifo.LinkElement[T]') -> None:
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

    - global_count (getter): S I E SE EE
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
    def global_count(self) -> int:
        return self._start_index + self.count

    @property
    def current_global_index(self) -> int:
        return self._start_index + self.inner_object.current_index

    def move_to_global_index(self, index: int) -> None:
        local_index = index - self._start_index
        self.inner_object.move_to_index(local_index)


class FifoToManagedFifoAdapter(ManagedFifo[T]):

    class ReferenceCounter:

        @staticmethod
        def make() -> 'FifoToManagedFifoAdapter.ReferenceCounter':
            instance = FifoToManagedFifoAdapter.ReferenceCounter()
            FifoToManagedFifoAdapter.ReferenceCounter._setup(instance)
            return instance

        @staticmethod
        def _setup(instance: 'FifoToManagedFifoAdapter.ReferenceCounter') -> None:
            instance._count = 0

        @property
        def is_at_zero(self) -> bool:
            return self._count == 0

        def increment(self) -> None:
            self._count = self._count + 1

        def decrement(self) -> None:
            self._count = self._count - 1

    @staticmethod
    def make(fifo: Fifo[T]) -> 'FifoToManagdFifoAdapter':
        instance = FifoToManagedFifoAdapter()
        FifoToManagedFifoAdapter._setup(instance, fifo)
        return instance

    @staticmethod
    def _setup(instance: 'FifoToManagedFifoAdapter', fifo: Fifo[T]) -> None:
        instance._refcounters = []
        instance._ref_token_dict = {}
        instance._current_reference_token = 0
        instance._fifo = fifo
        FifoToManagedFifoAdapter._initialize_ref_counters(instance)

    @staticmethod
    def _initialize_ref_counters(instance: 'FifoToManagedFifoAdapter') -> None:
        count = instance._fifo.count
        while (count != 0):
            instance._refcounters.append(FifoToManagedFifoAdapter.ReferenceCounter.make())
            count = count - 1

    MAX_ACTIVE_REFERENCES = 2147483647 # Max signed 32-bit int

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
        self._refcounters.append(FifoToManagedFifoAdapter.ReferenceCounter.make())
        self.collect_garbage()

    def collect_garbage(self) -> None:
        while self._can_shift:
            self.inner_object.shift()
            self._refcounters.pop(0)

    @property
    def _can_shift(self) -> bool:
        result = None
        if not self.is_empty:
            if self.is_at_start: # State S
                # S -> S
                result = False
            elif self.has_current_item: # State I
                # I -> I
                result = (self._refcounters[0].is_at_zero) and (self.current_index != 0)
            else: # State E
                # E -> E
                # E -> EE
                result = self._refcounters[0].is_at_zero
        else: # State SE or EE
            # SE -> SE
            # EE -> EE
            result = False
        return result

    def new_strong_reference(self) -> int:
        # State I
        ref_token = self._next_available_reference_token()
        refcounter = self._current_reference_counter()
        self._ref_token_dict[ref_token] = refcounter
        refcounter.increment()
        self._current_reference_token = ref_token
        return ref_token

    def _next_available_reference_token(self) -> int:
        ref_token = self._next_reference_token(self._current_reference_token)
        while (ref_token in self._ref_token_dict) and (ref_token != self._current_reference_token):
            ref_token = self._next_reference_token(self._current_reference_token)
        if ref_token == self._current_reference_token:
            raise RuntimeError('Reached maximum number of active strong references: ' + FifoToManagedFifoAdapter.MAX_ACTIVE_REFERENCES + '. You must release some references to continue.')
        return ref_token

    def _next_reference_token(self, ref_token: int) -> int:
        result = None
        if ref_token != FifoToManagedFifoAdapter.MAX_ACTIVE_REFERENCES:
            result = ref_token + 1
        else:
            result = 0
        return result

    def _current_reference_counter(self) -> 'FifoToManagedFifoAdapter.ReferenceCounter[T]':
        # State I
        return self._refcounters[self.current_index]

    def release_strong_reference(self, ref_token: int) -> None:
        if ref_token in self._ref_token_dict:
            refcounter = self._ref_token_dict[ref_token]
            refcounter.decrement()
            del self._ref_token_dict[ref_token]

    @property
    def inner_object(self) -> Fifo[T]:
        return self._fifo

del T


class LineBreakError(Exception):

    def __init__(self, message: str = None) -> None:
        if message is None:
            super().__init__('String has multiple line breaks.')
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

    def __eq__(self, other: 'Line') -> bool:
        if (other.__class__ is self.__class__) and (self.content == other.content) and (self.has_line_number is other.has_line_number):
            if self.has_line_number:
                if self.line_number == other.line_number:
                    return True
            else:
                return True
        return False

    def __hash__(self) -> int:
        if self.has_line_number:
            return hash(self.content, self.line_number)
        else:
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


class LineToCharIterator(Iterator[str]):

    EOL_LF = '\n'

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


class FileLineIterator(Iterator[Line]):

    @staticmethod
    def make(fp: io.TextIOBase) -> 'FileLineIterator':
        instance = FileLineIterator()
        FileLineIterator._setup(instance, fp)
        return instance

    @staticmethod
    def _setup(instance: 'FileLineIterator', fp: io.TextIOBase) -> None:
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
        if value.content == EmptyLineFilter._EMPTY_LINE.content:
            self._printing = False
        else:
            self._printing = True

    current_item = property(None, _set_current_item)

    @property
    def condition(self) -> bool:
        return self._printing

del EmptyLineFilter._set_current_item


class InformationalCommentFilter(StreamCondition[Line]):
    """
    Skips informational comments, when used with a
    ConditionalSkipIterator.

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


