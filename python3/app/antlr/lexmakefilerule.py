# Generated from antlr4/MakefileRuleLexer.g4 by ANTLR 4.5.1
from antlr4 import *
from io import StringIO


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u0430\ud6d1\u8206\uad2d\u4417\uaef1\u8d80\uaadd\2\f")
        buf.write("h\b\1\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7")
        buf.write("\t\7\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r\t\r")
        buf.write("\3\2\3\2\3\2\3\2\3\3\3\3\3\4\3\4\3\5\3\5\3\5\3\5\3\5\3")
        buf.write("\6\3\6\3\6\3\6\3\6\3\6\3\7\3\7\3\7\3\7\3\b\3\b\7\b\66")
        buf.write("\n\b\f\b\16\b9\13\b\3\b\3\b\3\t\3\t\3\t\3\t\3\t\3\n\3")
        buf.write("\n\3\n\6\nE\n\n\r\n\16\nF\3\13\7\13J\n\13\f\13\16\13M")
        buf.write("\13\13\3\13\3\13\3\13\3\13\3\13\3\f\7\fU\n\f\f\f\16\f")
        buf.write("X\13\f\3\f\3\f\3\f\3\f\3\f\3\f\5\f`\n\f\5\fb\n\f\3\r\3")
        buf.write("\r\3\r\5\rg\n\r\2\2\16\4\3\6\4\b\5\n\6\f\7\16\b\20\t\22")
        buf.write("\n\24\13\26\2\30\f\32\2\4\2\3\6\4\2\13\13\"\"\3\2\f\f")
        buf.write("\b\2\13\f\"\"%%<=^^~~\4\2\f\f^^m\2\4\3\2\2\2\2\6\3\2\2")
        buf.write("\2\2\b\3\2\2\2\2\n\3\2\2\2\2\f\3\2\2\2\2\16\3\2\2\2\2")
        buf.write("\20\3\2\2\2\2\22\3\2\2\2\2\24\3\2\2\2\3\26\3\2\2\2\3\30")
        buf.write("\3\2\2\2\4\34\3\2\2\2\6 \3\2\2\2\b\"\3\2\2\2\n$\3\2\2")
        buf.write("\2\f)\3\2\2\2\16/\3\2\2\2\20\63\3\2\2\2\22<\3\2\2\2\24")
        buf.write("D\3\2\2\2\26K\3\2\2\2\30V\3\2\2\2\32f\3\2\2\2\34\35\7")
        buf.write("\f\2\2\35\36\3\2\2\2\36\37\b\2\2\2\37\5\3\2\2\2 !\7~\2")
        buf.write("\2!\7\3\2\2\2\"#\7<\2\2#\t\3\2\2\2$%\7=\2\2%&\3\2\2\2")
        buf.write("&\'\b\5\3\2\'(\b\5\2\2(\13\3\2\2\2)*\7\f\2\2*+\7\13\2")
        buf.write("\2+,\3\2\2\2,-\b\6\3\2-.\b\6\2\2.\r\3\2\2\2/\60\t\2\2")
        buf.write("\2\60\61\3\2\2\2\61\62\b\7\2\2\62\17\3\2\2\2\63\67\7%")
        buf.write("\2\2\64\66\n\3\2\2\65\64\3\2\2\2\669\3\2\2\2\67\65\3\2")
        buf.write("\2\2\678\3\2\2\28:\3\2\2\29\67\3\2\2\2:;\b\b\2\2;\21\3")
        buf.write("\2\2\2<=\7^\2\2=>\7\f\2\2>?\3\2\2\2?@\b\t\2\2@\23\3\2")
        buf.write("\2\2AE\n\4\2\2BC\7^\2\2CE\n\3\2\2DA\3\2\2\2DB\3\2\2\2")
        buf.write("EF\3\2\2\2FD\3\2\2\2FG\3\2\2\2G\25\3\2\2\2HJ\5\32\r\2")
        buf.write("IH\3\2\2\2JM\3\2\2\2KI\3\2\2\2KL\3\2\2\2LN\3\2\2\2MK\3")
        buf.write("\2\2\2NO\7\f\2\2OP\3\2\2\2PQ\b\13\4\2QR\b\13\5\2R\27\3")
        buf.write("\2\2\2SU\5\32\r\2TS\3\2\2\2UX\3\2\2\2VT\3\2\2\2VW\3\2")
        buf.write("\2\2Wa\3\2\2\2XV\3\2\2\2YZ\7\f\2\2Zb\7\13\2\2[\\\7^\2")
        buf.write("\2\\]\7\f\2\2]_\3\2\2\2^`\7\13\2\2_^\3\2\2\2_`\3\2\2\2")
        buf.write("`b\3\2\2\2aY\3\2\2\2a[\3\2\2\2b\31\3\2\2\2cg\n\5\2\2d")
        buf.write("e\7^\2\2eg\n\3\2\2fc\3\2\2\2fd\3\2\2\2g\33\3\2\2\2\f\2")
        buf.write("\3\67DFKV_af\6\b\2\2\7\3\2\t\f\2\6\2\2")
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

    modeNames = [ "DEFAULT_MODE", "RECIPE" ]

    literalNames = [ "<INVALID>",
            "'\n'", "'|'", "':'", "';'", "'\n\t'", "'\\\n'" ]

    symbolicNames = [ "<INVALID>",
            "EOL", "PIPE", "COLON", "SEMICOLON", "INITIAL_TAB", "WHITESPACE", 
            "COMMENT", "LINE_CONTINATION", "IDENTIFIER", "RECIPE_TEXT" ]

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


