from abc import ABCMeta, abstractmethod
from io import IOBase
from typing import Dict
import os
import tempfile


class FileCreator(metaclass=ABCMeta):
    """
    Creates a file, and makes its path accessible.

    ## Transition System Definition

    ### States

    - S = Start <- INITIAL STATE
    - C = Created

    ### Transition Labels

    - Create = Client calls create_file

    ### Transitions Grouped by Label

    - Create
      - S -> C

    ## Call State Validity

    For each method listed, client is allowed to call the method in the
    given states.

    - create_file: S
    - file_path (getter): C
    """

    @abstractmethod
    def create_file(self) -> None:
        """
        Creates an empty file. When this function returns, the file is
        closed.
        """
        pass

    @property
    @abstractmethod
    def file_path(self) -> str:
        """
        The normalized absolute path to the created file.
        """
        pass


class UniqueFileCreator(FileCreator):

    @staticmethod
    def make() -> 'UniqueFileCreator':
        instance = UniqueFileCreator()
        instance._file_path = None
        instance._file_name_suffix = None
        instance._file_name_prefix = None
        instance._directory = None
        return instance

    def create_file(self) -> None:
        with tempfile.NamedTemporaryFile(**self._args) as file:
            self._file_path = file.name

    @property
    def file_path(self) -> str:
        return self._file_path

    @property
    def file_name_suffix(self) -> str:
        return self._file_name_suffix

    @file_name_suffix.setter
    def file_name_suffix(self, value: str) -> None:
        self._file_name_suffix = value

    @property
    def file_name_prefix(self) -> str:
        return self._file_name_prefix

    @file_name_prefix.setter
    def file_name_prefix(self, value: str) -> None:
        self._file_name_prefix = value

    @property
    def directory(self) -> str:
        return self._directory

    @directory.setter
    def directory(self, value: str) -> None:
        self._directory = value

    @property
    def _args(self) -> Dict:
        result = {'mode': 'x', 'delete': False}
        if self.file_name_suffix is not None:
            result['suffix'] = self.file_name_suffix
        if self.file_name_prefix is not None:
            result['prefix'] = self.file_name_prefix
        if self.directory is not None:
            result['dir'] = self.directory
        return result


class FileLifetimeManager:

    @staticmethod
    def make(file_creator: FileCreator) -> 'FileLifetimeManager':
        instance = FileLifetimeManager()
        instance._file_creator = file_creator
        return instance

    def open_file(self, *args, **kwargs) -> IOBase:
        return open(self._file_creator.file_path, *args, **kwargs)

    @property
    def file_path(self) -> str:
        return self._file_creator.file_path

    def __enter__(self) -> 'FileLifetimeManager':
        self._file_creator.create_file()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        os.remove(self._file_creator.file_path)
        return False


