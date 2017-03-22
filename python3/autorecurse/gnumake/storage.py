from abc import ABCMeta, abstractmethod
from autorecurse.lib.file import FileLifetimeManager, UniqueFileCreator
from autorecurse.common.storage import DirectoryMapping
from autorecurse.gnumake.implementation import Makefile
import hashlib
import os


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

    def target_listing_file_path(self, makefile: Makefile) -> str:
        """
        ## Notes

        - For application-wide consistency, the passed Makefile must use
          canonical absolute paths (as returned by os.path.realpath).
        """
        hash = hashlib.sha1()
        hash.update(makefile.path.encode())
        filename = ''.join(['target-listing.', hash.hexdigest(), '.makefile'])
        directory = self._directory_mapping.get_directory(DirectoryEnum.TARGET_LISTING)
        return os.path.join(directory, filename)

    def create_target_listing_file(self, makefile: Makefile) -> None:
        path = self.target_listing_file_path(makefile)
        if not os.path.isfile(path):
            self._directory_mapping.make_directory(DirectoryEnum.TARGET_LISTING)
            with open(path, mode='a') as file:
                pass


class DirectoryEnum:

    TARGET_LISTING = 'target listing'
    TMP = 'tmp'


