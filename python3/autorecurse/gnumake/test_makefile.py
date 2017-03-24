from autorecurse.gnumake.makefile import *
import unittest


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


