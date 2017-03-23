from autorecurse.gnumake.implementation import Makefile
from autorecurse.gnumake.api import GnuMake
from argparse import ArgumentParser
from typing import Dict, List
import sys
import os


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
            subparsers = parser.add_subparsers(dest='subcommand', title='commands', metavar='(gnumake | targetlisting | nestedrules)')
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
            pass

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
                if args[0] == 'gnumake':
                    namespace, make_args = parser.parse_known_args(args)
                    gnu = GnuMake.make()
                    execution_directory = gnu.execution_directory(make_args)
                    with gnu.create_nested_update_file() as file_manager:
                        with file_manager.open_file('w') as file:
                            gnu.update_nested_update_file(file, execution_directory)
                        gnu.run_make(make_args, file_manager.file_path)
                    break
                if args[0] == 'targetlisting':
                    namespace = parser.parse_args(args)
                    directory = os.path.realpath(os.path.join(os.getcwd(), namespace.dir))
                    file = namespace.makefile
                    makefile = Makefile.make_with_exec_path(directory, file)
                    gnu = GnuMake.make()
                    gnu.update_target_listing_file(makefile)
                    break
                if args[0] == 'nestedrules':
                    namespace = parser.parse_args(args)
                    directory = os.path.realpath(os.path.join(os.getcwd(), namespace.dir))
                    gnu = GnuMake.make()
                    gnu.update_nested_rule_file(directory)
                    break
                parser.parse_args(args)
                break
            parser.parse_args(['-h'])
            break
        pass


