from autorecurse.lib.buffer import Buffer
from abc import abstractmethod
from typing import TypeVar, Generic, List
import sys


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


class ArrayedFifo(Fifo[T]):

    DEFAULT_CAPACITY_FACTOR = 1.0

    @staticmethod
    def make() -> 'ArrayedFifo[T]':
        instance = ArrayedFifo()
        ArrayedFifo._setup(instance)
        return instance

    @staticmethod
    def _setup(instance: 'ArrayedFifo[T]') -> None:
        instance._list = [None]
        instance._physical_index_start = 0
        instance._physical_index_end = 0
        instance._inverted = False
        instance._capacity_factor = ArrayedFifo.DEFAULT_CAPACITY_FACTOR
        instance._to_S()

    @property
    def current_item(self) -> T:
        # State I
        return self._list[self._physical_index]

    @property
    def has_current_item(self) -> bool:
        # State S, I, E, SE, or EE
        return self._index is not None

    @property
    def is_at_start(self) -> bool:
        # State S, I, E, SE, or EE
        return not (self.has_current_item or self.is_at_end)

    @property
    def is_at_end(self) -> bool:
        # State S, I, E, SE, or EE
        return self._is_at_end

    def move_to_next(self) -> None:
        if not self.is_empty:
            if self.is_at_start: # State S
                # S -> I
                self._index = 0
                self._to_I()
            else: # State I
                if self._index + 1 != self.count:
                    # I -> I
                    self._index = self._index + 1
                else:
                    # I -> E
                    self._to_E()
        else: # State SE
            # SE -> EE
            self._to_E()

    def move_to_end(self) -> None:
        # State S, I, E, SE, or EE
        # S -> E
        # I -> E
        # E -> E
        # SE -> EE
        # EE -> EE
        self._to_E()

    @property
    def count(self) -> int:
        # State S, I, E, SE, or EE
        if not self._inverted:
            return self._physical_index_end - self._physical_index_start
        else:
            return self._physical_index_end + self.capacity - self._physical_index_start

    @property
    def current_index(self) -> int:
        # State I
        return self._index

    @property
    def is_empty(self) -> bool:
        # State S, I, E, SE, or EE
        return self.count == 0

    def move_to_start(self) -> None:
        # State S, I, E, SE, or EE
        # S -> S
        # I -> S
        # E -> S
        # SE -> SE
        # EE -> SE
        self._to_S()

    def move_to_index(self, index: int) -> None:
        # State S, I, or E
        # S -> I
        # I -> I
        # E -> I
        self._index = index
        self._to_I()

    def push(self, item: T) -> None:
        # State S, I, E, SE, or EE
        if self.count != self.capacity:
            self._list[self._physical_index_end] = item
            self._increment_physical_index_end()
        else: # State S, I, or E
            self._increase_capacity()
            self.push(item)

    def _increment_physical_index_end(self) -> None:
        # State S, I, E, SE, or EE
        if self._physical_index_end + 1 != self.capacity:
            self._physical_index_end = self._physical_index_end + 1
        else:
            self._physical_index_end = 0
            self._inverted = not self._inverted

    def shift(self) -> None:
        if self.is_at_start: # State S
            # S -> S
            # S -> SE
            self._increment_physical_index_start()
        elif self.has_current_item: # State I
            if self._physical_index != self._physical_index_start:
                # I -> I
                self._index = self._index - 1
                self._increment_physical_index_start()
            else:
                # I -> S
                # I -> SE
                self._increment_physical_index_start()
                self._to_S()
        else: # State E
            # E -> E
            # E -> EE
            self._increment_physical_index_start()

    def _increment_physical_index_start(self) -> None:
        # State S, I, or E
        self._list[self._physical_index_start] = None
        if self._physical_index_start + 1 != self.capacity:
            self._physical_index_start = self._physical_index_start + 1
        else:
            self._physical_index_start = 0
            self._inverted = not self._inverted

    @property
    def _physical_index(self) -> int:
        # State I
        if not self._inverted:
            return self._index + self._physical_index_start
        else:
            return self._index + self._physical_index_start - self.capacity

    def _increase_capacity(self) -> None:
        # State S, I, E
        added_capacity = int(self.capacity * self.capacity_factor)
        if added_capacity == 0:
            added_capacity = 1
        self._reallocate(self.capacity + added_capacity)

    def _reallocate(self, new_capacity: int) -> None:
        """
        ## Specification Domain

        - 0 < new_capacity
        - self.count <= new_capacity
        """
        # State S, I, E, SE, or EE
        new_list = [None] * new_capacity
        self._copy_to_list(new_list)
        if self.count != new_capacity:
            count = self.count
            self._list = new_list
            self._physical_index_start = 0
            self._physical_index_end = count
            self._inverted = False
        else:
            self._list = new_list
            self._physical_index_start = 0
            self._physical_index_end = 0
            self._inverted = True

    def _copy_to_list(self, list_: List[T]) -> None:
        # State S, I, E, SE, or EE
        if not self._inverted:
            list_[0:self.count] = self._list[self._physical_index_start:self._physical_index_end]
        else:
            list_[0:(self.capacity - self._physical_index_start)] = self._list[self._physical_index_start:self.capacity]
            list_[(self.capacity - self._physical_index_start):self.count] = self._list[0:self._physical_index_end]

    @property
    def capacity(self) -> int:
        # State S, I, E, SE, or EE
        return len(self._list)

    @property
    def capacity_factor(self) -> float:
        # State S, I, E, SE, or EE
        return self._capacity_factor

    @capacity_factor.setter
    def capacity_factor(self, value: float) -> None:
        """
        ## Specification Domain

        - 0 < value
        """
        # State S, I, E, SE, or EE
        self._capacity_factor = value

    def trim_capacity(self) -> None:
        # State S, I, E, SE, or EE
        if self.count != 0:
            self._reallocate(self.count)
        else:
            self._reallocate(1)

    def _to_S(self) -> None:
        self._index = None
        self._is_at_end = False

    def _to_I(self) -> None:
        self._is_at_end = False

    def _to_E(self) -> None:
        self._index = None
        self._is_at_end = True


class FifoManager(ManagedFifo[T]):

    class ReferenceCounter:

        @staticmethod
        def make() -> 'FifoManager.ReferenceCounter':
            instance = FifoManager.ReferenceCounter()
            FifoManager.ReferenceCounter._setup(instance)
            return instance

        @staticmethod
        def _setup(instance: 'FifoManager.ReferenceCounter') -> None:
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
        instance = FifoManager()
        FifoManager._setup(instance, fifo)
        return instance

    @staticmethod
    def _setup(instance: 'FifoManager', fifo: Fifo[T]) -> None:
        instance._refcounters = []
        instance._ref_token_dict = {}
        instance._current_reference_token = 0
        instance._fifo = fifo
        FifoManager._initialize_ref_counters(instance)

    @staticmethod
    def _initialize_ref_counters(instance: 'FifoManager') -> None:
        count = instance._fifo.count
        while (count != 0):
            instance._refcounters.append(FifoManager.ReferenceCounter.make())
            count = count - 1

    MAX_ACTIVE_REFERENCES = sys.maxsize

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
        self._refcounters.append(FifoManager.ReferenceCounter.make())
        self.collect_garbage()

    def collect_garbage(self) -> None:
        while self._can_shift:
            self.inner_object.shift()
            self._refcounters.pop(0)

    @property
    def _can_shift(self) -> bool:
        result = None
        if len(self._refcounters) != 0: # not self.is_empty (optimized)
            if self.has_current_item: # State I
                # I -> I
                result = (self._refcounters[0].is_at_zero) and (self.current_index != 0)
            elif self.is_at_start: # State S (out of order) (optimized)
                # S -> S
                result = False
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
            raise RuntimeError('Reached maximum number of active strong references: ' + FifoManager.MAX_ACTIVE_REFERENCES + '. You must release some references to continue.')
        return ref_token

    def _next_reference_token(self, ref_token: int) -> int:
        result = None
        if ref_token != FifoManager.MAX_ACTIVE_REFERENCES:
            result = ref_token + 1
        else:
            result = 0
        return result

    def _current_reference_counter(self) -> 'FifoManager.ReferenceCounter[T]':
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


class FifoStateCacheWrapper(Fifo[T]):
    """
    Memoizes Fifo state queries.
    """

    @staticmethod
    def make(fifo: Fifo[T]) -> 'FifoStateCacheWrapper[T]':
        instance = FifoStateCacheWrapper()
        FifoStateCacheWrapper._setup(instance, fifo)
        return instance

    @staticmethod
    def _setup(instance: 'FifoStateCacheWrapper[T]', fifo: Fifo[T]) -> None:
        instance._fifo = fifo
        instance._current_item_valid = False
        instance._current_item = None
        instance._has_current_item_valid = False
        instance._has_current_item = None
        instance._is_at_start_valid = False
        instance._is_at_start = None
        instance._is_at_end_valid = False
        instance._is_at_end = None
        instance._count_valid = False
        instance._count = None
        instance._current_index_valid = False
        instance._current_index = None
        instance._is_empty_valid = False
        instance._is_empty = None

    @property
    def current_item(self) -> T:
        if self._current_item_valid:
            return self._current_item
        else:
            self._current_item = self.inner_object.current_item
            self._current_item_valid = True
            return self._current_item

    @property
    def has_current_item(self) -> bool:
        if self._has_current_item_valid:
            return self._has_current_item
        else:
            self._has_current_item = self.inner_object.has_current_item
            self._has_current_item_valid = True
            return self._has_current_item

    @property
    def is_at_start(self) -> bool:
        if self._is_at_start_valid:
            return self._is_at_start
        else:
            self._is_at_start = self.inner_object.is_at_start
            self._is_at_start_valid = True
            return self._is_at_start

    @property
    def is_at_end(self) -> bool:
        if self._is_at_end_valid:
            return self._is_at_end
        else:
            self._is_at_end = self.inner_object.is_at_end
            self._is_at_end_valid = True
            return self._is_at_end

    def move_to_next(self) -> None:
        self.inner_object.move_to_next()
        self._current_item_valid = False
        self._current_item = None
        self._has_current_item_valid = False
        self._has_current_item = None
        self._is_at_start_valid = True
        self._is_at_start = False
        self._is_at_end_valid = False
        self._is_at_end = None
        self._current_index_valid = False
        self._current_index = None

    def move_to_end(self) -> None:
        self.inner_object.move_to_end()
        self._current_item_valid = False
        self._current_item = None
        self._has_current_item_valid = True
        self._has_current_item = False
        self._is_at_start_valid = True
        self._is_at_start = False
        self._is_at_end_valid = True
        self._is_at_end = True
        self._current_index_valid = False
        self._current_index = None

    @property
    def count(self) -> int:
        if self._count_valid:
            return self._count
        else:
            self._count = self.inner_object.count
            self._count_valid = True
            return self._count

    @property
    def current_index(self) -> int:
        if self._current_index_valid:
            return self._current_index
        else:
            self._current_index = self.inner_object.current_index
            self._current_index_valid = True
            return self._current_index

    @property
    def is_empty(self) -> bool:
        if self._is_empty_valid:
            return self._is_empty
        else:
            self._is_empty = self.inner_object.is_empty
            self._is_empty_valid = True
            return self._is_empty

    def move_to_start(self) -> None:
        self.inner_object.move_to_start()
        self._current_item_valid = False
        self._current_item = None
        self._has_current_item_valid = True
        self._has_current_item = False
        self._is_at_start_valid = True
        self._is_at_start = True
        self._is_at_end_valid = True
        self._is_at_end = False
        self._current_index_valid = False
        self._current_index = None

    def move_to_index(self, index: int) -> None:
        self.inner_object.move_to_index(index)
        self._current_item_valid = False
        self._current_item = None
        self._has_current_item_valid = True
        self._has_current_item = True
        self._is_at_start_valid = True
        self._is_at_start = False
        self._is_at_end_valid = True
        self._is_at_end = False
        self._current_index_valid = True
        self._current_index = index

    def push(self, item: T) -> None:
        self.inner_object.push(item)
        self._count_valid = False
        self._count = None
        self._current_index_valid = False
        self._current_index = None
        self._is_empty_valid = True
        self._is_empty = False

    def shift(self) -> None:
        self.inner_object.shift()
        self._current_item_valid = False
        self._current_item = None
        self._has_current_item_valid = False
        self._has_current_item = None
        self._count_valid = False
        self._count = None
        self._current_index_valid = False
        self._current_index = None
        self._is_empty_valid = False
        self._is_empty = None

    @property
    def inner_object(self) -> Fifo[T]:
        return self._fifo


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


del T


