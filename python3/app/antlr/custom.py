from antlr4.error.Errors import RecognitionException
from antlr4.error.ErrorStrategy import BailErrorStrategy
from antlr4.error.DiagnosticErrorListener import DiagnosticErrorListener
from antlr4.CommonTokenFactory import CommonTokenFactory
from antlr4.Lexer import Lexer
from antlr4.Parser import Parser
from antlr4.Token import CommonToken, Token
from app.antlr.abstract import CharStream, TokenStream
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
        self.addErrorListener(DiagnosticErrorListener())
        self._factory = CustomTokenFactory.DEFAULT_INSTANCE

    def recover(self, ex: RecognitionException) -> None:
        raise ex


class CustomParser(Parser):

    def __init__(self, input: TokenStream) -> None:
        super().__init__(input)
        self.addErrorListener(DiagnosticErrorListener())
        self._errHandler = BailErrorStrategy()


