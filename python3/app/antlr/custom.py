from antlr4.CommonTokenFactory import CommonTokenFactory
from antlr4.Lexer import Lexer
from antlr4.Token import CommonToken, Token
from app.antlr.abstract import CharStream
from typing import Tuple


class CustomTokenFactory(CommonTokenFactory):

    DEFAULT_INSTANCE = None

    def __init__(self):
        super().__init__(True)

    def create(self, source, type: int, text: str, channel: int, start: int, stop: int, line: int, column: int) -> CommonToken:
        token = super().create(source, type, text, channel, start, stop, line, column)
        if (token.type == Token.EOF) and (token._text == ''):
            token.text = '<EOF>'
        return token

CustomTokenFactory.DEFAULT_INSTANCE = CustomTokenFactory()


class CustomLexer(Lexer):

    def __init__(self, input: CharStream) -> None:
        super().__init__(input)
        self._factory = CustomTokenFactory.DEFAULT_INSTANCE


