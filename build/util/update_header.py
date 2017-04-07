#!/usr/bin/python3
import autorecurse_path
from autorecurse.lib.line import FileLineIterator, Line
from io import TextIOBase
from typing import Dict, List
from argparse import ArgumentParser
import hashlib
import shutil
import os


class FileInfo:

    def __init__(self) -> None:
        super().__init__()
        self._insert_before = None # type: int
        self._skip_count = None # type: int

    @staticmethod
    def make(insert_before: int, skip_count: int) -> 'FileInfo':
        instance = FileInfo()
        instance._insert_before = insert_before
        instance._skip_count = skip_count
        return instance

    @property
    def insert_before(self) -> int:
        return self._insert_before

    @property
    def skip_count(self) -> int:
        return self._skip_count


class Cli:

    class ArgumentParserFactory:

        _INSTANCE = None

        @staticmethod
        def make() -> ArgumentParser:
            if Cli.ArgumentParserFactory._INSTANCE is None:
                Cli.ArgumentParserFactory._INSTANCE = Cli.ArgumentParserFactory._make()
            return Cli.ArgumentParserFactory._INSTANCE

        @staticmethod
        def _make() -> ArgumentParser:
            parser = ArgumentParser(**Cli.ArgumentParserFactory._constructor_args())
            Cli.ArgumentParserFactory._setup_parser(parser)
            return parser

        @staticmethod
        def _constructor_args() -> Dict[str, object]:
            args = {} # type: Dict[str, object]
            args['prog'] = 'update_header'
            args['description'] = 'Insert or update the same header content in multiple files.'
            return args

        @staticmethod
        def _setup_parser(parser: 'ArgumentParser') -> None:
            parser.add_argument('header_file', metavar='<header-file>', help='File containing header content.')
            parser.add_argument('target_files', metavar='<target-file>', nargs='+', help='Files to insert or update header in.')
            parser.add_argument('--comment-prefix', dest='comment_prefix', metavar='<comment-prefix>', default='#', help='Comment prefix string used for inserting headers in software source code files (default: "#").')

    _INSTANCE = None

    @staticmethod
    def make() -> 'Cli':
        if Cli._INSTANCE is None:
            Cli._INSTANCE = Cli()
        return Cli._INSTANCE

    def execute(self, args: List[str]) -> None:
        parser = Cli.ArgumentParserFactory.make()
        while True:
            if 0 < len(args):
                namespace = parser.parse_args(args)
                file_manager = FileManager.make()
                for target_path in namespace.target_files:
                    sub = Substitution.make(target_path, namespace.header_file, namespace.comment_prefix, file_manager)
                    sub.execute()
                break
            parser.parse_args(['-h'])
            break


class FileManager:

    _INSTANCE = None

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def make() -> 'FileManager':
        if FileManager._INSTANCE is None:
            FileManager._INSTANCE = FileManager()
        return FileManager._INSTANCE

    @property
    def _directory(self) -> str:
        return os.path.realpath(sys.path[0])

    @property
    def temporary_directory(self) -> str:
        return os.path.join(os.path.dirname(self._directory), 'tmp')

    def temporary_file_path(self, path: str) -> str:
        filename = ''.join(['prepend-header', self._make_hash(path), '.txt'])
        return os.path.join(self.temporary_directory, filename)

    def _make_hash(self, message: str) -> str:
        hash = hashlib.sha1()
        hash.update(message.encode())
        return hash.hexdigest()

    def _make_directory(self, path: str) -> None:
        if not os.path.isdir(path):
            os.makedirs(path)

    def create_temporary_file(self, path: str) -> None:
        self._make_directory(os.path.dirname(self.temporary_file_path(path)))
        shutil.copyfile(path, self.temporary_file_path(path))

    def delete_temporary_file(self, path: str) -> None:
        os.remove(self.temporary_file_path(path))


class Substitution:

    EOL_LF = '\n'

    def __init__(self) -> None:
        super().__init__()
        self._target_path = None # type: str
        self._replacement_path = None # type: str
        self._first_line_to_replace = None # type: str
        self._last_line_to_replace = None # type: str
        self._comment_prefix = None # type: str
        self._file_manager = None # type: FileManager
        self._eol = None # type: str

    @staticmethod
    def make(target_path: str, replacement_path: str, comment_prefix: str, file_manager: FileManager) -> 'Substitution':
        instance = Substitution()
        instance._target_path = target_path
        instance._replacement_path = replacement_path
        instance._comment_prefix = comment_prefix
        instance._file_manager = file_manager
        instance._eol = Substitution.EOL_LF
        instance._init_first_and_last_replacement_lines()
        return instance

    def _init_first_and_last_replacement_lines(self) -> None:
        with open(self._replacement_path, encoding='utf-8') as file:
            first_line = None # type: Line
            last_line = None # type: Line
            for line in FileLineIterator.make(file):
                if first_line is None:
                    first_line = line
                else:
                    last_line = line
            self._first_line_to_replace = first_line.content
            self._last_line_to_replace = last_line.content


    def execute(self) -> None:
        self._file_manager.create_temporary_file(self._target_path)
        with open(self._file_manager.temporary_file_path(self._target_path), encoding='utf-8') as tmp_file:
            file_info = self._collect_file_info(tmp_file)
            tmp_file.seek(0)
            with open(self._target_path, mode='w', encoding='utf-8') as target_file:
                with open(self._replacement_path, encoding='utf-8') as replacement_file:
                    self._perform_substitution(tmp_file, target_file, replacement_file, file_info)
        self._file_manager.delete_temporary_file(self._target_path)

    def _perform_substitution(self, tmp_file: TextIOBase, target_file: TextIOBase, replacement_file: TextIOBase, file_info: FileInfo) -> None:
        for line in FileLineIterator.make(tmp_file):
            if line.line_number == file_info.insert_before:
                for replacement_line in FileLineIterator.make(replacement_file):
                    target_file.write(self._comment_line(replacement_line.content))
                    target_file.write(self._eol)
            if (line.line_number < file_info.insert_before) or (file_info.insert_before + file_info.skip_count <= line.line_number):
                target_file.write(line.content)
                target_file.write(self._eol)

    def _collect_file_info(self, file: TextIOBase) -> FileInfo:
        first_line_index = None # type: int
        last_line_index = None # type: int
        first_line_content = self._comment_line(self._first_line_to_replace)
        last_line_content = self._comment_line(self._last_line_to_replace)
        for line in FileLineIterator.make(file):
            if first_line_index is None:
                if line.content == first_line_content:
                    first_line_index = line.line_number
            else:
                if line.content == last_line_content:
                    last_line_index = line.line_number
                    break
        insert_before = 1
        skip_count = 0
        if last_line_index is not None:
            insert_before = first_line_index
            skip_count = last_line_index - first_line_index + 1
        return FileInfo.make(insert_before, skip_count)

    def _comment_line(self, line: str) -> str:
        parts = [self._comment_prefix]
        if 0 < len(line):
            parts.append(' ')
            parts.append(line)
        return ''.join(parts)


if __name__ == '__main__':
    import sys
    cli = Cli.make()
    cli.execute(sys.argv[1:])


