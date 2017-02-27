# Generated from antlr4/MakefileRuleLexer.g4 by ANTLR 4.5.1
from antlr4 import *
from io import StringIO


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u0430\ud6d1\u8206\uad2d\u4417\uaef1\u8d80\uaadd\2\r")
        buf.write("g\b\1\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7")
        buf.write("\t\7\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r\t\r")
        buf.write("\3\2\3\2\3\2\3\2\3\3\3\3\3\4\3\4\3\5\3\5\3\5\3\5\3\5\3")
        buf.write("\6\3\6\3\6\3\6\3\6\3\6\3\7\3\7\3\7\3\7\3\b\3\b\7\b\66")
        buf.write("\n\b\f\b\16\b9\13\b\3\b\3\b\3\t\3\t\3\t\3\t\3\t\3\n\3")
        buf.write("\n\3\n\6\nE\n\n\r\n\16\nF\3\13\7\13J\n\13\f\13\16\13M")
        buf.write("\13\13\3\13\3\13\3\13\3\13\3\f\7\fT\n\f\f\f\16\fW\13\f")
        buf.write("\3\f\3\f\3\f\3\f\3\f\3\f\5\f_\n\f\5\fa\n\f\3\r\3\r\3\r")
        buf.write("\5\rf\n\r\2\2\16\4\3\6\4\b\5\n\6\f\7\16\b\20\t\22\n\24")
        buf.write("\13\26\f\30\r\32\2\4\2\3\6\4\2\13\13\"\"\3\2\f\f\b\2\13")
        buf.write("\f\"\"%%<=^^~~\4\2\f\f^^l\2\4\3\2\2\2\2\6\3\2\2\2\2\b")
        buf.write("\3\2\2\2\2\n\3\2\2\2\2\f\3\2\2\2\2\16\3\2\2\2\2\20\3\2")
        buf.write("\2\2\2\22\3\2\2\2\2\24\3\2\2\2\3\26\3\2\2\2\3\30\3\2\2")
        buf.write("\2\4\34\3\2\2\2\6 \3\2\2\2\b\"\3\2\2\2\n$\3\2\2\2\f)\3")
        buf.write("\2\2\2\16/\3\2\2\2\20\63\3\2\2\2\22<\3\2\2\2\24D\3\2\2")
        buf.write("\2\26K\3\2\2\2\30U\3\2\2\2\32e\3\2\2\2\34\35\7\f\2\2\35")
        buf.write("\36\3\2\2\2\36\37\b\2\2\2\37\5\3\2\2\2 !\7~\2\2!\7\3\2")
        buf.write("\2\2\"#\7<\2\2#\t\3\2\2\2$%\7=\2\2%&\3\2\2\2&\'\b\5\3")
        buf.write("\2\'(\b\5\2\2(\13\3\2\2\2)*\7\f\2\2*+\7\13\2\2+,\3\2\2")
        buf.write("\2,-\b\6\3\2-.\b\6\2\2.\r\3\2\2\2/\60\t\2\2\2\60\61\3")
        buf.write("\2\2\2\61\62\b\7\2\2\62\17\3\2\2\2\63\67\7%\2\2\64\66")
        buf.write("\n\3\2\2\65\64\3\2\2\2\669\3\2\2\2\67\65\3\2\2\2\678\3")
        buf.write("\2\2\28:\3\2\2\29\67\3\2\2\2:;\b\b\2\2;\21\3\2\2\2<=\7")
        buf.write("^\2\2=>\7\f\2\2>?\3\2\2\2?@\b\t\2\2@\23\3\2\2\2AE\n\4")
        buf.write("\2\2BC\7^\2\2CE\n\3\2\2DA\3\2\2\2DB\3\2\2\2EF\3\2\2\2")
        buf.write("FD\3\2\2\2FG\3\2\2\2G\25\3\2\2\2HJ\5\32\r\2IH\3\2\2\2")
        buf.write("JM\3\2\2\2KI\3\2\2\2KL\3\2\2\2LN\3\2\2\2MK\3\2\2\2NO\7")
        buf.write("\f\2\2OP\3\2\2\2PQ\b\13\4\2Q\27\3\2\2\2RT\5\32\r\2SR\3")
        buf.write("\2\2\2TW\3\2\2\2US\3\2\2\2UV\3\2\2\2V`\3\2\2\2WU\3\2\2")
        buf.write("\2XY\7\f\2\2Ya\7\13\2\2Z[\7^\2\2[\\\7\f\2\2\\^\3\2\2\2")
        buf.write("]_\7\13\2\2^]\3\2\2\2^_\3\2\2\2_a\3\2\2\2`X\3\2\2\2`Z")
        buf.write("\3\2\2\2a\31\3\2\2\2bf\n\5\2\2cd\7^\2\2df\n\3\2\2eb\3")
        buf.write("\2\2\2ec\3\2\2\2f\33\3\2\2\2\f\2\3\67DFKU^`e\5\b\2\2\7")
        buf.write("\3\2\6\2\2")
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
    RECIPE_TEXT_WITH_TERMINATION = 10
    RECIPE_TEXT = 11

    modeNames = [ "DEFAULT_MODE", "RECIPE" ]

    literalNames = [ "<INVALID>",
            "'\n'", "'|'", "':'", "';'", "'\n\t'", "'\\\n'" ]

    symbolicNames = [ "<INVALID>",
            "EOL", "PIPE", "COLON", "SEMICOLON", "INITIAL_TAB", "WHITESPACE", 
            "COMMENT", "LINE_CONTINATION", "IDENTIFIER", "RECIPE_TEXT_WITH_TERMINATION", 
            "RECIPE_TEXT" ]

    ruleNames = [ "EOL", "PIPE", "COLON", "SEMICOLON", "INITIAL_TAB", "WHITESPACE", 
                  "COMMENT", "LINE_CONTINATION", "IDENTIFIER", "RECIPE_TEXT_WITH_TERMINATION", 
                  "RECIPE_TEXT", "RECIPE_TEXT_BASE" ]

    grammarFileName = "MakefileRuleLexer.g4"

    def __init__(self, input=None):
        super().__init__(input)
        self.checkVersion("4.5.1")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


