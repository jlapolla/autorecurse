from lib.generics import StringBuffer
from app.antlr.grammar import *
from antlr4 import *
import unittest


class TestParagraphLexer(unittest.TestCase):

    def test_basic_operation(self):
        string = """
Hello
Goodbye


Goodbye again"""
        input_ = InputStream(string)
        lexer = ParagraphLexer(input_)
        token = lexer.nextToken()
        self.assertEqual(token.text, 'Hello\nGoodbye\n')
        self.assertEqual(token.type, ParagraphLexer.PARAGRAPH)
        token = lexer.nextToken()
        self.assertEqual(token.text, 'Goodbye again')
        self.assertEqual(token.type, ParagraphLexer.PARAGRAPH)
        token = lexer.nextToken()
        self.assertEqual(token.text, '<EOF>')
        self.assertEqual(token.type, Token.EOF)


