from abc import ABCMeta, abstractmethod
from autorecurse.lib.iterator import Iterator, IteratorContext
from autorecurse.lib.file import FileLifetimeManager, UniqueFileCreator
from autorecurse.common.storage import DirectoryMapping
from autorecurse.gnumake.implementation import Factory, Makefile, Target
from subprocess import Popen, PIPE, CalledProcessError
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


class DirectoryEnum:

    NESTED_RULE = 'nested rule'
    TARGET_LISTING = 'target listing'
    TMP = 'tmp'


class TargetReader(metaclass=ABCMeta):

    class Context(IteratorContext[Target], metaclass=ABCMeta):

        @staticmethod
        def _setup(instance: 'TargetReader.Context', parent: 'TargetReader', makefile: Makefile) -> None:
            instance._parent = parent
            instance._makefile = makefile
            instance._process = None

        def __enter__(self) -> Iterator[Target]:
            self._process = self._spawn_subprocess()
            return Factory.make_target_iterator_for_file(self._process.stdout, self._makefile)

        def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
            if self._process is not None:
                self._process.stdout.close()
                self._process.wait()
                if self._process.returncode != 0:
                    raise CalledProcessError(self._process.returncode, ' '.join(self._process.args))
            return False

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


