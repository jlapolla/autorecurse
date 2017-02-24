from app.antlr.lexline import *
from antlr4 import InputStream, Token
import unittest


class TestLineLexer(unittest.TestCase):

    def test_basic_operation(self):
        string = """
Hello
Goodbye

Goodbye again"""
        input_ = InputStream(string)
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


