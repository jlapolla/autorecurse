from autorecurse.app.make.gnu.grammar import TargetParagraphLexer
from antlr4 import InputStream, Token
import unittest


class TestTargetParagraphLexer(unittest.TestCase):

    def test_basic_operation(self):
        not_a_target = """# Not a target:
.l.r:
#  Builtin rule
#  Implicit rule search has not been done.
#  Modification time never checked.
#  File has not been updated.
#  recipe to execute (built-in):
	$(LEX.l) $< > $@ 
	 mv -f lex.yy.r $@"""
        phony = """.PHONY: all
#  Implicit rule search has not been done.
#  Modification time never checked.
#  File has not been updated."""
        target1 = """objdir/bar.o: bar.c | objdir
#  Implicit rule search has been done.
#  Implicit/static pattern stem: 'bar'
#  Last modified 2017-02-20 14:12:50.825407391
#  File has been updated.
#  Successfully updated.
#  recipe to execute (from 'Makefile', line 5):
	touch $@"""
        target2 = """all: objdir/foo.o objdir/bar.o objdir/baz.o
#  Phony target (prerequisite of .PHONY).
#  Implicit rule search has not been done.
#  File does not exist.
#  File has been updated.
#  Successfully updated."""
        string = '\n\n'.join([not_a_target, phony, target1, not_a_target, target2])
        input_ = InputStream(string)
        lexer = TargetParagraphLexer(input_)
        token = lexer.nextToken()
        self.assertEqual(token.text, ''.join([target1, '\n']))
        self.assertEqual(token.type, TargetParagraphLexer.TARGET_PARAGRAPH)
        token = lexer.nextToken()
        self.assertEqual(token.text, target2)
        self.assertEqual(token.type, TargetParagraphLexer.TARGET_PARAGRAPH)
        token = lexer.nextToken()
        self.assertEqual(token.text, '<EOF>')
        self.assertEqual(token.type, Token.EOF)



