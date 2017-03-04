import app.antlr.custom
# Generated from antlr4/ParagraphLexer.g4 by ANTLR 4.5.1
from antlr4 import *
from io import StringIO


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u0430\ud6d1\u8206\uad2d\u4417\uaef1\u8d80\uaadd\2\4")
        buf.write("\"\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\3\2\6\2\r\n\2\r")
        buf.write("\2\16\2\16\3\3\6\3\22\n\3\r\3\16\3\23\3\3\3\3\3\4\6\4")
        buf.write("\31\n\4\r\4\16\4\32\3\4\3\4\5\4\37\n\4\3\5\3\5\2\2\6\3")
        buf.write("\3\5\4\7\2\t\2\3\2\3\3\2\f\f#\2\3\3\2\2\2\2\5\3\2\2\2")
        buf.write("\3\f\3\2\2\2\5\21\3\2\2\2\7\30\3\2\2\2\t \3\2\2\2\13\r")
        buf.write("\5\7\4\2\f\13\3\2\2\2\r\16\3\2\2\2\16\f\3\2\2\2\16\17")
        buf.write("\3\2\2\2\17\4\3\2\2\2\20\22\5\t\5\2\21\20\3\2\2\2\22\23")
        buf.write("\3\2\2\2\23\21\3\2\2\2\23\24\3\2\2\2\24\25\3\2\2\2\25")
        buf.write("\26\b\3\2\2\26\6\3\2\2\2\27\31\n\2\2\2\30\27\3\2\2\2\31")
        buf.write("\32\3\2\2\2\32\30\3\2\2\2\32\33\3\2\2\2\33\36\3\2\2\2")
        buf.write("\34\37\5\t\5\2\35\37\7\2\2\3\36\34\3\2\2\2\36\35\3\2\2")
        buf.write("\2\37\b\3\2\2\2 !\7\f\2\2!\n\3\2\2\2\7\2\16\23\32\36\3")
        buf.write("\b\2\2")
        return buf.getvalue()


class ParagraphLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]


    PARAGRAPH = 1
    BLANK = 2

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
 ]

    symbolicNames = [ "<INVALID>",
            "PARAGRAPH", "BLANK" ]

    ruleNames = [ "PARAGRAPH", "BLANK", "LINE", "EOL" ]

    grammarFileName = "ParagraphLexer.g4"

    def __init__(self, input=None):
        super().__init__(input)
        self.checkVersion("4.5.1")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


