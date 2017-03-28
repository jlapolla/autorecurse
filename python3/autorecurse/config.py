from autorecurse.common.storage import DictionaryDirectoryMapping, DirectoryMapping
from autorecurse.gnumake.storage import DirectoryEnum as GnuMakeDirectoryEnum
from configparser import ConfigParser
from abc import ABCMeta, abstractmethod
import os
import sys


class ConfigFileLocator:

    _INSTANCE = None

    @staticmethod
    def make() -> 'ConfigFileLocator':
        if ConfigFileLocator._INSTANCE is None:
            ConfigFileLocator._INSTANCE = ConfigFileLocator()
        return ConfigFileLocator._INSTANCE

    def include_default_config_files(self, builder: 'ConfigFileConverter') -> None:
        builder.include_config_file(self.default_config_file_path())
        path = self.platform_config_file_path()
        if path is not None:
            builder.include_config_file(path)

    def default_config_file_path(self) -> str:
        return os.path.join(os.path.realpath(sys.path[0]), 'config', 'default.txt')

    def platform_config_file_path(self) -> str:
        config_dir = os.path.join(os.path.realpath(sys.path[0]), 'config')
        if sys.platform.startswith('linux'):
            return os.path.join(config_dir, 'linux.txt')
        if sys.platform.startswith('cygwin'):
            return os.path.join(config_dir, 'cygwin.txt')
        if sys.platform.startswith('win'):
            # https://msdn.microsoft.com/en-us/library/windows/desktop/dd378457.aspx
            if 'LOCALAPPDATA' in os.environ:
                return os.path.join(config_dir, 'windows.txt')
            elif 'USERPROFILE' in os.environ:
                return os.path.join(config_dir, 'windows-legacy.txt')
        if sys.platform.startswith('darwin'):
            return os.path.join(config_dir, 'osx.txt')
        return None


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
        result = os.path.normcase(path) # Needed to process 'default.txt' on Windows (since it uses forward slashes)
        result = os.path.expandvars(path)
        result = os.path.expanduser(path)
        return os.path.realpath(result)


