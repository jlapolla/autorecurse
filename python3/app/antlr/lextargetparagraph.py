# Generated from antlr4/TargetParagraphLexer.g4 by ANTLR 4.5.1
from antlr4 import *
from io import StringIO


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u0430\ud6d1\u8206\uad2d\u4417\uaef1\u8d80\uaadd\2\6")
        buf.write("c\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7")
        buf.write("\4\b\t\b\4\t\t\t\3\2\3\2\7\2\26\n\2\f\2\16\2\31\13\2\3")
        buf.write("\2\3\2\3\3\3\3\7\3\37\n\3\f\3\16\3\"\13\3\3\3\3\3\3\4")
        buf.write("\6\4\'\n\4\r\4\16\4(\3\5\6\5,\n\5\r\5\16\5-\3\5\3\5\3")
        buf.write("\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6")
        buf.write("\3\6\3\6\3\6\3\6\5\6D\n\6\3\7\3\7\3\7\3\7\3\7\3\7\3\7")
        buf.write("\3\7\3\7\3\7\7\7P\n\7\f\7\16\7S\13\7\3\7\3\7\5\7W\n\7")
        buf.write("\3\b\6\bZ\n\b\r\b\16\b[\3\b\3\b\5\b`\n\b\3\t\3\t\2\2\n")
        buf.write("\3\3\5\4\7\5\t\6\13\2\r\2\17\2\21\2\3\2\3\3\2\f\fg\2\3")
        buf.write("\3\2\2\2\2\5\3\2\2\2\2\7\3\2\2\2\2\t\3\2\2\2\3\23\3\2")
        buf.write("\2\2\5\34\3\2\2\2\7&\3\2\2\2\t+\3\2\2\2\13\61\3\2\2\2")
        buf.write("\rE\3\2\2\2\17Y\3\2\2\2\21a\3\2\2\2\23\27\5\13\6\2\24")
        buf.write("\26\5\17\b\2\25\24\3\2\2\2\26\31\3\2\2\2\27\25\3\2\2\2")
        buf.write("\27\30\3\2\2\2\30\32\3\2\2\2\31\27\3\2\2\2\32\33\b\2\2")
        buf.write("\2\33\4\3\2\2\2\34 \5\r\7\2\35\37\5\17\b\2\36\35\3\2\2")
        buf.write("\2\37\"\3\2\2\2 \36\3\2\2\2 !\3\2\2\2!#\3\2\2\2\" \3\2")
        buf.write("\2\2#$\b\3\2\2$\6\3\2\2\2%\'\5\17\b\2&%\3\2\2\2\'(\3\2")
        buf.write("\2\2(&\3\2\2\2()\3\2\2\2)\b\3\2\2\2*,\5\21\t\2+*\3\2\2")
        buf.write("\2,-\3\2\2\2-+\3\2\2\2-.\3\2\2\2./\3\2\2\2/\60\b\5\2\2")
        buf.write("\60\n\3\2\2\2\61\62\7%\2\2\62\63\7\"\2\2\63\64\7P\2\2")
        buf.write("\64\65\7q\2\2\65\66\7v\2\2\66\67\7\"\2\2\678\7c\2\289")
        buf.write("\7\"\2\29:\7v\2\2:;\7c\2\2;<\7t\2\2<=\7i\2\2=>\7g\2\2")
        buf.write(">?\7v\2\2?@\7<\2\2@C\3\2\2\2AD\5\21\t\2BD\7\2\2\3CA\3")
        buf.write("\2\2\2CB\3\2\2\2D\f\3\2\2\2EF\7\60\2\2FG\7R\2\2GH\7J\2")
        buf.write("\2HI\7Q\2\2IJ\7P\2\2JK\7[\2\2KL\7<\2\2LM\7\"\2\2MQ\3\2")
        buf.write("\2\2NP\n\2\2\2ON\3\2\2\2PS\3\2\2\2QO\3\2\2\2QR\3\2\2\2")
        buf.write("RV\3\2\2\2SQ\3\2\2\2TW\5\21\t\2UW\7\2\2\3VT\3\2\2\2VU")
        buf.write("\3\2\2\2W\16\3\2\2\2XZ\n\2\2\2YX\3\2\2\2Z[\3\2\2\2[Y\3")
        buf.write("\2\2\2[\\\3\2\2\2\\_\3\2\2\2]`\5\21\t\2^`\7\2\2\3_]\3")
        buf.write("\2\2\2_^\3\2\2\2`\20\3\2\2\2ab\7\f\2\2b\22\3\2\2\2\f\2")
        buf.write("\27 (-CQV[_\3\b\2\2")
        return buf.getvalue()


class TargetParagraphLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]


    NOT_A_TARGET_PARAGRAPH = 1
    PHONY_PARAGRAPH = 2
    TARGET_PARAGRAPH = 3
    BLANK_PARAGRAPH = 4

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
 ]

    symbolicNames = [ "<INVALID>",
            "NOT_A_TARGET_PARAGRAPH", "PHONY_PARAGRAPH", "TARGET_PARAGRAPH", 
            "BLANK_PARAGRAPH" ]

    ruleNames = [ "NOT_A_TARGET_PARAGRAPH", "PHONY_PARAGRAPH", "TARGET_PARAGRAPH", 
                  "BLANK_PARAGRAPH", "NOT_A_TARGET_LINE", "PHONY_LINE", 
                  "LINE", "EOL" ]

    grammarFileName = "TargetParagraphLexer.g4"

    def __init__(self, input=None):
        super().__init__(input)
        self.checkVersion("4.5.1")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


