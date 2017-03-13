from autorecurse.lib.generics import *
from autorecurse.app.lib.makefile import *
from autorecurse.app.antlr.grammar import *
from autorecurse.app.antlr.adapter import *
from antlr4 import *
from io import StringIO
import sys
import subprocess


class GnuMake:

    @staticmethod
    def make_target_iterator_for_file(fp: io.TextIOBase, makefile: Makefile) -> Iterator[MakefileTarget]:
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
        makefile_target_iterator.makefile = makefile
        return makefile_target_iterator

    @staticmethod
    def make_target_iterator_for_file_streaming(fp: io.TextIOBase, makefile: Makefile) -> Iterator[MakefileTarget]:
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
        makefile_target_iterator.makefile = makefile
        return makefile_target_iterator


class GnuMakeTargetReader(MakefileTargetReader):

    class Context(IteratorContext[MakefileTarget]):

        @staticmethod
        def make(parent: 'GnuMakeTargetReader', makefile: Makefile) -> IteratorContext[MakefileTarget]:
            instance = GnuMakeTargetReader.Context()
            GnuMakeTargetReader.Context._setup(instance, parent, makefile)
            return instance

        @staticmethod
        def _setup(instance: 'GnuMakeTargetReader.Context', parent: 'GnuMakeTargetReader', makefile: Makefile) -> None:
            instance._parent = parent
            instance._makefile = makefile
            instance._stringio = None

        def __enter__(self) -> Iterator[MakefileTarget]:
            """
            ## Suggestions

            - Use subprocess.Popen and feed stdout directly to the
              parsing pipeline. This will require a TextIOWrapper, and
              additional code in __exit__.
            """
            args = []
            args.append(self._parent.executable_name)
            args.append('-qp')
            if len(self._makefile.exec_path) != 0:
                args.append('-C')
                args.append(self._makefile.exec_path)
            args.append('-f')
            args.append(self._makefile.file_path)
            result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if not ((result.returncode == 0) or (result.returncode == 1)):
                # Return code == 1 is okay, since the -q option returns
                # 1 when the default target is out of date.
                sys.stderr.write(result.stderr.decode())
                raise subprocess.CalledProcessError(result.returncode, ' '.join(result.args), result.stdout, result.stderr)
            self._stringio = StringIO(result.stdout.decode())
            return GnuMake.make_target_iterator_for_file(self._stringio, self._makefile)

        def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
            self._stringio.close()
            return False

    @staticmethod
    def make(executable_name: str) -> MakefileTargetReader:
        instance = GnuMakeTargetReader()
        GnuMakeTargetReader._setup(instance, executable_name)
        return instance

    @staticmethod
    def _setup(instance: 'GnuMakeTargetReader', executable_name: str) -> None:
        instance._executable_name = executable_name

    @property
    def executable_name(self) -> str:
        return self._executable_name

    def target_iterator(self, makefile: Makefile) -> IteratorContext[MakefileTarget]:
        return GnuMakeTargetReader.Context.make(self, makefile)


