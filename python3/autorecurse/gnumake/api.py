from autorecurse.lib.iterator import IteratorContext
from autorecurse.lib.file import FileLifetimeManager
from autorecurse.gnumake.implementation import ArgumentParserFactory, DefaultTargetFormatter, Makefile, NestedMakefileLocator, Target
from autorecurse.gnumake.storage import DirectoryEnum, FileStorageEngine, NestedRuleTargetReader, TargetListingTargetReader
from autorecurse.common.storage import DictionaryDirectoryMapping
from typing import List
from io import TextIOBase
import os
import sys
import subprocess


class GnuMake:

    _INSTANCE = None

    @staticmethod
    def make() -> 'GnuMake':
        if GnuMake._INSTANCE is None:
            GnuMake._INSTANCE = GnuMake()
            GnuMake._init_nested_makefile_locator(GnuMake._INSTANCE)
            GnuMake._init_storage_engine(GnuMake._INSTANCE)
        return GnuMake._INSTANCE

    @staticmethod
    def get_instance() -> 'GnuMake':
        return GnuMake.make()

    @staticmethod
    def _init_nested_makefile_locator(instance: 'GnuMake') -> None:
        locator = NestedMakefileLocator.make()
        locator.set_filename_priorities(['GNUmakefile', 'makefile', 'Makefile'])
        instance._makefile_locator = locator

    @staticmethod
    def _init_storage_engine(instance: 'GnuMake') -> None:
        mapping = {}
        mapping[DirectoryEnum.NESTED_RULE] = os.path.realpath(os.path.expanduser('~/.autorecurse/cache'))
        mapping[DirectoryEnum.TARGET_LISTING] = os.path.realpath(os.path.expanduser('~/.autorecurse/cache'))
        mapping[DirectoryEnum.TMP] = os.path.realpath(os.path.expanduser('~/.autorecurse/tmp'))
        directory_mapping = DictionaryDirectoryMapping.make(mapping)
        instance._storage_engine = FileStorageEngine.make(directory_mapping)

    @property
    def executable_name(self) -> str:
        return 'make'

    def nested_makefiles(self, directory_path: str) -> IteratorContext[Makefile]:
        return self._makefile_locator.makefile_iterator(directory_path)

    def execution_directory(self, args: List[str]) -> str:
        parser = ArgumentParserFactory.create_parser()
        directory_options = parser.parse_known_args(args)[0].directory
        if directory_options is None:
            return os.path.realpath(os.getcwd())
        else:
            return os.path.realpath(os.path.join(os.getcwd(), *directory_options))

    def create_nested_update_file(self) -> FileLifetimeManager:
        return self._storage_engine.create_nested_update_file()

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
        return self._storage_engine.target_listing_file_path(makefile)

    def update_target_listing_file(self, makefile: Makefile) -> None:
        target = self._get_target_listing_target(makefile)
        self._storage_engine.create_target_listing_file(makefile)
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
        return self._storage_engine.nested_rule_file_path(execution_directory)

    def update_nested_rule_file(self, execution_directory: str) -> None:
        target_reader = NestedRuleTargetReader.make(self.executable_name, self._storage_engine)
        target_formatter = DefaultTargetFormatter.make()
        self._storage_engine.create_nested_rule_file(execution_directory)
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
        prefix_args.append('-f')
        prefix_args.append(self.nested_rule_file_path(execution_directory))
        prefix_args.append('-f')
        prefix_args.append(nested_update_file_path)
        prefix_args.extend(args)
        result = subprocess.run(prefix_args)
        sys.exit(result.returncode)


