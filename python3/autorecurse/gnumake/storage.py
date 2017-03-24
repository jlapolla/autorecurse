from autorecurse.common.storage import DirectoryMapping
from autorecurse.lib.file import FileLifetimeManager, UniqueFileCreator
from autorecurse.gnumake.data import Makefile
from abc import ABCMeta, abstractmethod
import hashlib
import os


class StorageEngine(metaclass=ABCMeta):

    @abstractmethod
    def create_nested_update_file(self) -> FileLifetimeManager:
        pass

    @abstractmethod
    def target_listing_file_path(self, makefile: Makefile) -> str:
        pass

    @abstractmethod
    def create_target_listing_file(self, makefile: Makefile) -> None:
        pass

    @abstractmethod
    def nested_rule_file_path(self, execution_directory: str) -> str:
        pass

    @abstractmethod
    def create_nested_rule_file(self, execution_directory: str) -> None:
        pass

class FileStorageEngine(StorageEngine):

    @staticmethod
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

        - For application-wide consistency, makefile.exec_path must use
          canonical absolute paths (as returned by os.path.realpath).
        """
        filename = ''.join(['target-listing.', self._make_hash(makefile.path), '.makefile'])
        directory = self._directory_mapping.get_directory(DirectoryEnum.TARGET_LISTING)
        return os.path.join(directory, filename)

    def create_target_listing_file(self, makefile: Makefile) -> None:
        path = self.target_listing_file_path(makefile)
        if not os.path.isfile(path):
            self._directory_mapping.make_directory(DirectoryEnum.TARGET_LISTING)
            with open(path, mode='a') as file:
                pass

    def nested_rule_file_path(self, execution_directory: str) -> str:
        """
        ## Notes

        - For application-wide consistency, the passed execution
          directory must be a canonical absolute path (as returned by
          os.path.realpath).
        """
        filename = ''.join(['nested-rule.', self._make_hash(execution_directory), '.makefile'])
        directory = self._directory_mapping.get_directory(DirectoryEnum.NESTED_RULE)
        return os.path.join(directory, filename)

    def _make_hash(self, message: str) -> str:
        hash = hashlib.sha1()
        hash.update(message.encode())
        return hash.hexdigest()

    def create_nested_rule_file(self, execution_directory: str) -> None:
        path = self.nested_rule_file_path(execution_directory)
        if not os.path.isfile(path):
            self._directory_mapping.make_directory(DirectoryEnum.NESTED_RULE)
            with open(path, mode='a') as file:
                pass


class DirectoryEnum:

    NESTED_RULE = 'nested rule'
    TARGET_LISTING = 'target listing'
    TMP = 'tmp'


