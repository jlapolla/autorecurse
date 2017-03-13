import autorecurse.lib.antlr4.custom
# Generated from antlr4/MakefileRuleParser.g4 by ANTLR 4.5.1
# encoding: utf-8
from antlr4 import *
from io import StringIO

def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u0430\ud6d1\u8206\uad2d\u4417\uaef1\u8d80\uaadd\3\f")
        buf.write("8\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\3\2")
        buf.write("\3\2\5\2\21\n\2\3\3\6\3\24\n\3\r\3\16\3\25\3\3\3\3\7\3")
        buf.write("\32\n\3\f\3\16\3\35\13\3\3\3\3\3\7\3!\n\3\f\3\16\3$\13")
        buf.write("\3\5\3&\n\3\3\3\3\3\3\4\3\4\3\5\3\5\3\6\3\6\3\7\6\7\61")
        buf.write("\n\7\r\7\16\7\62\3\7\5\7\66\n\7\3\7\2\2\b\2\4\6\b\n\f")
        buf.write("\2\3\4\2\3\3\f\f8\2\20\3\2\2\2\4\23\3\2\2\2\6)\3\2\2\2")
        buf.write("\b+\3\2\2\2\n-\3\2\2\2\f\65\3\2\2\2\16\21\5\4\3\2\17\21")
        buf.write("\7\3\2\2\20\16\3\2\2\2\20\17\3\2\2\2\21\3\3\2\2\2\22\24")
        buf.write("\5\6\4\2\23\22\3\2\2\2\24\25\3\2\2\2\25\23\3\2\2\2\25")
        buf.write("\26\3\2\2\2\26\27\3\2\2\2\27\33\7\5\2\2\30\32\5\b\5\2")
        buf.write("\31\30\3\2\2\2\32\35\3\2\2\2\33\31\3\2\2\2\33\34\3\2\2")
        buf.write("\2\34%\3\2\2\2\35\33\3\2\2\2\36\"\7\4\2\2\37!\5\n\6\2")
        buf.write(" \37\3\2\2\2!$\3\2\2\2\" \3\2\2\2\"#\3\2\2\2#&\3\2\2\2")
        buf.write("$\"\3\2\2\2%\36\3\2\2\2%&\3\2\2\2&\'\3\2\2\2\'(\5\f\7")
        buf.write("\2(\5\3\2\2\2)*\7\13\2\2*\7\3\2\2\2+,\7\13\2\2,\t\3\2")
        buf.write("\2\2-.\7\13\2\2.\13\3\2\2\2/\61\t\2\2\2\60/\3\2\2\2\61")
        buf.write("\62\3\2\2\2\62\60\3\2\2\2\62\63\3\2\2\2\63\66\3\2\2\2")
        buf.write("\64\66\7\2\2\3\65\60\3\2\2\2\65\64\3\2\2\2\66\r\3\2\2")
        buf.write("\2\t\20\25\33\"%\62\65")
        return buf.getvalue()


class MakefileRuleParser ( autorecurse.lib.antlr4.custom.CustomParser ):

    grammarFileName = "MakefileRuleParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'\n'", "'|'", "':'", "';'", "'\n\t'", 
                     "<INVALID>", "<INVALID>", "'\\\n'" ]

    symbolicNames = [ "<INVALID>", "EOL", "PIPE", "COLON", "SEMICOLON", 
                      "INITIAL_TAB", "WHITESPACE", "COMMENT", "LINE_CONTINATION", 
                      "IDENTIFIER", "RECIPE_LINE" ]

    RULE_declaration = 0
    RULE_makefileRule = 1
    RULE_target = 2
    RULE_prerequisite = 3
    RULE_orderOnlyPrerequisite = 4
    RULE_recipe = 5

    ruleNames =  [ "declaration", "makefileRule", "target", "prerequisite", 
                   "orderOnlyPrerequisite", "recipe" ]

    EOF = Token.EOF
    EOL=1
    PIPE=2
    COLON=3
    SEMICOLON=4
    INITIAL_TAB=5
    WHITESPACE=6
    COMMENT=7
    LINE_CONTINATION=8
    IDENTIFIER=9
    RECIPE_LINE=10

    def __init__(self, input:TokenStream):
        super().__init__(input)
        self.checkVersion("4.5.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None



    class DeclarationContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def makefileRule(self):
            return self.getTypedRuleContext(MakefileRuleParser.MakefileRuleContext,0)


        def EOL(self):
            return self.getToken(MakefileRuleParser.EOL, 0)

        def getRuleIndex(self):
            return MakefileRuleParser.RULE_declaration

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDeclaration" ):
                listener.enterDeclaration(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDeclaration" ):
                listener.exitDeclaration(self)




    def declaration(self):

        localctx = MakefileRuleParser.DeclarationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_declaration)
        try:
            self.state = 14
            token = self._input.LA(1)
            if token in [MakefileRuleParser.IDENTIFIER]:
                self.enterOuterAlt(localctx, 1)
                self.state = 12
                self.makefileRule()

            elif token in [MakefileRuleParser.EOL]:
                self.enterOuterAlt(localctx, 2)
                self.state = 13
                self.match(MakefileRuleParser.EOL)

            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class MakefileRuleContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def COLON(self):
            return self.getToken(MakefileRuleParser.COLON, 0)

        def recipe(self):
            return self.getTypedRuleContext(MakefileRuleParser.RecipeContext,0)


        def target(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MakefileRuleParser.TargetContext)
            else:
                return self.getTypedRuleContext(MakefileRuleParser.TargetContext,i)


        def prerequisite(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MakefileRuleParser.PrerequisiteContext)
            else:
                return self.getTypedRuleContext(MakefileRuleParser.PrerequisiteContext,i)


        def PIPE(self):
            return self.getToken(MakefileRuleParser.PIPE, 0)

        def orderOnlyPrerequisite(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MakefileRuleParser.OrderOnlyPrerequisiteContext)
            else:
                return self.getTypedRuleContext(MakefileRuleParser.OrderOnlyPrerequisiteContext,i)


        def getRuleIndex(self):
            return MakefileRuleParser.RULE_makefileRule

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMakefileRule" ):
                listener.enterMakefileRule(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMakefileRule" ):
                listener.exitMakefileRule(self)




    def makefileRule(self):

        localctx = MakefileRuleParser.MakefileRuleContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_makefileRule)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 17 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 16
                self.target()
                self.state = 19 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==MakefileRuleParser.IDENTIFIER):
                    break

            self.state = 21
            self.match(MakefileRuleParser.COLON)
            self.state = 25
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==MakefileRuleParser.IDENTIFIER:
                self.state = 22
                self.prerequisite()
                self.state = 27
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 35
            _la = self._input.LA(1)
            if _la==MakefileRuleParser.PIPE:
                self.state = 28
                self.match(MakefileRuleParser.PIPE)
                self.state = 32
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==MakefileRuleParser.IDENTIFIER:
                    self.state = 29
                    self.orderOnlyPrerequisite()
                    self.state = 34
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)



            self.state = 37
            self.recipe()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class TargetContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self):
            return self.getToken(MakefileRuleParser.IDENTIFIER, 0)

        def getRuleIndex(self):
            return MakefileRuleParser.RULE_target

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTarget" ):
                listener.enterTarget(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTarget" ):
                listener.exitTarget(self)




    def target(self):

        localctx = MakefileRuleParser.TargetContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_target)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 39
            self.match(MakefileRuleParser.IDENTIFIER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class PrerequisiteContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self):
            return self.getToken(MakefileRuleParser.IDENTIFIER, 0)

        def getRuleIndex(self):
            return MakefileRuleParser.RULE_prerequisite

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPrerequisite" ):
                listener.enterPrerequisite(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPrerequisite" ):
                listener.exitPrerequisite(self)




    def prerequisite(self):

        localctx = MakefileRuleParser.PrerequisiteContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_prerequisite)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 41
            self.match(MakefileRuleParser.IDENTIFIER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class OrderOnlyPrerequisiteContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self):
            return self.getToken(MakefileRuleParser.IDENTIFIER, 0)

        def getRuleIndex(self):
            return MakefileRuleParser.RULE_orderOnlyPrerequisite

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOrderOnlyPrerequisite" ):
                listener.enterOrderOnlyPrerequisite(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOrderOnlyPrerequisite" ):
                listener.exitOrderOnlyPrerequisite(self)




    def orderOnlyPrerequisite(self):

        localctx = MakefileRuleParser.OrderOnlyPrerequisiteContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_orderOnlyPrerequisite)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 43
            self.match(MakefileRuleParser.IDENTIFIER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class RecipeContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def RECIPE_LINE(self, i:int=None):
            if i is None:
                return self.getTokens(MakefileRuleParser.RECIPE_LINE)
            else:
                return self.getToken(MakefileRuleParser.RECIPE_LINE, i)

        def EOL(self, i:int=None):
            if i is None:
                return self.getTokens(MakefileRuleParser.EOL)
            else:
                return self.getToken(MakefileRuleParser.EOL, i)

        def EOF(self):
            return self.getToken(MakefileRuleParser.EOF, 0)

        def getRuleIndex(self):
            return MakefileRuleParser.RULE_recipe

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterRecipe" ):
                listener.enterRecipe(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitRecipe" ):
                listener.exitRecipe(self)




    def recipe(self):

        localctx = MakefileRuleParser.RecipeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_recipe)
        self._la = 0 # Token type
        try:
            self.state = 51
            token = self._input.LA(1)
            if token in [MakefileRuleParser.EOL, MakefileRuleParser.RECIPE_LINE]:
                self.enterOuterAlt(localctx, 1)
                self.state = 46 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 45
                    _la = self._input.LA(1)
                    if not(_la==MakefileRuleParser.EOL or _la==MakefileRuleParser.RECIPE_LINE):
                        self._errHandler.recoverInline(self)
                    else:
                        self.consume()
                    self.state = 48 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==MakefileRuleParser.EOL or _la==MakefileRuleParser.RECIPE_LINE):
                        break


            elif token in [MakefileRuleParser.EOF]:
                self.enterOuterAlt(localctx, 2)
                self.state = 50
                self.match(MakefileRuleParser.EOF)

            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





