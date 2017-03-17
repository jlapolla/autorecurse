from argparse import ArgumentError
from autorecurse.gnumake.api import *
import unittest


class TestGnuMake(unittest.TestCase):

    def test_nested_makefiles(self):
        gnu = GnuMake.get_instance()
        with gnu.nested_makefiles('test_sample/gnu/nested-makefiles') as it:
            self.assertIs(it.is_at_start, True)
            it.move_to_next()
            makefile = it.current_item
            self.assertEqual(makefile.exec_path, 'test_sample/gnu/nested-makefiles')
            self.assertEqual(makefile.file_path, 'GNUmakefile')
            it.move_to_next()
            makefile = it.current_item
            self.assertEqual(makefile.exec_path, 'test_sample/gnu/nested-makefiles/make-folder-2')
            self.assertEqual(makefile.file_path, 'makefile')
            it.move_to_next()
            makefile = it.current_item
            self.assertEqual(makefile.exec_path, 'test_sample/gnu/nested-makefiles/make-folder-1')
            self.assertEqual(makefile.file_path, 'makefile')
            it.move_to_next()
            makefile = it.current_item
            self.assertEqual(makefile.exec_path, 'test_sample/gnu/nested-makefiles/make-folder-1/subfolder')
            self.assertEqual(makefile.file_path, 'Makefile')
            it.move_to_next()
            self.assertIs(it.is_at_end, True)

    def test_execution_directory(self):
        gnu = GnuMake.get_instance()
        self.assertIs(gnu.execution_directory('-h'.split()), None)
        self.assertIs(gnu.execution_directory('-f Makefile -qp'.split()), None)
        self.assertEqual(gnu.execution_directory('-f Makefile -qp -C /etc/usr'.split()), '/etc/usr')
        self.assertEqual(gnu.execution_directory('-f Makefile -qp -C / --directory etc --directory=/usr'.split()), '/etc/usr')
        with self.assertRaises(ArgumentError):
            self.assertEqual(gnu.execution_directory('-f Makefile -qp -C'.split()), '/etc/usr')


