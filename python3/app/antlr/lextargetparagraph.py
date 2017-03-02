# Generated from antlr4/TargetParagraphLexer.g4 by ANTLR 4.5.1
from antlr4 import *
from io import StringIO


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u0430\ud6d1\u8206\uad2d\u4417\uaef1\u8d80\uaadd\2\6")
        buf.write("`\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7")
        buf.write("\4\b\t\b\4\t\t\t\3\2\3\2\7\2\26\n\2\f\2\16\2\31\13\2\3")
        buf.write("\2\3\2\3\3\3\3\7\3\37\n\3\f\3\16\3\"\13\3\3\3\3\3\3\4")
        buf.write("\6\4\'\n\4\r\4\16\4(\3\5\3\5\3\5\3\5\3\6\3\6\3\6\3\6\3")
        buf.write("\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6")
        buf.write("\5\6A\n\6\3\7\3\7\3\7\3\7\3\7\3\7\3\7\3\7\3\7\3\7\7\7")
        buf.write("M\n\7\f\7\16\7P\13\7\3\7\3\7\5\7T\n\7\3\b\6\bW\n\b\r\b")
        buf.write("\16\bX\3\b\3\b\5\b]\n\b\3\t\3\t\2\2\n\3\3\5\4\7\5\t\6")
        buf.write("\13\2\r\2\17\2\21\2\3\2\3\3\2\f\fc\2\3\3\2\2\2\2\5\3\2")
        buf.write("\2\2\2\7\3\2\2\2\2\t\3\2\2\2\3\23\3\2\2\2\5\34\3\2\2\2")
        buf.write("\7&\3\2\2\2\t*\3\2\2\2\13.\3\2\2\2\rB\3\2\2\2\17V\3\2")
        buf.write("\2\2\21^\3\2\2\2\23\27\5\13\6\2\24\26\5\17\b\2\25\24\3")
        buf.write("\2\2\2\26\31\3\2\2\2\27\25\3\2\2\2\27\30\3\2\2\2\30\32")
        buf.write("\3\2\2\2\31\27\3\2\2\2\32\33\b\2\2\2\33\4\3\2\2\2\34 ")
        buf.write("\5\r\7\2\35\37\5\17\b\2\36\35\3\2\2\2\37\"\3\2\2\2 \36")
        buf.write("\3\2\2\2 !\3\2\2\2!#\3\2\2\2\" \3\2\2\2#$\b\3\2\2$\6\3")
        buf.write("\2\2\2%\'\5\17\b\2&%\3\2\2\2\'(\3\2\2\2(&\3\2\2\2()\3")
        buf.write("\2\2\2)\b\3\2\2\2*+\5\21\t\2+,\3\2\2\2,-\b\5\2\2-\n\3")
        buf.write("\2\2\2./\7%\2\2/\60\7\"\2\2\60\61\7P\2\2\61\62\7q\2\2")
        buf.write("\62\63\7v\2\2\63\64\7\"\2\2\64\65\7c\2\2\65\66\7\"\2\2")
        buf.write("\66\67\7v\2\2\678\7c\2\289\7t\2\29:\7i\2\2:;\7g\2\2;<")
        buf.write("\7v\2\2<=\7<\2\2=@\3\2\2\2>A\5\21\t\2?A\7\2\2\3@>\3\2")
        buf.write("\2\2@?\3\2\2\2A\f\3\2\2\2BC\7\60\2\2CD\7R\2\2DE\7J\2\2")
        buf.write("EF\7Q\2\2FG\7P\2\2GH\7[\2\2HI\7<\2\2IJ\7\"\2\2JN\3\2\2")
        buf.write("\2KM\n\2\2\2LK\3\2\2\2MP\3\2\2\2NL\3\2\2\2NO\3\2\2\2O")
        buf.write("S\3\2\2\2PN\3\2\2\2QT\5\21\t\2RT\7\2\2\3SQ\3\2\2\2SR\3")
        buf.write("\2\2\2T\16\3\2\2\2UW\n\2\2\2VU\3\2\2\2WX\3\2\2\2XV\3\2")
        buf.write("\2\2XY\3\2\2\2Y\\\3\2\2\2Z]\5\21\t\2[]\7\2\2\3\\Z\3\2")
        buf.write("\2\2\\[\3\2\2\2]\20\3\2\2\2^_\7\f\2\2_\22\3\2\2\2\13\2")
        buf.write("\27 (@NSX\\\3\b\2\2")
        return buf.getvalue()


class TargetParagraphLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]


    NOT_A_TARGET_PARAGRAPH = 1
    PHONY_PARAGRAPH = 2
    TARGET_PARAGRAPH = 3
    BLANK_LINE = 4

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
 ]

    symbolicNames = [ "<INVALID>",
            "NOT_A_TARGET_PARAGRAPH", "PHONY_PARAGRAPH", "TARGET_PARAGRAPH", 
            "BLANK_LINE" ]

    ruleNames = [ "NOT_A_TARGET_PARAGRAPH", "PHONY_PARAGRAPH", "TARGET_PARAGRAPH", 
                  "BLANK_LINE", "NOT_A_TARGET_LINE", "PHONY_LINE", "LINE", 
                  "EOL" ]

    grammarFileName = "TargetParagraphLexer.g4"

    def __init__(self, input=None):
        super().__init__(input)
        self.checkVersion("4.5.1")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


