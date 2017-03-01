from io import StringIO, TextIOBase
from antlr4 import InputStream, Token
from lib.generics import Iterator, LinkedFifo, FifoGlobalIndexWrapper, FifoToManagedFifoAdapter


class IteratorToInputStreamAdapter(Iterator[str], InputStream):
    """
    ## Transition System Definition

    ### States

    - I = Intermediate, Non-empty buffer
    - E = End, Not-empty buffer
    - EE = End, Empty buffer

    ### Transition Labels

    - Consume = Client calls consume
    - Next = Client calls move_to_next
    - End = Client calls move_to_end

    ### Transitions Grouped by Label

    - Consume
      - I -> I
      - I -> E
    - Next
      - I -> I
      - I -> E
    - End
      - I -> E
      - E -> E
      - EE -> EE

    ## Call State Validity

    For each method listed, client is allowed to call the method in the
    given states.

    - consume: I
    - current_item (getter): I
    - has_current_item (getter): I E EE
    - is_at_start (getter): I E EE
    - is_at_end (getter): I E EE
    - move_to_next: I
    - move_to_end: I E EE

    ## Call Argument Validity

    For each method listed, client is allowed to call the method with
    the given parameters.

    - LA(self, offset: int)
      - offset is in self._buffer
    - seek(self, _index: int)
      - _index >= 0
      - _index < self.index -> _index is in self._buffer

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

    Notes:

    - We are never at start state. InputStream only has intermediate
      state and end state.
    - In intermediate state, self.index < self.size.
    - In end state, self.index == self.size.
    """

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
        if self._buffer.current_index + 1 != self._buffer.count:
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
                # I -> E
                self._buffer.move_to_next()

    def move_to_end(self) -> None:
        if self._is_I: # State I
        elif self._is_E: # State E
            # Already at end
            pass
        else: # State EE
            # Already at end
            pass

    @property
    def index(self) -> int:
        result = None
        if self.has_current_item: # State I
            result = self._buffer_global.current_global_index
        else: # State E or EE
            result = self.size
        return result

    @property
    def size(self) -> int:
        # State I, E, or EE
        return self._buffer_global.global_count

    def reset(self) -> None:
        raise NotImplementedError()

    def consume(self) -> None:
        if self.has_current_item: # State I
            self.move_to_next()
        else: # State E or EE
            raise Exception('cannot consume EOF')

    def LA(self, offset: int) -> int:
        if offset == 0:
            return 0
        if offset < 0:
            index = self.index + offset
        else:
            index = self.index + offset - 1
        if index < 0:
            return Token.EOF
        result = None
        if self.has_current_item: # State I
            current_global_index = self.index
            ref_token = self._buffer.new_strong_reference()
            self.seek(index)
            if self.has_current_item: # State I
                result = ord(self.current_item)
            else: # State E
                result = Token.EOF
            self.seek(current_global_index)
            self._buffer.release_strong_reference(ref_token)
        elif not self._buffer.is_empty: # State E
            current_global_index = self.index
            self.seek(index)
            if self.has_current_item: # State I
                result = ord(self.current_item)
            else: # State E
                result = Token.EOF
            self.seek(current_global_index)
        else: # State EE
            result = Token.EOF
        return result

    def mark(self) -> int:
        result = None
        if self.has_current_item: # State I
            result = self._buffer.new_strong_reference()
        elif not self._buffer.is_empty: # State E
            result = -1
        else: # State EE
            result = -1
        return result

    def release(self, marker: int) -> None:
        self._buffer.release_strong_reference(marker)

    def seek(self, _index: int) -> None:
        if self.has_current_item: # State I
            if _index >= self.index:
                if _index >= self.size:
                    self._buffer_global.move_to_global_index(self.size - 1)
                    diff = _index - self.index
                    while not (diff == 0 or self.is_at_end):
                        self.move_to_next()
                        diff = diff - 1
                else:
                    self._buffer_global.move_to_global_index(_index)
            else:
                self._buffer_global.move_to_global_index(_index)
        elif not self._buffer.is_empty: # State E
            if _index >= self.index:
                # Already at end
                pass
            else:
                self._buffer_global.move_to_global_index(_index)
        else: # State EE
            if _index >= self.index:
                # Already at end
                pass
            else:
                # Buffer is empty
                # This is unreachable code, since it violates the argument validity rules
                pass

    def getText(self, start: int, stop: int) -> str:
        with StringIO() as strbuffer:
            if self.has_current_item: # State I
                current_global_index = self.index
                ref_token = self._buffer.new_strong_reference()
                self.seek(start)
                length = stop - start + 1
                self._write_text(strbuffer, length)
                self.seek(current_global_index)
                self._buffer.release_strong_reference(ref_token)
            elif not self._buffer.is_empty: # State E
                current_global_index = self.index
                self.seek(start)
                length = stop - start + 1
                self._write_text(strbuffer, length)
                self.seek(current_global_index)
            else: # State EE
                pass
            return strbuffer.getvalue()

    def _write_text(self, buffer_: TextIOBase, length: int) -> None:
        count = length
        while self.has_current_item and (count != 0):
            buffer_.write(self.current_item)
            self.move_to_next()
            count = count - 1

    def _is_I(self) -> bool:
        return self.has_current_item

    def _is_E(self) -> bool:
        return self.is_at_end and (not self._buffer.is_empty)

    def _is_EE(self) -> bool:
        return self.is_at_end and self._buffer.is_empty


