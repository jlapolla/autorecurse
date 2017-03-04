from abc import ABCMeta, abstractmethod
from io import StringIO, TextIOBase
from antlr4 import InputStream, Token
from lib.generics import Iterator, LinkedFifo, FifoGlobalIndexWrapper, FifoToManagedFifoAdapter
from app.antlr.abstract import IntStream, CharStream, TokenStream
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
            self._load_one_item_from_iterator()
            self._buffer.move_to_next()

    @property
    def _has_more_buffer(self) -> bool:
        # State I
        return self._buffer.current_index + 1 != self._buffer.count

    def _load_one_item_from_iterator(self) -> None:
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
        index = self._offset_to_index(offset)
        result = None
        if self._is_I: # State I
            ref_token = self._buffer.new_strong_reference()
            try:
                original_index = self.index
                self.seek(index)
                result = self._LA_result
                self.seek(original_index)
            finally:
                self._buffer.release_strong_reference(ref_token)
        else: # State E or EE
            original_index = self.index
            self.seek(index)
            result = self._LA_result
            self.seek(original_index)
        return result

    def _offset_to_index(self, offset: int) -> int:
        result = self.index + offset
        if offset > 0:
            result = result - 1
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


class IteratorToCharStreamAdapter(IteratorToIntStreamAdapter[str], CharStream):
    """
    ## Call State Validity

    For each method listed, client is allowed to call the method in the
    given states.

    - getText: I E EE

    ## Call Argument Validity

    For each method listed, client is allowed to call the method with
    the given parameters.

    - getText(self, start: int, stop: int)
      - 0 <= start (otherwise throws)
      - start <= stop + 1 (otherwise throws)
      - stop < size of stream (otherwise throws)
      - start is in self._buffer (otherwise throws)
    """

    @staticmethod
    def make(iterator: Iterator[str]) -> 'IteratorToCharStreamAdapter':
        instance = IteratorToCharStreamAdapter()
        IteratorToIntStreamAdapter._setup(instance, iterator)
        return instance

    def _item_to_int(self, item: str) -> int:
        return ord(item)

    def getText(self, start: int, stop: int) -> str:
        if (start > stop + 1):
            raise Exception('Cannot get text with start greater than stop plus 1.')
        with StringIO() as strbuffer:
            if self._is_I: # State I
                length = stop - start + 1 # 0 <= length
                ref_token = self._buffer.new_strong_reference()
                try:
                    original_index = self.index
                    self.seek(start) # throws if start < 0 \/ start not in self._buffer
                    self._write_text(strbuffer, length) # throws if stream size <= stop
                    self.seek(original_index)
                finally:
                    self._buffer.release_strong_reference(ref_token)
            else: # State E or EE
                length = stop - start + 1 # 0 <= length
                original_index = self.index
                self.seek(start) # throws if start < 0 \/ start not in self._buffer
                self._write_text(strbuffer, length) # throws if stream size <= stop
                self.seek(original_index)
            return strbuffer.getvalue()

    def _write_text(self, buffer_: TextIOBase, length: int) -> None:
        # State I or E
        count = length
        while self._is_I and (count != 0):
            buffer_.write(self.current_item)
            self.move_to_next()
            count = count - 1
        if count != 0:
            raise Exception('Cannot get text past end of stream.')


class IteratorToTokenStreamAdapter(IteratorToIntStreamAdapter[Token], TokenStream):
    """
    ## Call State Validity

    For each method listed, client is allowed to call the method in the
    given states.

    - get: I E EE
    - LT: I E EE

    ## Call Argument Validity

    For each method listed, client is allowed to call the method with
    the given parameters.

    - get(self, index: int)
      - 0 <= index (otherwise throws)
      - index is in self._buffer \/ index is beyond end of stream
        (otherwise throws)
    - LT(self, offset: int)
      - offset != 0
      - offset is in self._buffer \/ offset is beyond end of stream
        (otherwise throws)

    ## Semantic Differences

    A TokenStream returns a token representing EOF when it reaches EOF.
    Typically, this token is generated by an ANTLR Lexer which
    constructs Token's that are returned by our source Iterator[Token].
    This means that when we get the EOF token, our source
    Iterator.is_at_end still reports False since it still has a current
    item: the EOF token.
    
    However, in ANTLR a TokenStream is conceptually at end when it
    reports the EOF token. Therefore, self.is_at_end must report True as
    soon as we hit the EOF token in the source Iterator[Token]. At the
    same time, we need to return that EOF token from LT when we are at
    end. This means that we never move our source iterator to end state,
    because we always need to be able to refer to that EOF token.

    For example, when we use an IteratorToTokenStreamAdapter through its
    Iterator[Token] interface, we will never see an EOF token, since the
    Iterator[Token] interface reports end state once it pulls an EOF
    token from its source Iterator[Token].

    This also means that the source Iterator[Token] cannot be empty. It
    must produce at least one Token: the EOF token. Again, the source
    Iterator[Token] must produce an EOF token before it reaches end
    state.

    Ultimately the issue is that IteratorToTokenStreamAdapter cannot
    create an EOF token by itself. Only an ANTLR Lexer knows how to
    create an EOF token.
    
    Notice that in IteratorToIntStreamAdapter, we are always able to
    return IntStream.EOF from LA (i.e. we are able to create our end
    signal). IteratorToCharStreamAdapter does not need to create any end
    signal besides that already provided by IteratorToIntStreamAdapter.
    IteratorToTokenStreamAdapter is different because it needs to return
    an end signal that it cannot create itself. Therefore, it relies on
    the source Iterator[Token] to construct the end signal (the EOF
    token).

    On a higher level, we're having this discussion because
    Iterator[Token] uses an out-of-band signal to indicate end state.
    I.e. Iterator[Token] doesn't return a special value from
    current_item to indicate end state, and calling current_item in end
    state is invalid. This allows us to iterate over any item without
    having to reserve a special end item.

    On the other hand, TokenStream uses an in-band signal (a special EOF
    token) to indicate end state.
    """

    @staticmethod
    def make(iterator: Iterator[Token]) -> 'IteratorToTokenStreamAdapter':
        """
        ## Specification Domain

        - iterator.is_at_start and iterator.move_to_next() will make
          iterator.has_current_item True.
        - iterator.has_current_item is True.
        """
        instance = IteratorToTokenStreamAdapter()
        IteratorToTokenStreamAdapter._setup(instance, iterator)
        return instance

    @staticmethod
    def _setup(instance: 'IteratorToTokenStreamAdapter', iterator: Iterator[T]):
        """
        ## Specification Domain

        - iterator.is_at_start and iterator.move_to_next() will make
          iterator.has_current_item True.
        - iterator.has_current_item is True.
        """
        instance._buffer_global = FifoGlobalIndexWrapper.make(LinkedFifo.make())
        instance._buffer = FifoToManagedFifoAdapter.make(instance._buffer_global)
        instance._iterator = iterator
        IteratorToTokenStreamAdapter._initialize_buffer(instance)

    @staticmethod
    def _initialize_buffer(instance: 'IteratorToTokenStreamAdapter'):
        if instance._iterator.is_at_start: # State S
            instance._iterator.move_to_next()
            IteratorToTokenStreamAdapter._initialize_buffer(instance)
        else: # State I
            if not instance._iterator_is_at_eof_token:
                instance._buffer.push(instance._iterator.current_item)
                instance._buffer.move_to_next()
            else:
                instance._buffer.move_to_next()

    def _load_one_item_from_iterator(self) -> None:
        # State I
        if self._iterator.has_current_item: # State I (self._iterator)
            if not self._iterator_is_at_eof_token:
                self._iterator.move_to_next()
                if self._iterator.has_current_item: # State I (self._iterator)
                    if not self._iterator_is_at_eof_token:
                        self._buffer.push(self._iterator.current_item)
                    else:
                        pass
                else: # State E (self._iterator)
                    pass
            else:
                pass
        else: # State E (self._iterator)
            pass

    def _item_to_int(self, item: Token) -> int:
        return item.type

    def get(self, index: int) -> Token:
        result = None
        if self._is_I: # State I
            ref_token = self._buffer.new_strong_reference()
            try:
                original_index = self.index
                self.seek(index)
                result = self._get_result
                self.seek(original_index)
            finally:
                self._buffer.release_strong_reference(ref_token)
        else: # State E or EE
            original_index = self.index
            self.seek(index)
            result = self._get_result
            self.seek(original_index)
        return result

    def _get_result(self) -> Token:
        if self._is_I: # State I
            return self.current_item
        else: # State E or EE
            return self._eof_token

    def LT(self, offset: int) -> Token:
        index = self._offset_to_index(offset)
        return self.get(index)

    @property
    def _total_stream_size(self) -> int:
        if self._is_I: # State I
            ref_token = self._buffer.new_strong_reference()
            try:
                original_index = self.index
                self.move_to_end()
                self.seek(original_index)
            finally:
                self._buffer.release_strong_reference(ref_token)
            return self.size
        else: # State E or EE
            return self.size

    @property
    def _iterator_is_at_eof_token(self) -> bool:
        # State I (self._iterator)
        # self._iterator.has_current_item == True
        return self._iterator.current_item.type == Token.EOF

    @property
    def _eof_token(self) -> Token:
        # State E or EE
        return self._iterator.current_item

del T


