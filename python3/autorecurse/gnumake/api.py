from autorecurse.lib.iterator import IteratorContext
from autorecurse.lib.file import FileLifetimeManager
from autorecurse.gnumake.implementation import ArgumentParserFactory, DefaultTargetFormatter, Makefile, NestedMakefileLocator, TargetListingTargetReader, Target
from autorecurse.gnumake.storage import DirectoryEnum, FileStorageEngine
from autorecurse.common.storage import DictionaryDirectoryMapping
from typing import List
import os


class GnuMake:

    _INSTANCE = None

    @staticmethod
    def get_instance() -> 'GnuMake':
        if GnuMake._INSTANCE is None:
            GnuMake._INSTANCE = GnuMake._make()
        return GnuMake._INSTANCE

    @staticmethod
    def _make() -> 'GnuMake':
        instance = GnuMake()
        GnuMake._init_nested_makefile_locator(instance)
        GnuMake._init_storage_engine(instance)
        return instance

    @staticmethod
    def _init_nested_makefile_locator(instance: 'GnuMake') -> None:
        locator = NestedMakefileLocator.make()
        locator.set_filename_priorities(['GNUmakefile', 'makefile', 'Makefile'])
        instance._makefile_locator = locator

    @staticmethod
    def _init_storage_engine(instance: 'GnuMake') -> None:
        mapping = {}
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


