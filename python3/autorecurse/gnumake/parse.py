from antlr4 import CommonTokenStream, InputStream
from antlr4.error.Errors import ParseCancellationException
from autorecurse.lib.iterator import Iterator
from autorecurse.lib.line import FileLineIterator, LineToCharIterator
from autorecurse.lib.stream import ConditionFilter
from autorecurse.gnumake.grammar import DatabaseSectionFilter, FileSectionFilter, InformationalCommentFilter, MakefileRuleLexer, MakefileRuleParser, TargetParagraphLexer
from autorecurse.gnumake.data import Makefile, Target
from autorecurse.lib.antlr4.stream import IteratorToCharStreamAdapter, IteratorToTokenStreamAdapter, TokenSourceToIteratorAdapter, TokenToCharIterator
from abc import ABCMeta, abstractmethod
from io import StringIO, TextIOBase
from typing import cast


class ParseContextTargetBuilder:

    _INSTANCE = None

    @staticmethod
    def make() -> 'ParseContextTargetBuilder':
        if ParseContextTargetBuilder._INSTANCE is None:
            ParseContextTargetBuilder._INSTANCE = ParseContextTargetBuilder()
        return ParseContextTargetBuilder._INSTANCE

    def build_target(self, context: MakefileRuleParser.MakefileRuleContext, target_index: int) -> Target:
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


class ParsePipelineFactory(metaclass=ABCMeta):

    @abstractmethod
    def build_parse_pipeline(self, file: TextIOBase, makefile: Makefile) -> Iterator[Target]:
        pass


class BufferedParsePipelineFactory(ParsePipelineFactory):

    _INSTANCE = None

    @staticmethod
    def make() -> ParsePipelineFactory:
        if BufferedParsePipelineFactory._INSTANCE is None:
            BufferedParsePipelineFactory._INSTANCE = BufferedParsePipelineFactory()
        return BufferedParsePipelineFactory._INSTANCE

    def build_parse_pipeline(self, file: TextIOBase, makefile: Makefile) -> Iterator[Target]:
        file_lines = FileLineIterator.make(file)
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
            char_stream_1 = InputStream(cast(StringIO, strbuff).getvalue())
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
            char_stream_2 = InputStream(cast(StringIO, strbuff).getvalue())
        makefile_rule_lexer = MakefileRuleLexer(char_stream_2)
        token_stream_1 = CommonTokenStream(makefile_rule_lexer)
        makefile_rule_parser = MakefileRuleParser(token_stream_1)
        makefile_target_iterator = MakefileRuleParserToIteratorAdapter.make(makefile_rule_parser)
        makefile_target_iterator.makefile = makefile
        return makefile_target_iterator


class StreamingParsePipelineFactory(ParsePipelineFactory):

    _INSTANCE = None

    @staticmethod
    def make() -> ParsePipelineFactory:
        if StreamingParsePipelineFactory._INSTANCE is None:
            StreamingParsePipelineFactory._INSTANCE = StreamingParsePipelineFactory()
        return StreamingParsePipelineFactory._INSTANCE

    def build_parse_pipeline(self, file: TextIOBase, makefile: Makefile) -> Iterator[Target]:
        file_lines = FileLineIterator.make(file)
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
        makefile_rule_parser = MakefileRuleParser(token_stream_1) # type: ignore
        makefile_target_iterator = MakefileRuleParserToIteratorAdapter.make(makefile_rule_parser)
        makefile_target_iterator.makefile = makefile
        return makefile_target_iterator


class BalancedParsePipelineFactory(ParsePipelineFactory):

    _INSTANCE = None

    @staticmethod
    def make() -> ParsePipelineFactory:
        if BalancedParsePipelineFactory._INSTANCE is None:
            BalancedParsePipelineFactory._INSTANCE = BalancedParsePipelineFactory()
        return BalancedParsePipelineFactory._INSTANCE

    def build_parse_pipeline(self, file: TextIOBase, makefile: Makefile) -> Iterator[Target]:
        file_lines = FileLineIterator.make(file)
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
            char_stream_1 = InputStream(cast(StringIO, strbuff).getvalue())
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
            char_stream_2 = InputStream(cast(StringIO, strbuff).getvalue())
        makefile_rule_lexer = MakefileRuleLexer(char_stream_2)
        makefile_rule_tokens = TokenSourceToIteratorAdapter.make(makefile_rule_lexer)
        token_stream_1 = IteratorToTokenStreamAdapter.make(makefile_rule_tokens)
        makefile_rule_parser = MakefileRuleParser(token_stream_1) # type: ignore
        makefile_target_iterator = MakefileRuleParserToIteratorAdapter.make(makefile_rule_parser)
        makefile_target_iterator.makefile = makefile
        return makefile_target_iterator


class DefaultParsePipelineFactory:

    _INSTANCE = None

    @staticmethod
    def make() -> ParsePipelineFactory:
        if DefaultParsePipelineFactory._INSTANCE is not None:
            return DefaultParsePipelineFactory._INSTANCE
        else:
            raise Exception('Default parse pipeline factory not initialized.')

    @staticmethod
    def set(value: ParsePipelineFactory) -> None:
        DefaultParsePipelineFactory._INSTANCE = value


DefaultParsePipelineFactory.set(BalancedParsePipelineFactory.make())



class MakefileRuleParserToIteratorAdapter(Iterator[Target]):

    def __init__(self) -> None:
        super().__init__()
        self._index = None # type: int
        self._target = None # type: Target
        self._context = None # type: MakefileRuleParser.MakefileRuleContext
        self._is_at_end = None # type: bool
        self._makefile = None # type: Makefile
        self._parser = None # type: MakefileRuleParser

    @staticmethod
    def make(parser: MakefileRuleParser) -> 'MakefileRuleParserToIteratorAdapter':
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
        self._target = ParseContextTargetBuilder.make().build_target(self._context, self._index)
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


