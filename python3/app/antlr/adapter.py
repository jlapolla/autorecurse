from abc import ABCMeta, abstractmethod
from io import StringIO, TextIOBase
from antlr4 import InputStream, Token
from lib.generics import Iterator, LinkedFifo, FifoGlobalIndexWrapper, FifoToManagedFifoAdapter
from app.antlr.abstract import IntStream
from typing import TypeVar


T = TypeVar('T')
class IteratorToIntStreamAdapter(Iterator[T], IntStream):
    """
    ## Transition System Definition

    ### States

    - I = Intermediate, Non-empty buffer
    - E = End, Not-empty buffer
    - EE = End, Empty buffer

    ### Transition Labels

    - Next = Client calls move_to_next
    - End = Client calls move_to_end
    - Consume = Client calls consume
    - Seek = Client calls seek

    ### Transitions Grouped by Label

    - Next
      - I -> I
      - I -> E
    - End
      - I -> E
      - E -> E
      - EE -> EE
    - Consume
      - I -> I
      - I -> E
    - Seek
      - I -> I
      - I -> E
      - E -> I
      - E -> E
      - EE -> EE

    ## Call State Validity

    For each method listed, client is allowed to call the method in the
    given states.

    - current_item (getter): I
    - has_current_item (getter): I E EE
    - is_at_start (getter): I E EE
    - is_at_end (getter): I E EE
    - move_to_next: I
    - move_to_end: I E EE
    - index: I E EE
    - size: I E EE
    - getSourceName: I E EE
    - mark: I E EE
    - release: I E EE
    - LA: I E EE
    - consume: I (E EE throws)
    - seek: I E EE

    ## Call Argument Validity

    For each method listed, client is allowed to call the method with
    the given parameters.

    - LA(self, offset: int)
      - offset != 0
      - offset is in self._buffer \/ offset is beyond end of stream
        (otherwise throws)
    - seek(self, index: int)
      - 0 <= index (otherwise throws)
      - index is in self._buffer \/ index is beyond end of stream
        (otherwise throws)

    ## Call Results

    For each state listed, calling the specified method will return the
    given result.

    - I
      - has_current_item (getter): True
      - is_at_start (getter): False
      - is_at_end (getter): False
    - E
      - has_current_item (getter): False
      - is_at_start (getter): False
      - is_at_end (getter): True
    - EE
      - has_current_item (getter): False
      - is_at_start (getter): False
      - is_at_end (getter): True

    ## State Inference

    - State I <-> self.has_current_item
    - State I <-> self.index < self.size.
    - State E \/ State EE <-> self.is_at_end
    - State E \/ State EE <-> self.index == self.size.

    ## Notes:

    - There is no start state. IntStream only has intermediate state and
      end state.
    - release is tolerant, and may be called with any int. Calling
      release with an invalid int has no effect.
    """

    @staticmethod
    def make(iterator: Iterator[T]) -> 'IteratorToIntStreamAdapter':
        instance = IteratorToIntStreamAdapter()
        IteratorToIntStreamAdapter._setup(instance, iterator)
        return instance

    @staticmethod
    def _setup(instance: 'IteratorToIntStreamAdapter', iterator: Iterator[T]):
        instance._buffer_global = FifoGlobalIndexWrapper.make(LinkedFifo.make())
        instance._buffer = FifoToManagedFifoAdapter.make(instance._buffer_global)
        instance._iterator = iterator
        IteratorToIntStreamAdapter._initialize_buffer(instance)

    @staticmethod
    def _initialize_buffer(instance: 'IteratorToIntStreamAdapter'):
        if instance._iterator.is_at_start: # State S
            instance._iterator.move_to_next()
            IteratorToIntStreamAdapter._initialize_buffer(instance)
        elif instance._iterator.has_current_item: # State I
            instance._buffer.push(instance._iterator.current_item)
            instance._buffer.move_to_next()
        else: # State E
            instance._buffer.move_to_next()

    @property
    def current_item(self) -> T:
        return self._buffer.current_item

    @property
    def has_current_item(self) -> bool:
        return self._buffer.has_current_item

    @property
    def is_at_start(self) -> bool:
        return False

    @property
    def is_at_end(self) -> bool:
        return self._buffer.is_at_end

    def move_to_next(self) -> None:
        # State I
        if self._has_more_buffer:
            # I -> I
            self._buffer.move_to_next()
        else:
            # I -> I
            # I -> E
            self._load_buffer_from_iterator()
            self._buffer.move_to_next()

    @property
    def _has_more_buffer(self) -> bool:
        # State I
        return self._buffer.current_index + 1 != self._buffer.count

    def _load_buffer_from_iterator(self) -> None:
        # State I
        if self._iterator.has_current_item: # State I (self._iterator)
            self._iterator.move_to_next()
            if self._iterator.has_current_item: # State I (self._iterator)
                self._buffer.push(self._iterator.current_item)
            else: # State E (self._iterator)
                pass
        else: # State E (self._iterator)
            pass

    def move_to_end(self) -> None:
        if self._is_I: # State I
            self._buffer.move_to_index(self._buffer.count - 1)
            while not self.is_at_end:
                self.move_to_next()
        elif self._is_E: # State E
            # Already at end
            pass
        else: # State EE
            # Already at end
            pass

    @property
    def index(self) -> int:
        if self._is_I: # State I
            return self._buffer_global.current_global_index
        else: # State E or EE
            return self.size

    @property
    def size(self) -> int:
        # State I, E, or EE
        return self._buffer_global.global_count

    def getSourceName(self) -> str:
        if self._source_name is not None:
            return self._source_name
        else:
            return super().getSourceName()

    def mark(self) -> int:
        if self._is_I: # State I
            # 0 is reserved for states E and EE (see below). We use
            # self._new_strong_refernce_exclude(0) to ensure that 0 is
            # never returned in state I.
            return self._new_strong_reference_exclude(0)
        else: # State E or EE
            # We cannot call self._buffer.new_strong_reference() in
            # states E or EE. But we still have to return an int. So we
            # reserve 0 for states E and EE. Using
            # self._new_strong_reference_exclude(0) to generate
            # reference tokens in state I above ensures that 0 is always
            # an invalid ref_token in self._buffer. Therefore, calling
            # self.release(0) will not accidentally release a ref_token
            # that was returned in state I.
            return 0

    def _new_strong_reference_exclude(self, exclude: int) -> int:
        # State I
        ref_token = self._buffer.new_strong_reference()
        if ref_token == exclude:
            ref_token = self._buffer.new_strong_reference()
            self._buffer.release_strong_reference(exclude)
        return ref_token

    def release(self, marker: int) -> None:
        # State I, E, or EE
        self._buffer.release_strong_reference(marker)
        self._buffer.collect_garbage()

    def LA(self, offset: int) -> int:
        index = self.index + offset
        if offset > 0:
            index = index - 1
        result = None
        if self._is_I: # State I
            original_index = self.index
            ref_token = self._buffer.new_strong_reference()
            self.seek(index)
            result = self._LA_result
            self.seek(original_index)
            self._buffer.release_strong_reference(ref_token)
        else: # State E or EE
            original_index = self.index
            self.seek(index)
            result = self._LA_result
            self.seek(original_index)
        return result

    @property
    def _LA_result(self) -> int:
        if self._is_I: # State I
            return self._item_to_int(self.current_item)
        else: # State E or EE
            return IntStream.EOF

    @abstractmethod
    def _item_to_int(self, item: T) -> int:
        pass

    def consume(self) -> None:
        if self._is_I: # State I
            self.move_to_next()
        else: # State E or EE
            raise Exception('Cannot consume EOF.')

    def seek(self, index: int) -> None:
        if index < 0:
            raise Exception('Cannot seek to negative index.')
        if self._is_I: # State I
            if self.size <= index:
                # I -> I
                # I -> E
                self._buffer.move_to_index(self._buffer.count - 1)
                diff = index - self.index
                while not (diff == 0 or self.is_at_end):
                    self.move_to_next()
                    diff = diff - 1
            else:
                if self._index_is_in_buffer(index):
                    # I -> I
                    self._buffer_global.move_to_global_index(index)
                else:
                    raise Exception('Cannot seek to released index.')
        elif self._is_E: # State E
            if self.size <= index:
                # E -> E
                # Already at E
                pass
            else:
                if self._index_is_in_buffer(index):
                    # E -> I
                    self._buffer_global.move_to_global_index(index)
                else:
                    raise Exception('Cannot seek to released index.')
        else: # State EE
            if self.size <= index:
                # EE -> EE
                # Already at EE
                pass
            else:
                raise Exception('Cannot seek to released index.')

    def _index_is_in_buffer(self, index: int) -> bool:
        # State I, E, or EE
        return (self._lowest_index_in_buffer <= index) and (index < self.size)

    @property
    def _lowest_index_in_buffer(self) -> int:
        # State I, E, or EE
        return self._buffer_global.global_count - self._buffer.count

    @property
    def _is_I(self) -> bool:
        return self.has_current_item

    @property
    def _is_E(self) -> bool:
        return self.is_at_end and (not self._buffer.is_empty)

    @property
    def _is_EE(self) -> bool:
        return self.is_at_end and self._buffer.is_empty

del T


class IteratorToInputStreamAdapter(Iterator[str], InputStream):
    """
    ## Transition System Definition

    ### States

    - I = Intermediate, Non-empty buffer
    - E = End, Not-empty buffer
    - EE = End, Empty buffer

    ### Transition Labels

    - Next = Client calls move_to_next
    - End = Client calls move_to_end
    - Consume = Client calls consume
    - Seek = Client calls seek

    ### Transitions Grouped by Label

    - Next
      - I -> I
      - I -> E
    - End
      - I -> E
      - E -> E
      - EE -> EE
    - Consume
      - I -> I
      - I -> E
    - Seek
      - I -> I
      - I -> E
      - E -> I
      - E -> E
      - EE -> EE

    ## Call State Validity

    For each method listed, client is allowed to call the method in the
    given states.

    - current_item (getter): I
    - has_current_item (getter): I E EE
    - is_at_start (getter): I E EE
    - is_at_end (getter): I E EE
    - move_to_next: I
    - move_to_end: I E EE
    - consume: I (E EE throws)
    - seek: I E EE
    - index: I E EE
    - size: I E EE
    - reset: (I E EE throws)
    - LA: I E EE
    - LT: I E EE
    - mark: I E EE
    - release: I E EE
    - getText: I E EE

    ## Call Argument Validity

    For each method listed, client is allowed to call the method with
    the given parameters.

    - LA(self, offset: int)
      - offset != 0
      - 0 < offset -> offset < self.index -> offset is in self._buffer
    - LT(self, offset: int) # Same as LA
      - offset != 0
      - 0 < offset -> offset < self.index -> offset is in self._buffer
    - seek(self, _index: int)
      - 0 <= _index
      - _index < self.index -> _index is in self._buffer
    - getText(self, start: int, stop: int)
      - 0 <= start
      - 0 <= stop
      - start <= stop
      - start < self.index -> start is in self._buffer

    ## Call Results

    For each state listed, calling the specified method will return the
    given result.

    - I
      - has_current_item (getter): True
      - is_at_start (getter): False
      - is_at_end (getter): False
    - E
      - has_current_item (getter): False
      - is_at_start (getter): False
      - is_at_end (getter): True
    - EE
      - has_current_item (getter): False
      - is_at_start (getter): False
      - is_at_end (getter): True

    ## State Inference

    - State I <-> self.has_current_item
    - State I <-> self.index < self.size.
    - State E \/ State EE <-> self.is_at_end
    - State E \/ State EE <-> self.index == self.size.

    ## Notes:

    - There is no start state. InputStream only has intermediate
      state and end state.
    - release is tolerant, and may be called with any int. Calling
      release with an invalid int has no effect.
    """

    @staticmethod
    def make(iterator: Iterator[str]) -> 'IteratorToInputStreamAdapter':
        instance = IteratorToInputStreamAdapter()
        IteratorToInputStreamAdapter._setup(instance, iterator)
        return instance

    @staticmethod
    def _setup(instance: 'IteratorToInputStreamAdapter', iterator: Iterator[str]):
        instance._buffer_global = FifoGlobalIndexWrapper.make(LinkedFifo.make())
        instance._buffer = FifoToManagedFifoAdapter.make(instance._buffer_global)
        instance._iterator = iterator
        IteratorToInputStreamAdapter._initialize_buffer(instance)

    @staticmethod
    def _initialize_buffer(instance: 'IteratorToInputStreamAdapter'):
        if instance._iterator.is_at_start: # State S
            instance._iterator.move_to_next()
            IteratorToInputStreamAdapter._initialize_buffer(instance)
        elif instance._iterator.has_current_item: # State I
            instance._buffer.push(instance._iterator.current_item)
            instance._buffer.move_to_next()
        else: # State E
            instance._buffer.move_to_next()

    @property
    def current_item(self) -> str:
        return self._buffer.current_item

    @property
    def has_current_item(self) -> bool:
        return self._buffer.has_current_item

    @property
    def is_at_start(self) -> bool:
        return False

    @property
    def is_at_end(self) -> bool:
        return self._buffer.is_at_end

    def move_to_next(self) -> None:
        # State I
        if self._has_more_buffered_text:
            # I -> I
            self._buffer.move_to_next()
        else:
            if self._iterator.has_current_item: # State I
                self._iterator.move_to_next()
                if self._iterator.has_current_item: # State I
                    # I -> I
                    self._buffer.push(self._iterator.current_item)
                    self._buffer.move_to_next()
                else: # State E
                    # I -> E
                    self._buffer.move_to_next()
            else: # State E
                # Unreachable since self._is_I -> self._iterator.has_current_item
                # I -> E
                self._buffer.move_to_next()

    def _has_more_buffered_text(self) -> bool:
        return self._buffer.current_index + 1 != self._buffer.count

    def move_to_end(self) -> None:
        if self._is_I: # State I
            self._buffer_global.move_to_global_index(self.size - 1)
            while not self.is_at_end:
                self.move_to_next()
        elif self._is_E: # State E
            # Already at end
            pass
        else: # State EE
            # Already at end
            pass

    @property
    def index(self) -> int:
        if self._is_I: # State I
            return self._buffer_global.current_global_index
        else: # State E or EE
            return self.size

    @property
    def size(self) -> int:
        # State I, E, or EE
        return self._buffer_global.global_count

    def reset(self) -> None:
        # State I, E, or EE
        raise NotImplementedError()

    def consume(self) -> None:
        if self._is_I: # State I
            self.move_to_next()
        else: # State E or EE
            raise Exception('cannot consume EOF')

    def LA(self, offset: int) -> int:
        if offset == 0: # Defensive. From InputStream source code.
            return 0
        index = None
        if offset < 0:
            index = self.index + offset
        else:
            index = self.index + offset - 1
        if index < 0:
            return Token.EOF
        result = None
        if self._is_I: # State I
            original_index = self.index
            ref_token = self._buffer.new_strong_reference()
            self.seek(index)
            result = self._LA_result
            self.seek(original_index)
            self._buffer.release_strong_reference(ref_token)
        elif self._is_E: # State E
            original_index = self.index
            self.seek(index)
            result = self._LA_result
            self.seek(original_index)
        else: # State EE
            result = Token.EOF
        return result

    @property
    def _LA_result(self) -> int:
        if self._is_I: # State I
            return ord(self.current_item)
        else: # State E or EE
            return Token.EOF

    def mark(self) -> int:
        if self._is_I: # State I
            # Reserve -1 for states E and EE.
            #
            # If client code calls release(-1), we are assured that
            # self._buffer.new_strong_reference never issued -1 as a
            # ref_token. Therefore, -1 is not a ref_token that is
            # recognized by self._buffer, and calling release(-1) will
            # not affect self._buffer.
            return self._new_strong_reference_exclude(-1)
        else: # State E or EE
            return -1

    def _new_strong_reference_exclude(self, exclude: int) -> int:
        # State I
        ref_token = self._buffer.new_strong_reference()
        if ref_token == exclude:
            ref_token = self._buffer.new_strong_reference()
            self._buffer.release_strong_reference(exclude)
        return ref_token

    def release(self, marker: int) -> None:
        # State I, E, or EE
        self._buffer.release_strong_reference(marker)
        self._buffer.collect_garbage()

    def seek(self, _index: int) -> None:
        if self._is_I: # State I
            if _index >= self.index:
                if _index >= self.size:
                    # I -> I
                    # I -> E
                    self._buffer_global.move_to_global_index(self.size - 1)
                    diff = _index - self.index
                    while not (diff == 0 or self.is_at_end):
                        self.move_to_next()
                        diff = diff - 1
                else:
                    # I -> I
                    self._buffer_global.move_to_global_index(_index)
            else:
                # I -> I
                self._buffer_global.move_to_global_index(_index)
        elif self._is_E: # State E
            if _index >= self.index:
                # E -> E
                # Already at E
                pass
            else:
                # E -> I
                self._buffer_global.move_to_global_index(_index)
        else: # State EE
            # EE -> EE
            # Already at EE
            pass

    def getText(self, start: int, stop: int) -> str:
        with StringIO() as strbuffer:
            if self._is_I: # State I
                length = stop - start + 1
                original_index = self.index
                ref_token = self._buffer.new_strong_reference()
                self.seek(start)
                self._write_text(strbuffer, length)
                self.seek(original_index)
                self._buffer.release_strong_reference(ref_token)
            elif self._is_E: # State E
                length = stop - start + 1
                original_index = self.index
                self.seek(start)
                self._write_text(strbuffer, length)
                self.seek(original_index)
            else: # State EE
                pass
            return strbuffer.getvalue()

    def _write_text(self, buffer_: TextIOBase, length: int) -> None:
        # State I, E, or EE
        count = length
        while self._is_I and (count != 0):
            buffer_.write(self.current_item)
            self.move_to_next()
            count = count - 1

    @property
    def _is_I(self) -> bool:
        return self.has_current_item

    @property
    def _is_E(self) -> bool:
        return self.is_at_end and (not self._buffer.is_empty)

    @property
    def _is_EE(self) -> bool:
        return self.is_at_end and self._buffer.is_empty


