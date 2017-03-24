from autorecurse.lib.iterator import Iterator, IteratorConcatenator, IteratorContext, ListIterator
from autorecurse.gnumake.data import Makefile, Target
from autorecurse.gnumake.parse import Factory
from autorecurse.gnumake.storage import StorageEngine
from abc import ABCMeta, abstractmethod
from subprocess import Popen, PIPE, CalledProcessError
from typing import List
import os


class TargetReader(metaclass=ABCMeta):

    class Context(IteratorContext[Target], metaclass=ABCMeta):

        @staticmethod
        def _setup(instance: 'TargetReader.Context', parent: 'TargetReader', makefile: Makefile) -> None:
            instance._parent = parent
            instance._makefile = makefile
            instance._process = None

        def __enter__(self) -> Iterator[Target]:
            self._process = self._spawn_subprocess()
            return Factory.make_target_iterator_for_file(self._process.stdout, self._makefile)

        def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
            if self._process is not None:
                self._process.stdout.close()
                self._process.wait()
                self._check_returncode()
            return False

        def _check_returncode(self) -> None:
            if self._process.returncode != 0:
                raise CalledProcessError(self._process.returncode, ' '.join(self._process.args))

        @abstractmethod
        def _spawn_subprocess(self) -> Popen:
            pass

    @staticmethod
    def _setup(instance: 'TargetReader', executable_name: str) -> None:
        instance._executable_name = executable_name

    @property
    def executable_name(self) -> str:
        return self._executable_name

    @abstractmethod
    def target_iterator(self, makefile: Makefile) -> IteratorContext[Target]:
        pass


class TargetListingTargetReader(TargetReader):

    class Context(TargetReader.Context):

        @staticmethod
        def make(parent: 'TargetListingTargetReader', makefile: Makefile) -> IteratorContext[Target]:
            instance = TargetListingTargetReader.Context()
            TargetReader.Context._setup(instance, parent, makefile)
            return instance

        def _check_returncode(self) -> None:
            pass

        def _spawn_subprocess(self) -> Popen:
            args = []
            args.append(self._parent.executable_name)
            args.append('-np')
            args.append('-C')
            args.append(self._makefile.exec_path)
            args.append('-f')
            args.append(self._makefile.file_path)
            return Popen(args, stdout=PIPE, universal_newlines=True)

    @staticmethod
    def make(executable_name: str) -> 'TargetListingTargetReader':
        instance = TargetListingTargetReader()
        TargetReader._setup(instance, executable_name)
        return instance

    def target_iterator(self, makefile: Makefile) -> IteratorContext[Target]:
        return TargetListingTargetReader.Context.make(self, makefile)


class NestedRuleTargetReader(TargetReader):

    class Context(TargetReader.Context):

        @staticmethod
        def make(parent: 'NestedRuleTargetReader', makefile: Makefile) -> IteratorContext[Target]:
            instance = NestedRuleTargetReader.Context()
            TargetReader.Context._setup(instance, parent, makefile)
            return instance

        def _check_returncode(self) -> None:
            pass

        def _spawn_subprocess(self) -> Popen:
            target_listing_file = self._parent._storage_engine.target_listing_file_path(self._makefile)
            args = []
            args.append(self._parent.executable_name)
            args.append('-np')
            args.append('-C')
            args.append(self._makefile.exec_path)
            args.append('-f')
            args.append(self._makefile.file_path)
            args.append('-f')
            args.append(target_listing_file)
            args.append('autorecurse-all-targets')
            return Popen(args, stdout=PIPE, universal_newlines=True)

    @staticmethod
    def make(executable_name: str, storage_engine: StorageEngine) -> 'NestedRuleTargetReader':
        instance = NestedRuleTargetReader()
        TargetReader._setup(instance, executable_name)
        instance._storage_engine = storage_engine
        return instance

    def target_iterator(self, makefile: Makefile) -> IteratorContext[Target]:
        return NestedRuleTargetReader.Context.make(self, makefile)


class DirectoryMakefileLocator(metaclass=ABCMeta):

    @abstractmethod
    def makefile_iterator(self, directory_path: str) -> IteratorContext[Makefile]:
        pass


class PriorityMakefileLocator(DirectoryMakefileLocator):

    def _setup(instance: 'PriorityMakefileLocator') -> None:
        instance._priorities = {}

    def set_filename_priorities(self, filenames: List[str]) -> None:
        self._priorities = {}
        index = len(filenames)
        for name in filenames:
            self._priorities[name] = index
            index = index - 1

    def _get_best_name(self, filenames: List[str]) -> str:
        best_name = None
        best_priority = 0
        for name in filenames:
            if name in self._priorities:
                priority = self._priorities[name]
                if best_priority < priority:
                    best_name = name
                    best_priority = priority
        return best_name


class NestedMakefileLocator(PriorityMakefileLocator):

    class Context(IteratorContext[Makefile]):

        @staticmethod
        def make(parent: 'NestedMakefileLocator', directory_path: str) -> IteratorContext[Makefile]:
            instance = NestedMakefileLocator.Context()
            instance._parent = parent
            instance._directory_path = directory_path
            return instance

        def __enter__(self) -> Iterator[Makefile]:
            list_ = []
            first_directory = True
            for dirpath, dirnames, filenames in os.walk(self._directory_path):
                name = self._parent._get_best_name(filenames)
                if name is not None:
                    if not first_directory:
                        abs_path = os.path.realpath(os.path.join(os.getcwd(), dirpath))
                        list_.append(Makefile.make_with_exec_path(abs_path, name))
                else:
                    dirnames.clear()
                if first_directory:
                    first_directory = False
            return ListIterator.make(list_)

        def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
            return False

    def make() -> 'NestedMakefileLocator':
        instance = NestedMakefileLocator()
        PriorityMakefileLocator._setup(instance)
        return instance

    def makefile_iterator(self, directory_path: str) -> IteratorContext[Makefile]:
        return NestedMakefileLocator.Context.make(self, directory_path)


class BaseMakefileLocator(PriorityMakefileLocator):

    class Context(IteratorContext[Makefile]):

        @staticmethod
        def make(parent: 'BaseMakefileLocator', directory_path: str) -> IteratorContext[Makefile]:
            instance = BaseMakefileLocator.Context()
            instance._parent = parent
            instance._directory_path = directory_path
            return instance

        def __enter__(self) -> Iterator[Makefile]:
            filenames = []
            for entry in os.scandir(self._directory_path):
                if entry.is_file():
                    filenames.append(entry.name)
            list_ = []
            name = self._parent._get_best_name(filenames)
            if name is not None:
                abs_path = os.path.realpath(os.path.join(os.getcwd(), self._directory_path))
                list_.append(Makefile.make_with_exec_path(abs_path, name))
            return ListIterator.make(list_)

        def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
            return False

    def make() -> 'BaseMakefileLocator':
        instance = BaseMakefileLocator()
        PriorityMakefileLocator._setup(instance)
        return instance

    def makefile_iterator(self, directory_path: str) -> IteratorContext[Makefile]:
        return BaseMakefileLocator.Context.make(self, directory_path)


