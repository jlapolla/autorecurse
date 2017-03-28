from autorecurse.lib.iterator import Iterator, IteratorContext, ListIterator
from autorecurse.lib.file import FileLifetimeManager
from autorecurse.lib.python.argparse import ThrowingArgumentParser
from autorecurse.common.storage import DefaultDirectoryMapping
from autorecurse.gnumake.storage import FileStorageEngine, StorageEngine
from autorecurse.gnumake.data import DefaultTargetFormatter, Makefile, Target
from autorecurse.gnumake.parse import DefaultParsePipelineFactory
from abc import ABCMeta, abstractmethod
from argparse import ArgumentParser
from subprocess import Popen, PIPE, CalledProcessError
from typing import List
from io import TextIOBase
import os
import sys


class GnuMake:

    class ArgumentParserFactory:

        _PARSER = None

        @staticmethod
        def create_parser() -> ArgumentParser:
            if GnuMake.ArgumentParserFactory._PARSER is None:
                GnuMake.ArgumentParserFactory._PARSER = GnuMake.ArgumentParserFactory._create_parser()
            return GnuMake.ArgumentParserFactory._PARSER

        @staticmethod
        def _create_parser() -> ArgumentParser:
            parser = ThrowingArgumentParser(prog='', add_help=False, allow_abbrev=False)
            parser.add_argument('-C', '--directory', action='append', dest='directory', metavar='dir')
            return parser

    _INSTANCE = None

    @staticmethod
    def make() -> 'GnuMake':
        if GnuMake._INSTANCE is None:
            GnuMake._INSTANCE = GnuMake()
            GnuMake._INSTANCE._executable_name = 'make'
            GnuMake._init_nested_makefile_locator(GnuMake._INSTANCE)
            GnuMake._init_base_makefile_locator(GnuMake._INSTANCE)
            GnuMake._INSTANCE._storage_engine = None
        return GnuMake._INSTANCE

    @staticmethod
    def get_instance() -> 'GnuMake':
        return GnuMake.make()

    @staticmethod
    def _init_nested_makefile_locator(instance: 'GnuMake') -> None:
        locator = NestedMakefileLocator.make()
        locator.set_filename_priorities(['GNUmakefile', 'makefile', 'Makefile'])
        instance._nested_makefile_locator = locator

    @staticmethod
    def _init_base_makefile_locator(instance: 'GnuMake') -> None:
        locator = BaseMakefileLocator.make()
        locator.set_filename_priorities(['GNUmakefile', 'makefile', 'Makefile'])
        instance._base_makefile_locator = locator

    @staticmethod
    def _init_storage_engine(instance: 'GnuMake') -> None:
        instance._storage_engine = FileStorageEngine.make(DefaultDirectoryMapping.make())

    @property
    def storage_engine(self) -> StorageEngine:
        if self._storage_engine is None:
            GnuMake._init_storage_engine(self)
        return self._storage_engine

    @storage_engine.setter
    def storage_engine(self, value: StorageEngine) -> None:
        self._storage_engine = value

    @property
    def executable_name(self) -> str:
        return self._executable_name

    @executable_name.setter
    def executable_name(self, value: str) -> None:
        self._executable_name = value

    def base_makefile(self, directory_path: str) -> Makefile:
        with self._base_makefile_locator.makefile_iterator(directory_path) as makefiles:
            result = None
            for makefile in makefiles:
                result = makefile
                break
            return result

    def nested_makefiles(self, directory_path: str) -> IteratorContext[Makefile]:
        return self._nested_makefile_locator.makefile_iterator(directory_path)

    def execution_directory(self, args: List[str]) -> str:
        parser = GnuMake.ArgumentParserFactory.create_parser()
        directory_options = parser.parse_known_args(args)[0].directory
        if directory_options is None:
            return os.path.realpath(os.getcwd())
        else:
            return os.path.realpath(os.path.join(os.getcwd(), *directory_options))

    def create_nested_update_file(self) -> FileLifetimeManager:
        return self.storage_engine.create_nested_update_file()

    def update_nested_update_file(self, file: TextIOBase, execution_directory: str) -> None:
        target_formatter = DefaultTargetFormatter.make()
        nested_rule_file_prerequisites = []
        with self.nested_makefiles(execution_directory) as nested_makefiles:
            for nested_makefile in nested_makefiles:
                makefile_exec_path = os.path.relpath(nested_makefile.exec_path, start=execution_directory)
                makefile_file_path = nested_makefile.file_path
                makefile_path = os.path.join(makefile_exec_path, makefile_file_path)
                prerequisites = [makefile_path]
                recipe_lines = [' '.join(['autorecurse targetlisting', makefile_exec_path, makefile_file_path])]
                target = Target.make(prerequisites, [], recipe_lines)
                target.path = self.target_listing_file_path(nested_makefile)
                target_formatter.print(target, file)
                file.write('\n')
                nested_rule_file_prerequisites.append(target.path)
        recipe_lines = [' '.join(['autorecurse nestedrules', os.path.relpath(execution_directory, start=execution_directory)])]
        target = Target.make(nested_rule_file_prerequisites, [], recipe_lines)
        target.path = self.nested_rule_file_path(execution_directory)
        target_formatter.print(target, file)
        file.write('\n')

    def target_listing_file_path(self, makefile: Makefile) -> str:
        return self.storage_engine.target_listing_file_path(makefile)

    def update_target_listing_file(self, makefile: Makefile) -> None:
        target = self._get_target_listing_target(makefile)
        self.storage_engine.create_target_listing_file(makefile)
        with open(self.target_listing_file_path(makefile), mode='w') as file:
            target_formatter = DefaultTargetFormatter.make()
            file.write('.PHONY: ')
            file.write(target.path)
            file.write('\n')
            target_formatter.print(target, file)
            file.write('\n')

    def _get_target_listing_target(self, makefile: Makefile) -> Target:
        target_reader = TargetListingTargetReader.make(self.executable_name)
        makefile_targets = []
        with target_reader.target_iterator(makefile) as targets:
            for target in targets:
                makefile_targets.append(target.path)
        target = Target.make(makefile_targets, [], [])
        target.path = 'autorecurse-all-targets'
        return target

    def target_to_literal_target(self, target: Target, execution_directory: str) -> Target:
        """
        ## Specification Domain

        - target.file is not None
        """
        exec_path = target.file.exec_path
        prerequisites = []
        for prerequisite in target.prerequisites:
            abs_path = os.path.join(exec_path, prerequisite)
            rel_path = os.path.relpath(abs_path, start=execution_directory)
            prerequisites.append(rel_path)
        order_only_prerequisites = []
        for order_only_prerequisite in target.order_only_prerequisites:
            abs_path = os.path.join(exec_path, order_only_prerequisite)
            rel_path = os.path.relpath(abs_path, start=execution_directory)
            order_only_prerequisites.append(rel_path)
        recipe_args = []
        recipe_args.append('@$(MAKE) --no-print-directory -C')
        abs_path = exec_path
        rel_path = os.path.relpath(abs_path, start=execution_directory)
        recipe_args.append(rel_path)
        recipe_args.append('-f')
        recipe_args.append(target.file.file_path)
        recipe_args.append(target.path)
        recipe_lines = [' '.join(recipe_args)]
        abs_path = os.path.join(exec_path, target.path)
        rel_path = os.path.relpath(abs_path, start=execution_directory)
        literal_target = Target.make(prerequisites, order_only_prerequisites, recipe_lines)
        literal_target.path = rel_path
        return literal_target

    def nested_rule_file_path(self, execution_directory: str) -> str:
        return self.storage_engine.nested_rule_file_path(execution_directory)

    def update_nested_rule_file(self, execution_directory: str) -> None:
        target_reader = NestedRuleTargetReader.make(self.executable_name, self.storage_engine)
        target_formatter = DefaultTargetFormatter.make()
        self.storage_engine.create_nested_rule_file(execution_directory)
        with open(self.nested_rule_file_path(execution_directory), mode='w') as file:
            with self.nested_makefiles(execution_directory) as nested_makefiles:
                for nested_makefile in nested_makefiles:
                    with target_reader.target_iterator(nested_makefile) as nested_targets:
                        for nested_target in nested_targets:
                            if nested_target.path != 'autorecurse-all-targets':
                                literal_target = self.target_to_literal_target(nested_target, execution_directory)
                                target_formatter.print(literal_target, file)
                                file.write('\n')

    def run_make(self, args: List[str], nested_update_file_path: str) -> None:
        execution_directory = self.execution_directory(args)
        prefix_args = []
        prefix_args.append(self.executable_name)
        suffix_args = []
        base_makefile = self.base_makefile(execution_directory)
        if base_makefile is not None:
            suffix_args.append('-f')
            suffix_args.append(base_makefile.file_path)
        suffix_args.append('-f')
        suffix_args.append(self.nested_rule_file_path(execution_directory))
        suffix_args.append('-f')
        suffix_args.append(nested_update_file_path)
        prefix_args.extend(args)
        prefix_args.extend(suffix_args)
        proc = Popen(prefix_args)
        try:
            proc.wait()
        except KeyboardInterrupt:
            proc.terminate()
            proc.wait()
        sys.exit(proc.returncode)


class TargetReader(metaclass=ABCMeta):

    class Context(IteratorContext[Target], metaclass=ABCMeta):

        @staticmethod
        def _setup(instance: 'TargetReader.Context', parent: 'TargetReader', makefile: Makefile) -> None:
            instance._parent = parent
            instance._makefile = makefile
            instance._process = None

        def __enter__(self) -> Iterator[Target]:
            self._process = self._spawn_subprocess()
            return DefaultParsePipelineFactory.make().build_parse_pipeline(self._process.stdout, self._makefile)

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


