from autorecurse.common.storage import DictionaryDirectoryMapping, DirectoryMapping
from autorecurse.gnumake.storage import DirectoryEnum as GnuMakeDirectoryEnum
from pkg_resources import resource_stream
from abc import ABCMeta, abstractmethod
from configparser import ConfigParser
from io import TextIOBase, TextIOWrapper
from typing import Dict
import os
import sys


class ConfigFileLocator:

    _INSTANCE = None

    @staticmethod
    def make() -> 'ConfigFileLocator':
        if ConfigFileLocator._INSTANCE is None:
            ConfigFileLocator._INSTANCE = ConfigFileLocator()
        return ConfigFileLocator._INSTANCE

    def include_standard_config_files(self, builder: 'ConfigFileConverter') -> None:
        with self._resource_name_to_file(self._default_config_resource_name()) as default_file:
            builder.include_config_file(default_file)
        resource_name = self._platform_resource_config_name()
        if resource_name is not None:
            with self._resource_name_to_file(resource_name) as platform_file:
                builder.include_config_file(platform_file)

    def _default_config_resource_name(self) -> str:
        return 'config/default.txt'

    def _platform_resource_config_name(self) -> str:
        if sys.platform.startswith('linux'):
            return 'config/linux.txt'
        if sys.platform.startswith('cygwin'):
            return 'config/cygwin.txt'
        if sys.platform.startswith('win'):
            # https://msdn.microsoft.com/en-us/library/windows/desktop/dd378457.aspx
            if 'LOCALAPPDATA' in os.environ:
                return 'config/windows.txt'
            elif 'USERPROFILE' in os.environ:
                return 'config/windows-legacy.txt'
        if sys.platform.startswith('darwin'):
            return 'config/osx.txt'
        return None

    def _resource_name_to_file(self, resource_name: str) -> TextIOBase:
        return TextIOWrapper(resource_stream('autorecurse', resource_name), encoding='utf-8')


class ConfigFileConverter(metaclass=ABCMeta):

    @abstractmethod
    def include_config_file_path(self, config_file_path: str) -> None:
        pass

    @abstractmethod
    def include_config_file(self, config_file: TextIOBase) -> None:
        pass


class DirectoryMappingBuilder(ConfigFileConverter):

    def __init__(self) -> None:
        super().__init__()
        self._dict = None # type: Dict[str, str]

    @staticmethod
    def make() -> 'DirectoryMappingBuilder':
        instance = DirectoryMappingBuilder()
        instance._dict = {}
        return instance

    def include_config_file_path(self, path: str) -> None:
        with open(path, mode='r', encoding='utf-8') as config_file:
            config = ConfigParser(dict_type=dict, empty_lines_in_values=False, interpolation=None) # type: ignore
            config.read_file(config_file, source=path)
            self._process_config(config)

    def include_config_file(self, config_file: TextIOBase) -> None:
        config = ConfigParser(dict_type=dict, empty_lines_in_values=False, interpolation=None) # type: ignore
        config.read_file(config_file)
        self._process_config(config)

    def _process_config(self, config: ConfigParser) -> None:
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


