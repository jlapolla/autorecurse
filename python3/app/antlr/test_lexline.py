from lib.generics import StringBuffer
from app.antlr.lexline import *
from app.antlr.adapter import IteratorToCharStreamAdapter
from antlr4 import Token
import unittest


class TestLineLexer(unittest.TestCase):

    def test_basic_operation(self):
        string = """
Hello
Goodbye

Goodbye again"""
        char_iterator = StringBuffer.make(string)
        input_ = IteratorToCharStreamAdapter.make(char_iterator)
        lexer = LineLexer(input_)
        token = lexer.nextToken()
        self.assertEqual(token.text, '\n')
        self.assertEqual(token.type, LineLexer.BLANK)
        token = lexer.nextToken()
        self.assertEqual(token.text, 'Hello\n')
        self.assertEqual(token.type, LineLexer.LINE)
        token = lexer.nextToken()
        self.assertEqual(token.text, 'Goodbye\n')
        self.assertEqual(token.type, LineLexer.LINE)
        token = lexer.nextToken()
        self.assertEqual(token.text, '\n')
        self.assertEqual(token.type, LineLexer.BLANK)
        token = lexer.nextToken()
        self.assertEqual(token.text, 'Goodbye again')
        self.assertEqual(token.type, LineLexer.LINE)
        token = lexer.nextToken()
        self.assertEqual(token.text, '<EOF>')
        self.assertEqual(token.type, Token.EOF)


