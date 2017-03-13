from autorecurse.lib.generics import StringBuffer
from autorecurse.app.antlr.grammar import *
from antlr4 import *
from antlr4.error.Errors import ParseCancellationException
import unittest


class TestMakefileRuleParser(unittest.TestCase):

    def test_basic_operation(self):
        string = """# A comment
\\backslash\\target\\:: source\\ |\t\\back\tslash\\ 
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
all:|;

\t
\t\\
and here is the recipe finally
clean:;
dist:;
\t
a b c:
a b c: d | e
a b c: d

# A comment

\t# The recipe!
a:"""
        input_ = InputStream(string)
        lexer = MakefileRuleLexer(input_)
        token_stream = CommonTokenStream(lexer)
        parser = MakefileRuleParser(token_stream)
        with self.assertRaises(ParseCancellationException):
            parser.makefileRule() # Because the first token is EOL
        token_stream.consume() # Consume the EOL token
        ctx = parser.makefileRule()
        self.assertIsNone(ctx.exception)
        self.assertEqual(len(ctx.target()), 1)
        self.assertEqual(ctx.target()[0].IDENTIFIER().symbol.text, '\\backslash\\target\\:')
        self.assertEqual(len(ctx.prerequisite()), 1)
        self.assertEqual(ctx.prerequisite()[0].IDENTIFIER().symbol.text, 'source\\ ')
        self.assertEqual(len(ctx.orderOnlyPrerequisite()), 2)
        self.assertEqual(ctx.orderOnlyPrerequisite()[0].IDENTIFIER().symbol.text, '\\back')
        self.assertEqual(ctx.orderOnlyPrerequisite()[1].IDENTIFIER().symbol.text, 'slash\\ ')
        self.assertEqual(len(ctx.recipe().RECIPE_LINE()), 4)
        self.assertEqual(ctx.recipe().RECIPE_LINE()[0].symbol.text, '  Hurray:|;#\t it works\\quite\\well\\\n')
        self.assertEqual(ctx.recipe().RECIPE_LINE()[1].symbol.text, '  And this is still recipe text \\\n\t')
        self.assertEqual(ctx.recipe().RECIPE_LINE()[2].symbol.text, 'And this tab is removed # Not a comment!\n')
        self.assertEqual(ctx.recipe().RECIPE_LINE()[3].symbol.text, '  More recipe (trailing spaces)  \n')
        ctx = parser.makefileRule()
        self.assertIsNone(ctx.exception)
        self.assertEqual(len(ctx.target()), 1)
        self.assertEqual(ctx.target()[0].IDENTIFIER().symbol.text, 'next/target')
        self.assertEqual(len(ctx.prerequisite()), 3)
        self.assertEqual(ctx.prerequisite()[0].IDENTIFIER().symbol.text, 'next\\ source')
        self.assertEqual(ctx.prerequisite()[1].IDENTIFIER().symbol.text, 'another-source')
        self.assertEqual(ctx.prerequisite()[2].IDENTIFIER().symbol.text, 'and-another-source')
        self.assertEqual(len(ctx.orderOnlyPrerequisite()), 0)
        self.assertEqual(len(ctx.recipe().RECIPE_LINE()), 4)
        self.assertEqual(ctx.recipe().RECIPE_LINE()[0].symbol.text, '|:recipes!!;; # Oh\tboy!\n\t')
        self.assertEqual(ctx.recipe().RECIPE_LINE()[1].symbol.text, ' :#I can\'t wait...\n')
        self.assertEqual(ctx.recipe().RECIPE_LINE()[2].symbol.text, ' ...until this recipe is over!\n')
        self.assertEqual(ctx.recipe().RECIPE_LINE()[3].symbol.text, '\n')
        ctx = parser.makefileRule()
        self.assertIsNone(ctx.exception)
        self.assertEqual(len(ctx.target()), 1)
        self.assertEqual(ctx.target()[0].IDENTIFIER().symbol.text, 'all')
        self.assertEqual(len(ctx.prerequisite()), 0)
        self.assertEqual(len(ctx.orderOnlyPrerequisite()), 0)
        self.assertEqual(len(ctx.recipe().RECIPE_LINE()), 4)
        self.assertEqual(ctx.recipe().RECIPE_LINE()[0].symbol.text, '\n')
        self.assertEqual(ctx.recipe().RECIPE_LINE()[1].symbol.text, '\n\t')
        self.assertEqual(ctx.recipe().RECIPE_LINE()[2].symbol.text, '\\\n')
        self.assertEqual(ctx.recipe().RECIPE_LINE()[3].symbol.text, 'and here is the recipe finally\n')
        ctx = parser.makefileRule()
        self.assertIsNone(ctx.exception)
        self.assertEqual(len(ctx.target()), 1)
        self.assertEqual(ctx.target()[0].IDENTIFIER().symbol.text, 'clean')
        self.assertEqual(len(ctx.prerequisite()), 0)
        self.assertEqual(len(ctx.orderOnlyPrerequisite()), 0)
        self.assertEqual(len(ctx.recipe().RECIPE_LINE()), 1)
        self.assertEqual(ctx.recipe().RECIPE_LINE()[0].symbol.text, '\n')
        ctx = parser.makefileRule()
        self.assertIsNone(ctx.exception)
        self.assertEqual(len(ctx.target()), 1)
        self.assertEqual(ctx.target()[0].IDENTIFIER().symbol.text, 'dist')
        self.assertEqual(len(ctx.prerequisite()), 0)
        self.assertEqual(len(ctx.orderOnlyPrerequisite()), 0)
        self.assertEqual(len(ctx.recipe().RECIPE_LINE()), 2)
        self.assertEqual(ctx.recipe().RECIPE_LINE()[0].symbol.text, '\n\t')
        self.assertEqual(ctx.recipe().RECIPE_LINE()[1].symbol.text, '\n')
        ctx = parser.makefileRule()
        self.assertIsNone(ctx.exception)
        self.assertEqual(len(ctx.target()), 3)
        self.assertEqual(ctx.target()[0].IDENTIFIER().symbol.text, 'a')
        self.assertEqual(ctx.target()[1].IDENTIFIER().symbol.text, 'b')
        self.assertEqual(ctx.target()[2].IDENTIFIER().symbol.text, 'c')
        self.assertEqual(len(ctx.prerequisite()), 0)
        self.assertEqual(len(ctx.orderOnlyPrerequisite()), 0)
        self.assertEqual(len(ctx.recipe().RECIPE_LINE()), 0)
        ctx = parser.makefileRule()
        self.assertIsNone(ctx.exception)
        self.assertEqual(len(ctx.target()), 3)
        self.assertEqual(ctx.target()[0].IDENTIFIER().symbol.text, 'a')
        self.assertEqual(ctx.target()[1].IDENTIFIER().symbol.text, 'b')
        self.assertEqual(ctx.target()[2].IDENTIFIER().symbol.text, 'c')
        self.assertEqual(len(ctx.prerequisite()), 1)
        self.assertEqual(ctx.prerequisite()[0].IDENTIFIER().symbol.text, 'd')
        self.assertEqual(len(ctx.orderOnlyPrerequisite()), 1)
        self.assertEqual(ctx.orderOnlyPrerequisite()[0].IDENTIFIER().symbol.text, 'e')
        self.assertEqual(len(ctx.recipe().RECIPE_LINE()), 0)
        ctx = parser.makefileRule()
        self.assertIsNone(ctx.exception)
        self.assertEqual(len(ctx.target()), 3)
        self.assertEqual(ctx.target()[0].IDENTIFIER().symbol.text, 'a')
        self.assertEqual(ctx.target()[1].IDENTIFIER().symbol.text, 'b')
        self.assertEqual(ctx.target()[2].IDENTIFIER().symbol.text, 'c')
        self.assertEqual(len(ctx.prerequisite()), 1)
        self.assertEqual(ctx.prerequisite()[0].IDENTIFIER().symbol.text, 'd')
        self.assertEqual(len(ctx.orderOnlyPrerequisite()), 0)
        self.assertEqual(len(ctx.recipe().RECIPE_LINE()), 1)
        self.assertEqual(ctx.recipe().RECIPE_LINE()[0].symbol.text, '# The recipe!\n')
        ctx = parser.makefileRule()
        self.assertIsNone(ctx.exception)
        self.assertEqual(len(ctx.target()), 1)
        self.assertEqual(ctx.target()[0].IDENTIFIER().symbol.text, 'a')
        self.assertEqual(len(ctx.prerequisite()), 0)
        self.assertEqual(len(ctx.orderOnlyPrerequisite()), 0)
        self.assertEqual(len(ctx.recipe().RECIPE_LINE()), 0)
        with self.assertRaises(ParseCancellationException):
            parser.makefileRule() # Because the next token is EOF
        token = lexer.nextToken()
        self.assertEqual(token.text, '<EOF>')
        self.assertEqual(token.type, Token.EOF)


