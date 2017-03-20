from autorecurse.lib.iterator import IteratorContext
from autorecurse.lib.file import FileLifetimeManager
from autorecurse.gnumake.implementation import ArgumentParserFactory, Makefile, NestedMakefileLocator
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
        mapping[DirectoryEnum.TMP] = os.path.realpath(os.path.expanduser('~/.autorecurse/tmp'))
        directory_mapping = DictionaryDirectoryMapping.make(mapping)
        instance._storage_engine = FileStorageEngine.make(directory_mapping)

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


