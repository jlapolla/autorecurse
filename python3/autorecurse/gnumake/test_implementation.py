from autorecurse.gnumake.implementation import *
from antlr4 import CommonTokenStream, InputStream
import unittest
import os


class TestTarget(unittest.TestCase):

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

        ctx = parser.makefileRule()
        self.assertIsNone(ctx.exception)
        target = ParseContextTargetBuilder.get_instance().build_target(ctx, 0)
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
        it = target.recipe_lines
        it.move_to_next()
        self.assertEqual(it.current_item, '  Hurray:|;#\t it works\\quite\\well\\')
        it.move_to_next()
        self.assertEqual(it.current_item, '  And this is still recipe text \\')
        it.move_to_next()
        self.assertEqual(it.current_item, 'And this tab is removed # Not a comment!')
        it.move_to_next()
        self.assertEqual(it.current_item, '  More recipe (trailing spaces)  ')
        it.move_to_next()
        self.assertIs(it.is_at_end, True)

        ctx = parser.makefileRule()
        self.assertIsNone(ctx.exception)
        target = ParseContextTargetBuilder.get_instance().build_target(ctx, 0)
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
        it = target.recipe_lines
        it.move_to_next()
        self.assertEqual(it.current_item, '|:recipes!!;; # Oh\tboy!')
        it.move_to_next()
        self.assertEqual(it.current_item, ' :#I can\'t wait...')
        it.move_to_next()
        self.assertEqual(it.current_item, ' ...until this recipe is over!')
        it.move_to_next()
        self.assertEqual(it.current_item, '')
        it.move_to_next()
        self.assertIs(it.is_at_end, True)

        ctx = parser.makefileRule()
        self.assertIsNone(ctx.exception)
        target = ParseContextTargetBuilder.get_instance().build_target(ctx, 0)
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
        target = ParseContextTargetBuilder.get_instance().build_target(ctx, 1)
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
        target = ParseContextTargetBuilder.get_instance().build_target(ctx, 2)
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
        it = target.recipe_lines
        it.move_to_next()
        self.assertIs(it.is_at_end, True)


class TestTargetListingTargetReader(unittest.TestCase):

    def test_target_iterator(self):
        target_reader = TargetListingTargetReader.make('make')
        makefile = Makefile.make('test_sample/gnu/project/Makefile')
        with target_reader.target_iterator(makefile) as target_iterator:
            self.assertIs(target_iterator.is_at_start, True)

            target_iterator.move_to_next()
            target = target_iterator.current_item
            self.assertEqual(target.path, 'objdir/bar.o')
            it = target.prerequisites
            it.move_to_next()
            self.assertEqual(it.current_item, 'src/bar.c')
            it.move_to_next()
            self.assertIs(it.is_at_end, True)
            it = target.order_only_prerequisites
            it.move_to_next()
            self.assertEqual(it.current_item, 'objdir')
            it.move_to_next()
            self.assertIs(it.is_at_end, True)
            self.assertIs(target.file, makefile)
            it = target.recipe_lines
            it.move_to_next()
            self.assertEqual(it.current_item, 'touch $@')
            it.move_to_next()
            self.assertIs(it.is_at_end, True)

            target_iterator.move_to_next()
            target = target_iterator.current_item
            self.assertEqual(target.path, 'all')
            it = target.prerequisites
            it.move_to_next()
            self.assertEqual(it.current_item, 'objdir/foo.o')
            it.move_to_next()
            self.assertEqual(it.current_item, 'objdir/bar.o')
            it.move_to_next()
            self.assertEqual(it.current_item, 'objdir/baz.o')
            it.move_to_next()
            self.assertIs(it.is_at_end, True)
            it = target.order_only_prerequisites
            it.move_to_next()
            self.assertIs(it.is_at_end, True)
            self.assertIs(target.file, makefile)
            it = target.recipe_lines
            it.move_to_next()
            self.assertIs(it.is_at_end, True)

            target_iterator.move_to_next()
            target = target_iterator.current_item
            self.assertEqual(target.path, 'objdir/foo.o')
            it = target.prerequisites
            it.move_to_next()
            self.assertEqual(it.current_item, 'src/foo.c')
            it.move_to_next()
            self.assertIs(it.is_at_end, True)
            it = target.order_only_prerequisites
            it.move_to_next()
            self.assertEqual(it.current_item, 'objdir')
            it.move_to_next()
            self.assertIs(it.is_at_end, True)
            self.assertIs(target.file, makefile)
            it = target.recipe_lines
            it.move_to_next()
            self.assertEqual(it.current_item, 'touch $@')
            it.move_to_next()
            self.assertIs(it.is_at_end, True)

            target_iterator.move_to_next()
            target = target_iterator.current_item
            self.assertEqual(target.path, 'objdir/baz.o')
            it = target.prerequisites
            it.move_to_next()
            self.assertEqual(it.current_item, 'src/baz.c')
            it.move_to_next()
            self.assertIs(it.is_at_end, True)
            it = target.order_only_prerequisites
            it.move_to_next()
            self.assertEqual(it.current_item, 'objdir')
            it.move_to_next()
            self.assertIs(it.is_at_end, True)
            self.assertIs(target.file, makefile)
            it = target.recipe_lines
            it.move_to_next()
            self.assertEqual(it.current_item, 'touch $@')
            it.move_to_next()
            self.assertIs(it.is_at_end, True)

            target_iterator.move_to_next()
            target = target_iterator.current_item
            self.assertEqual(target.path, 'objdir')
            it = target.prerequisites
            it.move_to_next()
            self.assertIs(it.is_at_end, True)
            it = target.order_only_prerequisites
            it.move_to_next()
            self.assertIs(it.is_at_end, True)
            self.assertIs(target.file, makefile)
            it = target.recipe_lines
            it.move_to_next()
            self.assertEqual(it.current_item, 'mkdir $(OBJDIR)')
            it.move_to_next()
            self.assertIs(it.is_at_end, True)

            target_iterator.move_to_next()
            self.assertIs(target_iterator.is_at_end, True)


class TestNestedMakefileLocator(unittest.TestCase):

    CWD = os.path.realpath(os.getcwd())

    def test_with_results(self):
        locator = NestedMakefileLocator.make()
        locator.set_filename_priorities(['GNUmakefile', 'makefile', 'Makefile'])
        with locator.makefile_iterator('test_sample/gnu/nested-makefiles') as it:
            self.assertIs(it.is_at_start, True)
            it.move_to_next()
            makefile = it.current_item
            self.assertEqual(makefile.exec_path, os.path.join(TestNestedMakefileLocator.CWD, 'test_sample/gnu/nested-makefiles'))
            self.assertEqual(makefile.file_path, 'GNUmakefile')
            it.move_to_next()
            makefile = it.current_item
            self.assertEqual(makefile.exec_path, os.path.join(TestNestedMakefileLocator.CWD, 'test_sample/gnu/nested-makefiles/make-folder-2'))
            self.assertEqual(makefile.file_path, 'makefile')
            it.move_to_next()
            makefile = it.current_item
            self.assertEqual(makefile.exec_path, os.path.join(TestNestedMakefileLocator.CWD, 'test_sample/gnu/nested-makefiles/make-folder-1'))
            self.assertEqual(makefile.file_path, 'makefile')
            it.move_to_next()
            makefile = it.current_item
            self.assertEqual(makefile.exec_path, os.path.join(TestNestedMakefileLocator.CWD, 'test_sample/gnu/nested-makefiles/make-folder-1/subfolder'))
            self.assertEqual(makefile.file_path, 'Makefile')
            it.move_to_next()
            self.assertIs(it.is_at_end, True)

    def test_without_results(self):
        locator = NestedMakefileLocator.make()
        with locator.makefile_iterator('test_sample/gnu/nested-makefiles') as it:
            self.assertIs(it.is_at_start, True)
            it.move_to_next()
            self.assertIs(it.is_at_end, True)


