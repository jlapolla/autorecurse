from app.lib.makefile import *
from app.antlr.grammar import *
from app.antlr.parsemakefilerule import MakefileRuleParser
from antlr4 import *
from antlr4.error.Errors import ParseCancellationException
import unittest


class TestMakefileTarget(unittest.TestCase):

    def test_basic_operation(self):
        string = """\\backslash\\target\\:: source\\ |\t\\back\tslash\\ 
\t  Hurray:|;#\t it works\\quite\\well\\
  And this is still recipe text \\
\tAnd this tab is removed # Not a comment!
# Interspersed comment

\t  More recipe (trailing spaces)  
next/target : next\\ source\\
another-source\\
\t and-another-source;|:recipes!!;; # Oh\tboy!
\t :#I can't wait...
# Still in the recipe
\t ...until this recipe is over!
# New line with lone tab
\t
a b c: d | e"""

        input_ = InputStream(string)
        lexer = MakefileRuleLexer(input_)
        token_stream = CommonTokenStream(lexer)
        parser = MakefileRuleParser(token_stream)
        parser._errHandler = BailErrorStrategy()

        ctx = parser.makefileRule()
        self.assertIsNone(ctx.exception)
        target = MakefileTarget.make_from_parse_context(ctx, 0)
        self.assertEqual(target.path, '\\backslash\\target\\:')
        it = target.prerequisites
        it.move_to_next()
        self.assertEqual(it.current_item, 'source\\ ')
        it.move_to_next()
        self.assertIs(it.is_at_end, True)
        it = target.order_only_prerequisites
        it.move_to_next()
        self.assertEqual(it.current_item, '\\back')
        it.move_to_next()
        self.assertEqual(it.current_item, 'slash\\ ')
        it.move_to_next()
        self.assertIs(it.is_at_end, True)

        ctx = parser.makefileRule()
        self.assertIsNone(ctx.exception)
        target = MakefileTarget.make_from_parse_context(ctx, 0)
        self.assertEqual(target.path, 'next/target')
        it = target.prerequisites
        it.move_to_next()
        self.assertEqual(it.current_item, 'next\\ source')
        it.move_to_next()
        self.assertEqual(it.current_item, 'another-source')
        it.move_to_next()
        self.assertEqual(it.current_item, 'and-another-source')
        it.move_to_next()
        self.assertIs(it.is_at_end, True)
        it = target.order_only_prerequisites
        it.move_to_next()
        self.assertIs(it.is_at_end, True)

        ctx = parser.makefileRule()
        self.assertIsNone(ctx.exception)
        target = MakefileTarget.make_from_parse_context(ctx, 0)
        self.assertEqual(target.path, 'a')
        it = target.prerequisites
        it.move_to_next()
        self.assertEqual(it.current_item, 'd')
        it.move_to_next()
        self.assertIs(it.is_at_end, True)
        it = target.order_only_prerequisites
        it.move_to_next()
        self.assertEqual(it.current_item, 'e')
        it.move_to_next()
        self.assertIs(it.is_at_end, True)
        target = MakefileTarget.make_from_parse_context(ctx, 1)
        self.assertEqual(target.path, 'b')
        it = target.prerequisites
        it.move_to_next()
        self.assertEqual(it.current_item, 'd')
        it.move_to_next()
        self.assertIs(it.is_at_end, True)
        it = target.order_only_prerequisites
        it.move_to_next()
        self.assertEqual(it.current_item, 'e')
        it.move_to_next()
        self.assertIs(it.is_at_end, True)
        target = MakefileTarget.make_from_parse_context(ctx, 2)
        self.assertEqual(target.path, 'c')
        it = target.prerequisites
        it.move_to_next()
        self.assertEqual(it.current_item, 'd')
        it.move_to_next()
        self.assertIs(it.is_at_end, True)
        it = target.order_only_prerequisites
        it.move_to_next()
        self.assertEqual(it.current_item, 'e')
        it.move_to_next()
        self.assertIs(it.is_at_end, True)


