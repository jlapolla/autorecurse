from autorecurse.lib.iterator import Iterator, ListIterator
from abc import ABCMeta, abstractmethod
from io import TextIOBase
from typing import List
import os


class Makefile:

    def __init__(self) -> None:
        super().__init__()
        self._exec_path = None # type: str
        self._file_path = None # type: str

    @staticmethod
    def make(path: str) -> 'Makefile':
        instance = Makefile()
        Makefile._setup(instance, path)
        return instance

    @staticmethod
    def _setup(instance: 'Makefile', path: str) -> None:
        instance._exec_path = os.path.dirname(path)
        instance._file_path = os.path.basename(path)

    @staticmethod
    def make_with_exec_path(exec_path: str, file_path: str) -> 'Makefile':
        instance = Makefile()
        Makefile._setup_with_exec_path(instance, exec_path, file_path)
        return instance

    @staticmethod
    def _setup_with_exec_path(instance: 'Makefile', exec_path: str, file_path: str) -> None:
        instance._exec_path = exec_path
        instance._file_path = file_path

    @property
    def path(self) -> str:
        """
        Path to the Makefile.
        """
        if not os.path.isabs(self.file_path): # file_path is relative
            if len(self.exec_path) == 0: # exec_path is empty
                return self.file_path
            elif not os.path.isabs(self.exec_path): # exec_path is relative
                return os.path.join(self.exec_path, self.file_path)
            else: # exec_path is absolute
                return os.path.join(self.exec_path, self.file_path)
        else: # file_path is absolute
            # exec_path is empty
            # exec_path is relative
            # exec_path is absolute
            return self.file_path

    @property
    def exec_path(self) -> str:
        """
        Path that make should be run from (-C option).

        ## Notes

        - Empty exec_path will not generate a -C option.
        """
        return self._exec_path

    @exec_path.setter
    def exec_path(self, value: str) -> None:
        self._exec_path = value

    @property
    def file_path(self) -> str:
        """
        Path to file that make should be run on (-f option).
        """
        return self._file_path

    @file_path.setter
    def file_path(self, value: str) -> None:
        self._file_path = value


class Target:

    def __init__(self) -> None:
        super().__init__()
        self._file = None # type: Makefile
        self._path = None # type: str
        self._prerequisites = None # type: List[str]
        self._order_only_prerequisites = None # type: List[str]
        self._recipe_lines = None # type: List[str]

    @staticmethod
    def make(prerequisites: List[str], order_only_prerequisites: List[str], recipe_lines: List[str]) -> 'Target':
        instance = Target()
        instance._file = None
        instance._path = None
        instance._prerequisites = list(prerequisites)
        instance._order_only_prerequisites = list(order_only_prerequisites)
        instance._recipe_lines = list(recipe_lines)
        return instance

    @property
    def file(self) -> Makefile:
        return self._file

    @file.setter
    def file(self, value: Makefile) -> None:
        self._file = value

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, value: str) -> None:
        self._path = value

    @property
    def prerequisites(self) -> Iterator[str]:
        return ListIterator.make(self._prerequisites)

    @property
    def order_only_prerequisites(self) -> Iterator[str]:
        return ListIterator.make(self._order_only_prerequisites)

    @property
    def recipe_lines(self) -> Iterator[str]:
        return ListIterator.make(self._recipe_lines)


class TargetFormatter(metaclass=ABCMeta):

    @abstractmethod
    def print(self, target: Target, file: TextIOBase) -> None:
        pass


class DefaultTargetFormatter(TargetFormatter):

    _INSTANCE = None

    @staticmethod
    def make() -> TargetFormatter:
        if DefaultTargetFormatter._INSTANCE is None:
            DefaultTargetFormatter._INSTANCE = DefaultTargetFormatter()
        return DefaultTargetFormatter._INSTANCE

    def print(self, target: Target, file: TextIOBase) -> None:
        file.write(target.path)
        file.write(':')
        for prerequisite in target.prerequisites:
            file.write(' ')
            file.write(prerequisite)
        first_oo_prerequisite = True
        for oo_prerequisite in target.order_only_prerequisites:
            if first_oo_prerequisite:
                file.write(' |')
                first_oo_prerequisite = False
            file.write(' ')
            file.write(oo_prerequisite)
        has_recipe_lines = False
        for recipe_line in target.recipe_lines:
            file.write('\n\t')
            file.write(recipe_line)
            if not has_recipe_lines:
                has_recipe_lines = True
        if not has_recipe_lines:
            file.write(' ;')
        file.write('\n')


