from lib.generics import *
from app.lib.makefile import *
from app.antlr.grammar import *
from app.antlr.adapter import *


class GnuMake:

    @staticmethod
    def make_target_iterator_for_file(fp: io.TextIOBase) -> Iterator[MakefileTarget]:
        file_lines = FileLineIterator.make(fp)
        file_section = ConditionalSkipIterator.make(file_lines, FileSectionFilter.make())
        file_section_chars = LineToCharIterator.make(file_section)
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


