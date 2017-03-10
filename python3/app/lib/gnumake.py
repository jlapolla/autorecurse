from lib.generics import *
from app.lib.makefile import *
from app.antlr.grammar import *
from app.antlr.adapter import *
from antlr4 import *
from io import StringIO


class GnuMake:

    @staticmethod
    def make_target_iterator_for_file(fp: io.TextIOBase) -> Iterator[MakefileTarget]:
        file_lines = FileLineIterator.make(fp)
        file_section = ConditionalSkipIterator.make(file_lines, FileSectionFilter.make())
        file_section_no_comments = ConditionalSkipIterator.make(file_section, InformationalCommentFilter.make())
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
        return makefile_target_iterator

    @staticmethod
    def make_target_iterator_for_file_streaming(fp: io.TextIOBase) -> Iterator[MakefileTarget]:
        file_lines = FileLineIterator.make(fp)
        file_section = ConditionalSkipIterator.make(file_lines, FileSectionFilter.make())
        file_section_no_comments = ConditionalSkipIterator.make(file_section, InformationalCommentFilter.make())
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
        return makefile_target_iterator


