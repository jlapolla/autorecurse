from abc import ABCMeta, abstractmethod
from argparse import ArgumentParser, ArgumentError
from io import StringIO, TextIOBase
from typing import List
import os
import sys
from antlr4 import CommonTokenStream, InputStream
from antlr4.error.Errors import ParseCancellationException
from autorecurse.lib.iterator import Iterator, IteratorConcatenator, IteratorContext, ListIterator
from autorecurse.lib.line import FileLineIterator, LineToCharIterator
from autorecurse.lib.stream import ConditionFilter
from autorecurse.gnumake.grammar import DatabaseSectionFilter, FileSectionFilter, InformationalCommentFilter, MakefileRuleLexer, MakefileRuleParser, TargetParagraphLexer
from autorecurse.lib.antlr4.stream import TokenSourceToIteratorAdapter, TokenToCharIterator


class Makefile:

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


class ParseContextTargetBuilder:

    _INSTANCE = None

    @staticmethod
    def get_instance() -> 'ParseContextTargetBuilder':
        if ParseContextTargetBuilder._INSTANCE is None:
            ParseContextTargetBuilder._INSTANCE = ParseContextTargetBuilder.make()
        return ParseContextTargetBuilder._INSTANCE

    @staticmethod
    def make() -> 'ParseContextTargetBuilder':
        return ParseContextTargetBuilder()

    def build_target(self, context: MakefileRuleParser.MakefileRuleContext, target_index: int) -> None:
        prerequisites = []
        for item in context.prerequisite():
            prerequisites.append(item.IDENTIFIER().symbol.text)
        order_only_prerequisites = []
        for item in context.orderOnlyPrerequisite():
            order_only_prerequisites.append(item.IDENTIFIER().symbol.text)
        recipe_lines = []
        for item in context.recipe().RECIPE_LINE():
            line = self._trim_recipe_line(item.symbol.text)
            recipe_lines.append(line)
        target = Target.make(prerequisites, order_only_prerequisites, recipe_lines)
        target.path = context.target(target_index).IDENTIFIER().symbol.text
        return target

    def _trim_recipe_line(self, recipe_line: str) -> str:
        remove_count = 0
        if (recipe_line.rfind('\t') + 1 + remove_count == len(recipe_line)):
            remove_count = remove_count + 1
        if (recipe_line.rfind('\n') + 1 + remove_count == len(recipe_line)):
            remove_count = remove_count + 1
        end_index = len(recipe_line) - remove_count
        return recipe_line[0:end_index]


class Factory:

    @staticmethod
    def make_target_iterator_for_file(fp: TextIOBase, makefile: Makefile) -> Iterator[Target]:
        file_lines = FileLineIterator.make(fp)
        database_section = ConditionFilter.make(file_lines, DatabaseSectionFilter.make())
        file_section = ConditionFilter.make(database_section, FileSectionFilter.make())
        file_section_no_comments = ConditionFilter.make(file_section, InformationalCommentFilter.make())
        file_section_chars = LineToCharIterator.make(file_section_no_comments)
        char_stream_1 = None
        with StringIO() as strbuff:
            if file_section_chars.is_at_start:
                file_section_chars.move_to_next()
            while file_section_chars.has_current_item:
                strbuff.write(file_section_chars.current_item)
                file_section_chars.move_to_next()
            char_stream_1 = InputStream(strbuff.getvalue())
        paragraph_lexer = TargetParagraphLexer(char_stream_1)
        paragraph_tokens = TokenSourceToIteratorAdapter.make(paragraph_lexer)
        paragraph_chars = TokenToCharIterator.make(paragraph_tokens)
        char_stream_2 = None
        with StringIO() as strbuff:
            if paragraph_chars.is_at_start:
                paragraph_chars.move_to_next()
            while paragraph_chars.has_current_item:
                strbuff.write(paragraph_chars.current_item)
                paragraph_chars.move_to_next()
            char_stream_2 = InputStream(strbuff.getvalue())
        makefile_rule_lexer = MakefileRuleLexer(char_stream_2)
        token_stream_1 = CommonTokenStream(makefile_rule_lexer)
        makefile_rule_parser = MakefileRuleParser(token_stream_1)
        makefile_target_iterator = MakefileRuleParserToIteratorAdapter.make(makefile_rule_parser)
        makefile_target_iterator.makefile = makefile
        return makefile_target_iterator

    @staticmethod
    def make_target_iterator_for_file_streaming(fp: TextIOBase, makefile: Makefile) -> Iterator[Target]:
        file_lines = FileLineIterator.make(fp)
        database_section = ConditionFilter.make(file_lines, DatabaseSectionFilter.make())
        file_section = ConditionFilter.make(database_section, FileSectionFilter.make())
        file_section_no_comments = ConditionFilter.make(file_section, InformationalCommentFilter.make())
        file_section_chars = LineToCharIterator.make(file_section_no_comments)
        char_stream_1 = IteratorToCharStreamAdapter.make(file_section_chars)
        paragraph_lexer = TargetParagraphLexer(char_stream_1)
        paragraph_tokens = TokenSourceToIteratorAdapter.make(paragraph_lexer)
        paragraph_chars = TokenToCharIterator.make(paragraph_tokens)
        char_stream_2 = IteratorToCharStreamAdapter.make(paragraph_chars)
        makefile_rule_lexer = MakefileRuleLexer(char_stream_2)
        makefile_rule_tokens = TokenSourceToIteratorAdapter.make(makefile_rule_lexer)
        token_stream_1 = IteratorToTokenStreamAdapter.make(makefile_rule_tokens)
        makefile_rule_parser = MakefileRuleParser(token_stream_1)
        makefile_target_iterator = MakefileRuleParserToIteratorAdapter.make(makefile_rule_parser)
        makefile_target_iterator.makefile = makefile
        return makefile_target_iterator


class MakefileRuleParserToIteratorAdapter(Iterator[Target]):

    @staticmethod
    def make(parser: MakefileRuleParser) -> Iterator[Target]:
        instance = MakefileRuleParserToIteratorAdapter()
        MakefileRuleParserToIteratorAdapter._setup(instance, parser)
        return instance

    @staticmethod
    def _setup(instance: 'MakefileRuleParserToIteratorAdapter', parser: MakefileRuleParser) -> None:
        instance._parser = parser
        instance._makefile = None
        instance._to_S()

    @property
    def current_item(self) -> Target:
        return self._target

    @property
    def has_current_item(self) -> bool:
        return self._target is not None

    @property
    def is_at_start(self) -> bool:
        return not (self.has_current_item or self.is_at_end)

    @property
    def is_at_end(self) -> bool:
        return self._is_at_end

    def move_to_next(self) -> None:
        if self.is_at_start: # State S
            # S -> I
            # S -> E
            self._get_next_target()
        else: # State I
            if self._index + 1 != self._current_length:
                # I -> I
                self._index = self._index + 1
                self._generate_target()
            else:
                # I -> I
                # I -> E
                self._index = 0
                self._get_next_target()

    @property
    def _current_length(self) -> int:
        if self.is_at_start: # State S
            return 0
        elif self.has_current_item: # State I
            return len(self._context.target())
        else: # State E
            return 0

    def _get_next_target(self) -> None:
        # State S or I
        self._get_next_non_empty_context()
        if not self.is_at_end:
            # S -> I
            # I -> I
            self._generate_target()
            self._to_I()
        else:
            # S -> E
            # I -> E
            # Already at state E
            pass

    def _generate_target(self) -> None:
        self._target = ParseContextTargetBuilder.get_instance().build_target(self._context, self._index)
        self._target.file = self.makefile

    def _get_next_non_empty_context(self) -> None:
        # State S or I
        self._get_next_context()
        while not ((self._context is not None) or self.is_at_end):
            self._get_next_context()

    def _get_next_context(self) -> None:
        # State S or I
        ctx = None
        try:
            ctx = self._parser.declaration()
        except ParseCancellationException:
            self._to_E()
        else:
            self._context = ctx.makefileRule()

    def _to_S(self) -> None:
        self._index = 0
        self._target = None
        self._context = None
        self._is_at_end = False

    def _to_I(self) -> None:
        self._is_at_end = False

    def _to_E(self) -> None:
        self._index = 0
        self._target = None
        self._context = None
        self._is_at_end = True

    @property
    def makefile(self) -> Makefile:
        return self._makefile

    @makefile.setter
    def makefile(self, value: Makefile) -> None:
        self._makefile = value


class DirectoryMakefileLocator(metaclass=ABCMeta):

    @abstractmethod
    def makefile_iterator(self, directory_path: str) -> IteratorContext[Makefile]:
        pass


class NestedMakefileLocator(DirectoryMakefileLocator):

    class Context(IteratorContext[Makefile]):

        @staticmethod
        def make(parent: 'NestedMakefileLocator', directory_path: str) -> IteratorContext[Makefile]:
            instance = NestedMakefileLocator.Context()
            instance._parent = parent
            instance._directory_path = directory_path
            return instance

        def __enter__(self) -> Iterator[Makefile]:
            list_ = []
            for dirpath, dirnames, filenames in os.walk(self._directory_path):
                name = self._parent._get_best_name(filenames)
                if name is not None:
                    abs_path = os.path.realpath(os.path.join(os.getcwd(), dirpath))
                    list_.append(Makefile.make_with_exec_path(abs_path, name))
                else:
                    dirnames.clear()
            return ListIterator.make(list_)

        def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
            return False

    def make() -> 'NestedMakefileLocator':
        instance = NestedMakefileLocator()
        instance._priorities = {}
        return instance

    def makefile_iterator(self, directory_path: str) -> IteratorContext[Makefile]:
        return NestedMakefileLocator.Context.make(self, directory_path)

    def set_filename_priorities(self, filenames: List[str]) -> None:
        self._priorities = {}
        index = len(filenames)
        for name in filenames:
            self._priorities[name] = index
            index = index - 1

    def _get_best_name(self, filenames: List[str]) -> str:
        best_name = None
        best_priority = 0
        for name in filenames:
            if name in self._priorities:
                priority = self._priorities[name]
                if best_priority < priority:
                    best_name = name
                    best_priority = priority
        return best_name


class ThrowingArgumentParser(ArgumentParser):

    def error(self, message: str) -> None:
        raise ArgumentError(None, message)


class ArgumentParserFactory:

    _PARSER = None

    @staticmethod
    def create_parser() -> ArgumentParser:
        if ArgumentParserFactory._PARSER is None:
            ArgumentParserFactory._PARSER = ArgumentParserFactory._create_parser()
        return ArgumentParserFactory._PARSER

    @staticmethod
    def _create_parser() -> ArgumentParser:
        parser = ThrowingArgumentParser(prog='', add_help=False, allow_abbrev=False)
        parser.add_argument('-C', '--directory', action='append', dest='directory', metavar='dir')
        return parser


