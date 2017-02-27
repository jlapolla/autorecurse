# Generated from antlr4/MakefileRuleParser.g4 by ANTLR 4.5.1
# encoding: utf-8
from antlr4 import *
from io import StringIO

def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u0430\ud6d1\u8206\uad2d\u4417\uaef1\u8d80\uaadd\3\f")
        buf.write("\60\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\3\2\6\2\16")
        buf.write("\n\2\r\2\16\2\17\3\2\3\2\7\2\24\n\2\f\2\16\2\27\13\2\3")
        buf.write("\2\3\2\7\2\33\n\2\f\2\16\2\36\13\2\5\2 \n\2\3\2\5\2#\n")
        buf.write("\2\3\3\3\3\3\4\3\4\3\5\3\5\3\6\6\6,\n\6\r\6\16\6-\3\6")
        buf.write("\2\2\7\2\4\6\b\n\2\2\60\2\r\3\2\2\2\4$\3\2\2\2\6&\3\2")
        buf.write("\2\2\b(\3\2\2\2\n+\3\2\2\2\f\16\5\4\3\2\r\f\3\2\2\2\16")
        buf.write("\17\3\2\2\2\17\r\3\2\2\2\17\20\3\2\2\2\20\21\3\2\2\2\21")
        buf.write("\25\7\5\2\2\22\24\5\6\4\2\23\22\3\2\2\2\24\27\3\2\2\2")
        buf.write("\25\23\3\2\2\2\25\26\3\2\2\2\26\37\3\2\2\2\27\25\3\2\2")
        buf.write("\2\30\34\7\4\2\2\31\33\5\b\5\2\32\31\3\2\2\2\33\36\3\2")
        buf.write("\2\2\34\32\3\2\2\2\34\35\3\2\2\2\35 \3\2\2\2\36\34\3\2")
        buf.write("\2\2\37\30\3\2\2\2\37 \3\2\2\2 \"\3\2\2\2!#\5\n\6\2\"")
        buf.write("!\3\2\2\2\"#\3\2\2\2#\3\3\2\2\2$%\7\13\2\2%\5\3\2\2\2")
        buf.write("&\'\7\13\2\2\'\7\3\2\2\2()\7\13\2\2)\t\3\2\2\2*,\7\f\2")
        buf.write("\2+*\3\2\2\2,-\3\2\2\2-+\3\2\2\2-.\3\2\2\2.\13\3\2\2\2")
        buf.write("\b\17\25\34\37\"-")
        return buf.getvalue()


class MakefileRuleParser ( Parser ):

    grammarFileName = "MakefileRuleParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'\n'", "'|'", "':'", "';'", "'\n\t'", 
                     "<INVALID>", "<INVALID>", "'\\\n'" ]

    symbolicNames = [ "<INVALID>", "EOL", "PIPE", "COLON", "SEMICOLON", 
                      "INITIAL_TAB", "WHITESPACE", "COMMENT", "LINE_CONTINATION", 
                      "IDENTIFIER", "RECIPE_TEXT" ]

    RULE_makefileRule = 0
    RULE_target = 1
    RULE_prerequisite = 2
    RULE_orderOnlyPrerequisite = 3
    RULE_recipe = 4

    ruleNames =  [ "makefileRule", "target", "prerequisite", "orderOnlyPrerequisite", 
                   "recipe" ]

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
    RECIPE_TEXT=10

    def __init__(self, input:TokenStream):
        super().__init__(input)
        self.checkVersion("4.5.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None



    class MakefileRuleContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def COLON(self):
            return self.getToken(MakefileRuleParser.COLON, 0)

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

        def recipe(self):
            return self.getTypedRuleContext(MakefileRuleParser.RecipeContext,0)


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
        self.enterRule(localctx, 0, self.RULE_makefileRule)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 11 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 10
                self.target()
                self.state = 13 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==MakefileRuleParser.IDENTIFIER):
                    break

            self.state = 15
            self.match(MakefileRuleParser.COLON)
            self.state = 19
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==MakefileRuleParser.IDENTIFIER:
                self.state = 16
                self.prerequisite()
                self.state = 21
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 29
            _la = self._input.LA(1)
            if _la==MakefileRuleParser.PIPE:
                self.state = 22
                self.match(MakefileRuleParser.PIPE)
                self.state = 26
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==MakefileRuleParser.IDENTIFIER:
                    self.state = 23
                    self.orderOnlyPrerequisite()
                    self.state = 28
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)



            self.state = 32
            _la = self._input.LA(1)
            if _la==MakefileRuleParser.RECIPE_TEXT:
                self.state = 31
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
        self.enterRule(localctx, 2, self.RULE_target)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 34
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
        self.enterRule(localctx, 4, self.RULE_prerequisite)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 36
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
        self.enterRule(localctx, 6, self.RULE_orderOnlyPrerequisite)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 38
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

        def RECIPE_TEXT(self, i:int=None):
            if i is None:
                return self.getTokens(MakefileRuleParser.RECIPE_TEXT)
            else:
                return self.getToken(MakefileRuleParser.RECIPE_TEXT, i)

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
        self.enterRule(localctx, 8, self.RULE_recipe)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 41 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 40
                self.match(MakefileRuleParser.RECIPE_TEXT)
                self.state = 43 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==MakefileRuleParser.RECIPE_TEXT):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





