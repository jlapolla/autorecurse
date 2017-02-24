# Generated from antlr4/MakefileRuleLexer.g4 by ANTLR 4.5.1
from antlr4 import *
from io import StringIO


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u0430\ud6d1\u8206\uad2d\u4417\uaef1\u8d80\uaadd\2\r")
        buf.write("T\b\1\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7")
        buf.write("\t\7\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r\t\r")
        buf.write("\3\2\3\2\3\3\3\3\3\4\3\4\3\5\3\5\3\5\3\5\3\6\3\6\3\6\3")
        buf.write("\6\3\6\3\7\3\7\3\7\3\7\3\b\3\b\7\b\62\n\b\f\b\16\b\65")
        buf.write("\13\b\3\b\3\b\3\t\3\t\3\t\3\t\3\t\3\n\6\n?\n\n\r\n\16")
        buf.write("\n@\3\13\3\13\3\13\3\13\3\f\3\f\3\f\3\f\3\f\5\fL\n\f\3")
        buf.write("\r\3\r\3\r\6\rQ\n\r\r\r\16\rR\2\2\16\4\3\6\4\b\5\n\6\f")
        buf.write("\7\16\b\20\t\22\n\24\13\26\f\30\r\32\2\4\2\3\6\4\2\13")
        buf.write("\13\"\"\3\2\f\f\7\2\13\f\"\"%%<=~~\4\2\f\f^^V\2\4\3\2")
        buf.write("\2\2\2\6\3\2\2\2\2\b\3\2\2\2\2\n\3\2\2\2\2\f\3\2\2\2\2")
        buf.write("\16\3\2\2\2\2\20\3\2\2\2\2\22\3\2\2\2\2\24\3\2\2\2\3\26")
        buf.write("\3\2\2\2\3\30\3\2\2\2\4\34\3\2\2\2\6\36\3\2\2\2\b \3\2")
        buf.write("\2\2\n\"\3\2\2\2\f&\3\2\2\2\16+\3\2\2\2\20/\3\2\2\2\22")
        buf.write("8\3\2\2\2\24>\3\2\2\2\26B\3\2\2\2\30F\3\2\2\2\32P\3\2")
        buf.write("\2\2\34\35\7\f\2\2\35\5\3\2\2\2\36\37\7~\2\2\37\7\3\2")
        buf.write("\2\2 !\7<\2\2!\t\3\2\2\2\"#\7=\2\2#$\3\2\2\2$%\b\5\2\2")
        buf.write("%\13\3\2\2\2&\'\7\f\2\2\'(\7\13\2\2()\3\2\2\2)*\b\6\2")
        buf.write("\2*\r\3\2\2\2+,\t\2\2\2,-\3\2\2\2-.\b\7\3\2.\17\3\2\2")
        buf.write("\2/\63\7%\2\2\60\62\n\3\2\2\61\60\3\2\2\2\62\65\3\2\2")
        buf.write("\2\63\61\3\2\2\2\63\64\3\2\2\2\64\66\3\2\2\2\65\63\3\2")
        buf.write("\2\2\66\67\b\b\3\2\67\21\3\2\2\289\7^\2\29:\7\f\2\2:;")
        buf.write("\3\2\2\2;<\b\t\3\2<\23\3\2\2\2=?\n\4\2\2>=\3\2\2\2?@\3")
        buf.write("\2\2\2@>\3\2\2\2@A\3\2\2\2A\25\3\2\2\2BC\5\32\r\2CD\3")
        buf.write("\2\2\2DE\b\13\4\2E\27\3\2\2\2FG\5\32\r\2GH\7^\2\2HI\7")
        buf.write("\f\2\2IK\3\2\2\2JL\7\13\2\2KJ\3\2\2\2KL\3\2\2\2L\31\3")
        buf.write("\2\2\2MQ\n\5\2\2NO\7^\2\2OQ\n\3\2\2PM\3\2\2\2PN\3\2\2")
        buf.write("\2QR\3\2\2\2RP\3\2\2\2RS\3\2\2\2S\33\3\2\2\2\t\2\3\63")
        buf.write("@KPR\5\7\3\2\b\2\2\6\2\2")
        return buf.getvalue()


class MakefileRuleLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    RECIPE = 1

    EOL = 1
    PIPE = 2
    COLON = 3
    SEMICOLON = 4
    INITIAL_TAB = 5
    WHITESPACE = 6
    COMMENT = 7
    LINE_CONTINATION = 8
    IDENTIFIER = 9
    RECIPE_TEXT = 10
    RECIPE_TEXT_MULTI = 11

    modeNames = [ "DEFAULT_MODE", "RECIPE" ]

    literalNames = [ "<INVALID>",
            "'\n'", "'|'", "':'", "';'", "'\n\t'", "'\\\n'" ]

    symbolicNames = [ "<INVALID>",
            "EOL", "PIPE", "COLON", "SEMICOLON", "INITIAL_TAB", "WHITESPACE", 
            "COMMENT", "LINE_CONTINATION", "IDENTIFIER", "RECIPE_TEXT", 
            "RECIPE_TEXT_MULTI" ]

    ruleNames = [ "EOL", "PIPE", "COLON", "SEMICOLON", "INITIAL_TAB", "WHITESPACE", 
                  "COMMENT", "LINE_CONTINATION", "IDENTIFIER", "RECIPE_TEXT", 
                  "RECIPE_TEXT_MULTI", "RECIPE_TEXT_BASE" ]

    grammarFileName = "MakefileRuleLexer.g4"

    def __init__(self, input=None):
        super().__init__(input)
        self.checkVersion("4.5.1")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


