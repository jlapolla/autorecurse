from antlr4 import BailErrorStrategy, DiagnosticErrorListener, InputStream, Lexer, Parser, RecognitionException, Token
from antlr4.BufferedTokenStream import TokenStream
from antlr4.CommonTokenFactory import CommonTokenFactory
from antlr4.Token import CommonToken
from typing import cast
import autorecurse.lib.antlr4.abstract as abstract


class CustomTokenFactory(CommonTokenFactory):

    _INSTANCE = None

    @staticmethod
    def make() -> 'CustomTokenFactory':
        if CustomTokenFactory._INSTANCE is None:
            CustomTokenFactory._INSTANCE = CustomTokenFactory()
        return CustomTokenFactory._INSTANCE

    def __init__(self):
        super().__init__(True)

    def create(self, source, type: int, text: str, channel: int, start: int, stop: int, line: int, column: int) -> CommonToken:
        token = super().create(source, type, text, channel, start, stop, line, column)
        if (token.type == Token.EOF) and (token._text == ''):
            token.text = '<EOF>'
        return token


class CustomLexer(Lexer, abstract.TokenSource):

    def __init__(self, input: abstract.CharStream) -> None:
        super().__init__(cast(InputStream, input))
        self.addErrorListener(DiagnosticErrorListener())
        self._factory = CustomTokenFactory.make()

    def recover(self, ex: RecognitionException) -> None:
        raise ex


class CustomParser(Parser):

    def __init__(self, input: abstract.TokenStream) -> None:
        super().__init__(cast(TokenStream, input))
        self.addErrorListener(DiagnosticErrorListener())
        self._errHandler = BailErrorStrategy()


