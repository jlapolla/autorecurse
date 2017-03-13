from abc import ABCMeta, abstractmethod
from autorecurse.lib.generics import *
from antlr4.error.Errors import ParseCancellationException
from autorecurse.app.make.gnu.grammar import MakefileRuleParser
import os
import typing


class Makefile:

    @staticmethod
    def make(path: str) -> 'Makefile':
        instance = Makefile()
        Makefile._setup(instance, path)
        return instance

    @staticmethod
    def _setup(instance: 'Makefile', path: str) -> None:
        instance._exec_path = os.path.dirname(path)
        instance._file_path = os.path.basename(path)

    @staticmethod
    def make_with_exec_path(exec_path: str, file_path: str) -> 'Makefile':
        instance = Makefile()
        Makefile._setup_with_exec_path(instance, exec_path, file_path)
        return instance

    @staticmethod
    def _setup_with_exec_path(instance: 'Makefile', exec_path: str, file_path: str) -> None:
        instance._exec_path = exec_path
        instance._file_path = file_path

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
        instance._makefile = None
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
        self._target.file = self.makefile

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

    @property
    def makefile(self) -> Makefile:
        return self._makefile

    @makefile.setter
    def makefile(self, value: Makefile) -> None:
        self._makefile = value


class MakefileTargetReader(metaclass=ABCMeta):

    @abstractmethod
    def target_iterator(self, makefile: Makefile) -> IteratorContext[MakefileTarget]:
        pass


class SubMakefileLocator(metaclass=ABCMeta):

    @abstractmethod
    def makefile_iterator(self, makefile: Makefile) -> IteratorContext[Makefile]:
        pass


class DirectoryMakefileLocator(metaclass=ABCMeta):

    @abstractmethod
    def makefile_iterator(self, directory_path: str) -> IteratorContext[Makefile]:
        pass


class PriorityMakefileIterator(DirectoryMakefileLocator):
    """
    Picks one Makefile in a directory based on a priority list of
    potential Makefile file names. The file with the highest priority
    name is picked.
    """

    class Context(IteratorContext[Makefile]):

        @staticmethod
        def make(parent: 'PriorityMakefileIterator', directory_path: str) -> IteratorContext[Makefile]:
            instance = PriorityMakefileIterator.Context()
            PriorityMakefileIterator.Context._setup(instance, parent, directory_path)
            return instance

        @staticmethod
        def _setup(instance: 'PriorityMakefileIterator.Context', parent: 'PriorityMakefileIterator', directory_path: str) -> None:
            instance._parent = parent
            instance._directory_path = directory_path

        def __enter__(self) -> Iterator[Makefile]:
            list_ = []
            file_path = self._get_best_name()
            if file_path is not None:
                list_.append(Makefile.make_with_exec_path(self._directory_path, file_path))
            return ListIterator.make(list_)

        def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
            return False

        def _get_best_name(self) -> str:
            best_name = None
            best_priority = 0
            for name in self._get_file_names():
                if name in self._parent._priorities:
                    priority = self._parent._priorities[name]
                    if best_priority < priority:
                        best_name = name
                        best_priority = priority
            return best_name

        def _get_file_names(self) -> typing.List[str]:
            """
            ## Suggestions

            - Use os.scandir directly (used internally by os.walk).
            """
            it = os.walk(self._directory_path)
            return it.__next__()[2]

    @staticmethod
    def make(priorities: typing.List[str]) -> MakefileTargetReader:
        instance = PriorityMakefileIterator()
        PriorityMakefileIterator._setup(instance, priorities)
        return instance

    @staticmethod
    def _setup(instance: 'PriorityMakefileIterator', priorities: typing.List[str]) -> None:
        instance._priorities = {}
        PriorityMakefileIterator._init_priorities(instance, priorities)

    @staticmethod
    def _init_priorities(instance: 'PriorityMakefileIterator', priorities: typing.List[str]) -> None:
        index = len(priorities)
        for name in priorities:
            instance._priorities[name] = index
            index = index - 1

    def makefile_iterator(self, directory_path: str) -> IteratorContext[Makefile]:
        return PriorityMakefileIterator.Context.make(self, directory_path)


class RecursiveDirectoryMakefileLocator(DirectoryMakefileLocator):
    """
    Returns Makefiles found by another DirectoryMakefileLocator in a
    directory and all its subdirectories.
    """

    class Iterator(Iterator[Iterator[Makefile]]):

        @staticmethod
        def make(parent: 'RecursiveDirectoryMakefileLocator', walker_iterator) -> 'RecursiveDirectoryMakefileLocator.Iterator':
            """
            ## Specification Domain

            - walker_iterator is an iterator returned from os.walk.
            """
            instance = RecursiveDirectoryMakefileLocator.Iterator()
            RecursiveDirectoryMakefileLocator.Iterator._setup(instance, parent, walker_iterator)
            return instance

        @staticmethod
        def _setup(instance: 'RecursiveDirectoryMakefileLocator.Iterator', parent: 'RecursiveDirectoryMakefileLocator', walker_iterator) -> None:
            instance._directory_walker = walker_iterator
            instance._parent = parent
            instance._to_S()

        @property
        def current_item(self) -> Makefile:
            return self._current_item

        @property
        def has_current_item(self) -> bool:
            return self._current_item is not None

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
                self._move_to_next_directory()
            else: # State I
                # I -> I
                # I -> E
                self._close_current_context()
                self._move_to_next_directory()

        def move_to_end(self) -> None:
            if self.is_at_start: # State S
                # S -> E
                self._to_E()
            elif self.has_current_item: # State I
                # I -> E
                self._close_current_context()
                self._to_E()
            else: # State E
                # E -> E
                self._to_E()

        def _close_current_context(self) -> None:
            # State I
            # self._current_context != None
            # self._current_item != None
            context = self._current_context
            self._current_context = None
            self._current_item = None
            context.__exit__(None, None, None)

        def _move_to_next_directory(self) -> None:
            # State S or I
            # self._current_context == None
            # self._current_item == None
            try:
                self._current_tuple = self._directory_walker.__next__()
            except StopIteration:
                self._to_E()
            else:
                context = self._parent._locator.makefile_iterator(self._current_tuple[0])
                item = context.__enter__()
                self._current_context = context
                self._current_item = item
                self._trim_excluded_directory_names()
                self._to_I()

        def _trim_excluded_directory_names(self) -> None:
            directories = self._current_tuple[1]
            index = 0
            length = len(directories)
            while index != length:
                if directories[index] in self._parent._excluded_directory_names:
                    del directories[index]
                    length = length - 1
                else:
                    index = index + 1

        def _to_S(self) -> None:
            self._current_context = None
            self._current_item = None
            self._current_tuple = None
            self._is_at_end = False

        def _to_I(self) -> None:
            self._is_at_end = False

        def _to_E(self) -> None:
            self._current_context = None
            self._current_item = None
            self._current_tuple = None
            self._is_at_end = True

    class Context(IteratorContext[Makefile], Iterator):

        @staticmethod
        def make(parent: 'RecursiveDirectoryMakefileLocator', directory_path: str) -> IteratorContext[Makefile]:
            instance = RecursiveDirectoryMakefileLocator.Context()
            RecursiveDirectoryMakefileLocator.Context._setup(instance, parent, directory_path)
            return instance

        @staticmethod
        def _setup(instance: 'RecursiveDirectoryMakefileLocator.Context', parent: 'RecursiveDirectoryMakefileLocator', directory_path: str) -> None:
            instance._parent = parent
            instance._directory_path = directory_path

        def __enter__(self) -> Iterator[Makefile]:
            RecursiveDirectoryMakefileLocator.Iterator._setup(self, self._parent, os.walk(self._directory_path))
            return IteratorConcatenator.make(self)

        def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
            if self._current_context is None:
                return False
            else:
                return self._current_context.__exit__(exc_type, exc_val, exc_tb)

    @staticmethod
    def make(locator: DirectoryMakefileLocator) -> MakefileTargetReader:
        instance = RecursiveDirectoryMakefileLocator()
        RecursiveDirectoryMakefileLocator._setup(instance, locator)
        return instance

    @staticmethod
    def _setup(instance: 'RecursiveDirectoryMakefileLocator', locator: DirectoryMakefileLocator) -> None:
        instance._locator = locator
        instance._excluded_directory_names = set()

    def exclude_directory_name(self, directory_name: str) -> None:
        self._excluded_directory_names.add(directory_name)

    def include_directory_name(self, directory_name: str) -> None:
        self._excluded_directory_names.discard(directory_name)

    def makefile_iterator(self, directory_path: str) -> IteratorContext[Makefile]:
        return RecursiveDirectoryMakefileLocator.Context.make(self, directory_path)


