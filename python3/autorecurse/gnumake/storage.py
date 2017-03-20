from abc import ABCMeta, abstractmethod
from autorecurse.lib.file import FileLifetimeManager, UniqueFileCreator
from autorecurse.common.storage import DirectoryMapping


class StorageEngine(metaclass=ABCMeta):

    @abstractmethod
    def create_nested_update_file(self) -> FileLifetimeManager:
        pass

class FileStorageEngine(StorageEngine):

    def make(directory_mapping: DirectoryMapping) -> StorageEngine:
        instance = FileStorageEngine()
        instance._directory_mapping = directory_mapping
        return instance

    def create_nested_update_file(self) -> FileLifetimeManager:
        file_creator = UniqueFileCreator.make()
        file_creator.file_name_prefix = 'nested-update.'
        file_creator.file_name_suffix = '.makefile'
        file_creator.directory = self._directory_mapping.get_directory(DirectoryEnum.TMP)
        self._directory_mapping.make_directory(DirectoryEnum.TMP)
        return FileLifetimeManager.make(file_creator)


class DirectoryEnum:

    TMP = 'tmp'


