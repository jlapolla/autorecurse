import app.antlr.custom
# Generated from antlr4/MakefileRuleLexer.g4 by ANTLR 4.5.1
from antlr4 import *
from io import StringIO


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u0430\ud6d1\u8206\uad2d\u4417\uaef1\u8d80\uaadd\2\f")
        buf.write("f\b\1\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7")
        buf.write("\t\7\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r\t\r")
        buf.write("\3\2\3\2\3\3\3\3\3\4\3\4\3\5\3\5\3\5\3\5\3\5\3\6\3\6\3")
        buf.write("\6\3\6\3\6\3\6\3\7\3\7\3\7\3\7\3\b\3\b\7\b\64\n\b\f\b")
        buf.write("\16\b\67\13\b\3\b\3\b\3\t\3\t\3\t\3\t\3\t\3\n\3\n\3\n")
        buf.write("\6\nC\n\n\r\n\16\nD\3\13\7\13H\n\13\f\13\16\13K\13\13")
        buf.write("\3\13\3\13\3\13\3\13\3\13\3\f\7\fS\n\f\f\f\16\fV\13\f")
        buf.write("\3\f\3\f\3\f\3\f\3\f\3\f\5\f^\n\f\5\f`\n\f\3\r\3\r\3\r")
        buf.write("\5\re\n\r\2\2\16\4\3\6\4\b\5\n\6\f\7\16\b\20\t\22\n\24")
        buf.write("\13\26\2\30\f\32\2\4\2\3\6\4\2\13\13\"\"\3\2\f\f\b\2\13")
        buf.write("\f\"\"%%<=^^~~\4\2\f\f^^k\2\4\3\2\2\2\2\6\3\2\2\2\2\b")
        buf.write("\3\2\2\2\2\n\3\2\2\2\2\f\3\2\2\2\2\16\3\2\2\2\2\20\3\2")
        buf.write("\2\2\2\22\3\2\2\2\2\24\3\2\2\2\3\26\3\2\2\2\3\30\3\2\2")
        buf.write("\2\4\34\3\2\2\2\6\36\3\2\2\2\b \3\2\2\2\n\"\3\2\2\2\f")
        buf.write("\'\3\2\2\2\16-\3\2\2\2\20\61\3\2\2\2\22:\3\2\2\2\24B\3")
        buf.write("\2\2\2\26I\3\2\2\2\30T\3\2\2\2\32d\3\2\2\2\34\35\7\f\2")
        buf.write("\2\35\5\3\2\2\2\36\37\7~\2\2\37\7\3\2\2\2 !\7<\2\2!\t")
        buf.write("\3\2\2\2\"#\7=\2\2#$\3\2\2\2$%\b\5\2\2%&\b\5\3\2&\13\3")
        buf.write("\2\2\2\'(\7\f\2\2()\7\13\2\2)*\3\2\2\2*+\b\6\2\2+,\b\6")
        buf.write("\3\2,\r\3\2\2\2-.\t\2\2\2./\3\2\2\2/\60\b\7\3\2\60\17")
        buf.write("\3\2\2\2\61\65\7%\2\2\62\64\n\3\2\2\63\62\3\2\2\2\64\67")
        buf.write("\3\2\2\2\65\63\3\2\2\2\65\66\3\2\2\2\668\3\2\2\2\67\65")
        buf.write("\3\2\2\289\b\b\3\29\21\3\2\2\2:;\7^\2\2;<\7\f\2\2<=\3")
        buf.write("\2\2\2=>\b\t\3\2>\23\3\2\2\2?C\n\4\2\2@A\7^\2\2AC\n\3")
        buf.write("\2\2B?\3\2\2\2B@\3\2\2\2CD\3\2\2\2DB\3\2\2\2DE\3\2\2\2")
        buf.write("E\25\3\2\2\2FH\5\32\r\2GF\3\2\2\2HK\3\2\2\2IG\3\2\2\2")
        buf.write("IJ\3\2\2\2JL\3\2\2\2KI\3\2\2\2LM\7\f\2\2MN\3\2\2\2NO\b")
        buf.write("\13\4\2OP\b\13\5\2P\27\3\2\2\2QS\5\32\r\2RQ\3\2\2\2SV")
        buf.write("\3\2\2\2TR\3\2\2\2TU\3\2\2\2U_\3\2\2\2VT\3\2\2\2WX\7\f")
        buf.write("\2\2X`\7\13\2\2YZ\7^\2\2Z[\7\f\2\2[]\3\2\2\2\\^\7\13\2")
        buf.write("\2]\\\3\2\2\2]^\3\2\2\2^`\3\2\2\2_W\3\2\2\2_Y\3\2\2\2")
        buf.write("`\31\3\2\2\2ae\n\5\2\2bc\7^\2\2ce\n\3\2\2da\3\2\2\2db")
        buf.write("\3\2\2\2e\33\3\2\2\2\f\2\3\65BDIT]_d\6\7\3\2\b\2\2\t\f")
        buf.write("\2\6\2\2")
        return buf.getvalue()


class MakefileRuleLexer(app.antlr.custom.CustomLexer):

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
    RECIPE_LINE = 10

    modeNames = [ "DEFAULT_MODE", "RECIPE" ]

    literalNames = [ "<INVALID>",
            "'\n'", "'|'", "':'", "';'", "'\n\t'", "'\\\n'" ]

    symbolicNames = [ "<INVALID>",
            "EOL", "PIPE", "COLON", "SEMICOLON", "INITIAL_TAB", "WHITESPACE", 
            "COMMENT", "LINE_CONTINATION", "IDENTIFIER", "RECIPE_LINE" ]

    ruleNames = [ "EOL", "PIPE", "COLON", "SEMICOLON", "INITIAL_TAB", "WHITESPACE", 
                  "COMMENT", "LINE_CONTINATION", "IDENTIFIER", "RECIPE_LINE_WITH_TERMINATION", 
                  "RECIPE_LINE", "RECIPE_TEXT_BASE" ]

    grammarFileName = "MakefileRuleLexer.g4"

    def __init__(self, input=None):
        super().__init__(input)
        self.checkVersion("4.5.1")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


