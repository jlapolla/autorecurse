from abc import ABCMeta, abstractmethod
from typing import Dict
import os


class DirectoryMapping(metaclass=ABCMeta):

    @abstractmethod
    def get_directory(self, symbolic_name: str) -> str:
        pass

    def make_directory(self, symbolic_name: str) -> None:
        if not os.path.isdir(self.get_directory(symbolic_name)):
            os.makedirs(self.get_directory(symbolic_name))


class DictionaryDirectoryMapping(DirectoryMapping):

    def __init__(self) -> None:
        super().__init__()
        self._directory_dict = None # type: Dict[str, str]

    @staticmethod
    def make(mapping: Dict[str, str]) -> DirectoryMapping:
        instance = DictionaryDirectoryMapping()
        DictionaryDirectoryMapping._setup(instance, mapping)
        return instance

    @staticmethod
    def _setup(instance: 'DictionaryDirectoryMapping', mapping: Dict[str, str]) -> None:
        instance._directory_dict = {};
        for key in mapping:
            instance._directory_dict[key] = mapping[key]

    def get_directory(self, symbolic_name: str) -> str:
        return self._directory_dict[symbolic_name]


class DefaultDirectoryMapping:

    _INSTANCE = None

    @staticmethod
    def make() -> DirectoryMapping:
        if DefaultDirectoryMapping._INSTANCE is not None:
            return DefaultDirectoryMapping._INSTANCE
        else:
            raise Exception('Default directory mapping not initialized.')

    @staticmethod
    def set(mapping: DirectoryMapping) -> None:
        DefaultDirectoryMapping._INSTANCE = mapping


