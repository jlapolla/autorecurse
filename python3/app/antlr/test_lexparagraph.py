from lib.generics import StringBuffer
from app.antlr.lexparagraph import *
from app.antlr.adapter import IteratorToCharStreamAdapter
from antlr4 import Token
import unittest


class TestParagraphLexer(unittest.TestCase):

    def test_basic_operation(self):
        string = """
Hello
Goodbye


Goodbye again"""
        char_iterator = StringBuffer.make(string)
        input_ = IteratorToCharStreamAdapter.make(char_iterator)
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


