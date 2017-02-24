# Generated from antlr4/LineLexer.g4 by ANTLR 4.5.1
from antlr4 import *
from io import StringIO


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u0430\ud6d1\u8206\uad2d\u4417\uaef1\u8d80\uaadd\2\4")
        buf.write("\26\b\1\4\2\t\2\4\3\t\3\4\4\t\4\3\2\6\2\13\n\2\r\2\16")
        buf.write("\2\f\3\2\3\2\5\2\21\n\2\3\3\3\3\3\4\3\4\2\2\5\3\3\5\4")
        buf.write("\7\2\3\2\3\3\2\f\f\26\2\3\3\2\2\2\2\5\3\2\2\2\3\n\3\2")
        buf.write("\2\2\5\22\3\2\2\2\7\24\3\2\2\2\t\13\n\2\2\2\n\t\3\2\2")
        buf.write("\2\13\f\3\2\2\2\f\n\3\2\2\2\f\r\3\2\2\2\r\20\3\2\2\2\16")
        buf.write("\21\5\7\4\2\17\21\7\2\2\3\20\16\3\2\2\2\20\17\3\2\2\2")
        buf.write("\21\4\3\2\2\2\22\23\5\7\4\2\23\6\3\2\2\2\24\25\7\f\2\2")
        buf.write("\25\b\3\2\2\2\5\2\f\20\2")
        return buf.getvalue()


class LineLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]


    LINE = 1
    BLANK = 2

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
 ]

    symbolicNames = [ "<INVALID>",
            "LINE", "BLANK" ]

    ruleNames = [ "LINE", "BLANK", "EOL" ]

    grammarFileName = "LineLexer.g4"

    def __init__(self, input=None):
        super().__init__(input)
        self.checkVersion("4.5.1")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


