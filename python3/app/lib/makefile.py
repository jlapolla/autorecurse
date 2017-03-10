from abc import ABCMeta, abstractmethod
from lib.generics import ListIterator, Iterator, IteratorContext
from antlr4.error.Errors import ParseCancellationException
from app.antlr.grammar import MakefileRuleParser
import os


class Makefile:

    @staticmethod
    def make(path: str) -> 'Makefile':
        instance = Makefile()
        Makefile._setup(instance, path)
        return instance

    @staticmethod
    def _setup(instance: 'Makefile', path: str) -> None:
        instance._exec_path = os.path.split(path)[0]
        instance._file_path = os.path.split(path)[1]

    @property
    def path(self) -> str:
        """
        Path to the Makefile.
        """
        if not os.path.isabs(self.file_path): # file_path is relative
            if len(self.exec_path) == 0: # exec_path is empty
                return self.file_path
            elif not os.path.isabs(self.exec_path): # exec_path is relative
                return os.path.join(self.exec_path, self.file_path)
            else: # exec_path is absolute
                return os.path.join(self.exec_path, self.file_path)
        else: # file_path is absolute
            # exec_path is empty
            # exec_path is relative
            # exec_path is absolute
            return self.file_path

    @property
    def exec_path(self) -> str:
        """
        Path that make should be run from (-C option).

        ## Notes

        - Empty exec_path will not generate a -C option.
        """
        return self._exec_path

    @exec_path.setter
    def exec_path(self, value: str) -> None:
        self._exec_path = value

    @property
    def file_path(self) -> str:
        """
        Path to file that make should be run on (-f option).
        """
        return self._file_path

    @file_path.setter
    def file_path(self, value: str) -> None:
        self._file_path = value


class MakefileTarget:

    @staticmethod
    def make_from_parse_context(context: MakefileRuleParser.MakefileRuleContext, target_index: int) -> 'MakefileTarget':
        instance = MakefileTarget()
        MakefileTarget._setup_from_parse_context(instance, context, target_index)
        return instance

    @staticmethod
    def _setup_from_parse_context(instance: 'MakefileTarget', context: MakefileRuleParser.MakefileRuleContext, target_index: int) -> None:
        instance._file = None
        instance._path = context.target(target_index).IDENTIFIER().symbol.text
        instance._prerequisites = []
        for prerequisite in context.prerequisite():
            instance._prerequisites.append(prerequisite.IDENTIFIER().symbol.text)
        instance._order_only_prerequisites = []
        for order_only_prerequisite in context.orderOnlyPrerequisite():
            instance._order_only_prerequisites.append(order_only_prerequisite.IDENTIFIER().symbol.text)

    @property
    def file(self) -> Makefile:
        return self._file

    @file.setter
    def file(self, value: Makefile) -> None:
        self._file = value

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, value: str) -> None:
        self._path = value

    @property
    def prerequisites(self) -> Iterator[str]:
        return ListIterator.make(self._prerequisites)

    @property
    def order_only_prerequisites(self) -> Iterator[str]:
        return ListIterator.make(self._order_only_prerequisites)


class MakefileRuleParserToIteratorAdapter(Iterator[MakefileTarget]):

    @staticmethod
    def make(parser: MakefileRuleParser) -> Iterator[MakefileTarget]:
        instance = MakefileRuleParserToIteratorAdapter()
        MakefileRuleParserToIteratorAdapter._setup(instance, parser)
        return instance

    @staticmethod
    def _setup(instance: 'MakefileRuleParserToIteratorAdapter', parser: MakefileRuleParser) -> None:
        instance._parser = parser
        instance._to_S()

    @property
    def current_item(self) -> MakefileTarget:
        return self._target

    @property
    def has_current_item(self) -> bool:
        return self._target is not None

    @property
    def is_at_start(self) -> bool:
        return not (self.has_current_item or self.is_at_end)

    @property
    def is_at_end(self) -> bool:
        return self._is_at_end

    def move_to_next(self) -> None:
        if self.is_at_start: # State S
            # S -> I
            # S -> E
            self._get_next_target()
        else: # State I
            if self._index + 1 != self._current_length:
                # I -> I
                self._index = self._index + 1
                self._generate_target()
            else:
                # I -> I
                # I -> E
                self._index = 0
                self._get_next_target()

    @property
    def _current_length(self) -> int:
        if self.is_at_start: # State S
            return 0
        elif self.has_current_item: # State I
            return len(self._context.target())
        else: # State E
            return 0

    def _get_next_target(self) -> None:
        # State S or I
        self._get_next_non_empty_context()
        if not self.is_at_end:
            # S -> I
            # I -> I
            self._generate_target()
            self._to_I()
        else:
            # S -> E
            # I -> E
            # Already at state E
            pass

    def _generate_target(self) -> None:
        self._target = MakefileTarget.make_from_parse_context(self._context, self._index)

    def _get_next_non_empty_context(self) -> None:
        # State S or I
        self._get_next_context()
        while not ((self._context is not None) or self.is_at_end):
            self._get_next_context()

    def _get_next_context(self) -> None:
        # State S or I
        ctx = None
        try:
            ctx = self._parser.declaration()
        except ParseCancellationException:
            self._to_E()
        else:
            self._context = ctx.makefileRule()

    def _to_S(self) -> None:
        self._index = 0
        self._target = None
        self._context = None
        self._is_at_end = False

    def _to_I(self) -> None:
        self._is_at_end = False

    def _to_E(self) -> None:
        self._index = 0
        self._target = None
        self._context = None
        self._is_at_end = True


class MakefileTargetReader(metaclass=ABCMeta):

    @abstractmethod
    def target_iterator(self, makefile: Makefile) -> IteratorContext[MakefileTarget]:
        pass


