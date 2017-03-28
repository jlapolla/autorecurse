from autorecurse.common.storage import DefaultDirectoryMapping, DictionaryDirectoryMapping, DirectoryMapping
from autorecurse.gnumake.storage import DirectoryEnum as GnuMakeDirectoryEnum
from configparser import ConfigParser
from abc import ABCMeta, abstractmethod
import os
import sys


class UnsupportedPlatformError(Exception):

    def __init__(self, message: str = None) -> None:
        if message is None:
            super().__init__('Platform not supported.')
        else:
            super().__init__(message)


class DirectoryMappingAutoLoader:

    _INSTANCE = None

    @staticmethod
    def make() -> 'DirectoryMappingAutoLoader':
        if DirectoryMappingAutoLoader._INSTANCE is None:
            DirectoryMappingAutoLoader._INSTANCE = DirectoryMappingAutoLoader()
        return DirectoryMappingAutoLoader._INSTANCE

    def auto_load(self) -> None:
        config_file_path = self.auto_config_file_path()
        if config_file_path is None:
            raise UnsupportedPlatformError('No configuration file for ' + sys.platform + ' platform.')
        self.load_from_path(config_file_path)

    def load_from_path(self, config_file_path: str) -> None:
        reader = DirectoryMappingReader.make()
        mapping = reader.parse_directory_mapping(config_file_path)
        DefaultDirectoryMapping.set(mapping)

    def default_config_file_path(self) -> str:
        return os.path.join(os.path.realpath(sys.path[0]), 'config', 'default.txt')

    def auto_config_file_path(self) -> str:
        if os.path.isfile(self.default_config_file_path()):
            return self.default_config_file_path()
        config_dir = os.path.join(os.path.realpath(sys.path[0]), 'config')
        if sys.platform.startswith('linux'):
            return os.path.join(config_dir, 'linux.txt')
        if sys.platform.startswith('cygwin'):
            return os.path.join(config_dir, 'cygwin.txt')
        if sys.platform.startswith('win'):
            return os.path.join(config_dir, 'windows.txt')
        if sys.platform.startswith('darwin'):
            return os.path.join(config_dir, 'osx.txt')
        return None


class DirectoryMappingReader:

    _INSTANCE = None

    @staticmethod
    def make() -> 'DirectoryMappingReader':
        if DirectoryMappingReader._INSTANCE is None:
            DirectoryMappingReader._INSTANCE = DirectoryMappingReader()
        return DirectoryMappingReader._INSTANCE

    def parse_directory_mapping(self, config_file_path: str) -> DirectoryMapping:
        builder = DirectoryMappingBuilder.make()
        builder.include_config_file(config_file_path)
        return builder.build_directory_mapping()


class ConfigFileConverter(metaclass=ABCMeta):

    @abstractmethod
    def include_config_file(self, config_file_path: str) -> None:
        pass


class DirectoryMappingBuilder(ConfigFileConverter):

    @staticmethod
    def make() -> 'DirectoryMappingBuilder':
        instance = DirectoryMappingBuilder()
        instance._dict = {}
        return instance

    def include_config_file(self, path: str) -> None:
        with open(path, 'r') as file:
            config = ConfigParser(dict_type=dict, empty_lines_in_values=False, interpolation=None)
            config.read_file(file, source=path)
            if 'gnumake' in config:
                gnumake_config = config['gnumake']
                if 'cache_dir' in gnumake_config:
                    self._dict[GnuMakeDirectoryEnum.NESTED_RULE] = self._expand_path(gnumake_config['cache_dir'])
                    self._dict[GnuMakeDirectoryEnum.TARGET_LISTING] = self._expand_path(gnumake_config['cache_dir'])
                if 'temp_dir' in gnumake_config:
                    self._dict[GnuMakeDirectoryEnum.TMP] = self._expand_path(gnumake_config['temp_dir'])

    def build_directory_mapping(self) -> DirectoryMapping:
        return DictionaryDirectoryMapping.make(self._dict)

    def _expand_path(self, path: str) -> str:
        result = os.path.expandvars(path)
        result = os.path.expanduser(path)
        return os.path.realpath(result)


