from autorecurse.gnumake.implementation import GnuMake
from autorecurse.gnumake.data import Makefile
from autorecurse.common.storage import DefaultDirectoryMapping
from autorecurse.config import DirectoryMappingAutoLoader, DirectoryMappingBuilder
from argparse import ArgumentParser, Namespace
from typing import Dict, List
import os
import sys


class Cli:

    class ArgumentParserFactory:

        _PARSER = None

        @staticmethod
        def create_parser() -> ArgumentParser:
            if Cli.ArgumentParserFactory._PARSER is None:
                Cli.ArgumentParserFactory._PARSER = Cli.ArgumentParserFactory._create_parser()
            return Cli.ArgumentParserFactory._PARSER

        @staticmethod
        def _create_parser() -> ArgumentParser:
            parser = ArgumentParser(**Cli.ArgumentParserFactory._init_args())
            Cli.ArgumentParserFactory._setup_parser(parser)
            subparsers = parser.add_subparsers(dest='command', title='commands', metavar='(gnumake | targetlisting | nestedrules)')
            Cli.ArgumentParserFactory._init_gnumake(subparsers)
            Cli.ArgumentParserFactory._init_targetlisting(subparsers)
            Cli.ArgumentParserFactory._init_nestedrules(subparsers)
            return parser

        @staticmethod
        def _init_args() -> Dict:
            args = {}
            args['prog'] = 'autorecurse'
            args['description'] = 'Recursively call `make` on makefiles in subdirectories.'
            args['allow_abbrev'] = False
            return args

        @staticmethod
        def _setup_parser(parser: 'ArgumentParser') -> None:
            parser.add_argument('--make-executable', dest='make_executable', metavar='<make-path>', help='Path to `make` executable.')
            parser.add_argument('--config-file', dest='config_file_path', metavar='<config-file>', help='Path to `autorecurse` configuration file.')

        @staticmethod
        def _init_gnumake(subparsers) -> None:
            args = {}
            args['help'] = 'Run GNU Make.'
            args['description'] = 'Run GNU Make.'
            args['allow_abbrev'] = False
            parser = subparsers.add_parser('gnumake', **args)

        @staticmethod
        def _init_targetlisting(subparsers) -> None:
            args = {}
            args['help'] = 'Generate target listing file for <makefile>.'
            args['description'] = 'Generate target listing file for <makefile>.'
            args['allow_abbrev'] = False
            parser = subparsers.add_parser('targetlisting', **args)
            parser.add_argument('dir', metavar='<dir>', help='Directory from which <makefile> is executed.')
            parser.add_argument('makefile', metavar='<makefile>', help='Relative path from <dir> to <makefile>.')

        @staticmethod
        def _init_nestedrules(subparsers) -> None:
            args = {}
            args['help'] = 'Generate nested rule file for <dir>.'
            args['description'] = 'Generate nested rule file for <dir>.'
            args['allow_abbrev'] = False
            parser = subparsers.add_parser('nestedrules', **args)
            parser.add_argument('dir', metavar='<dir>', help='Directory to generate nested rules for.')

    @staticmethod
    def make() -> 'Cli':
        return Cli()

    def execute(self, args: List[str]) -> None:
        parser = Cli.ArgumentParserFactory.create_parser()
        while True:
            if 0 < len(args):
                namespace, other_args = parser.parse_known_args(args)
                self._configure_application(namespace)
                if namespace.command == 'gnumake':
                    namespace, make_args = parser.parse_known_args(args)
                    gnu = GnuMake.make()
                    if namespace.make_executable is not None:
                        gnu.executable_name = namespace.make_executable
                    execution_directory = gnu.execution_directory(make_args)
                    with gnu.create_nested_update_file() as file_manager:
                        with file_manager.open_file('w') as file:
                            gnu.update_nested_update_file(file, execution_directory)
                        gnu.run_make(make_args, file_manager.file_path)
                    break
                if namespace.command == 'targetlisting':
                    namespace = parser.parse_args(args)
                    directory = os.path.realpath(os.path.join(os.getcwd(), namespace.dir))
                    file = namespace.makefile
                    makefile = Makefile.make_with_exec_path(directory, file)
                    gnu = GnuMake.make()
                    if namespace.make_executable is not None:
                        gnu.executable_name = namespace.make_executable
                    gnu.update_target_listing_file(makefile)
                    break
                if namespace.command == 'nestedrules':
                    namespace = parser.parse_args(args)
                    directory = os.path.realpath(os.path.join(os.getcwd(), namespace.dir))
                    gnu = GnuMake.make()
                    if namespace.make_executable is not None:
                        gnu.executable_name = namespace.make_executable
                    gnu.update_nested_rule_file(directory)
                    break
                parser.parse_args(args)
                break
            parser.parse_args(['-h'])
            break


    def _configure_application(self, namespace: Namespace) -> None:
        auto_loader = DirectoryMappingAutoLoader.make()
        builder = DirectoryMappingBuilder.make()
        path = auto_loader.auto_config_file_path()
        if path is not None:
            builder.include_config_file(path)
        path = namespace.config_file_path
        if path is not None:
            builder.include_config_file(path)
        DefaultDirectoryMapping.set(builder.build_directory_mapping())


