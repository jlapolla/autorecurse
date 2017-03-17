from argparse import ArgumentError
from autorecurse.gnumake.api import *
import unittest


class TestGnuMake(unittest.TestCase):

    def test_execution_directory(self):
        gnu = GnuMake.get_instance()
        self.assertIs(gnu.execution_directory('-h'.split()), None)
        self.assertIs(gnu.execution_directory('-f Makefile -qp'.split()), None)
        self.assertEqual(gnu.execution_directory('-f Makefile -qp -C /etc/usr'.split()), '/etc/usr')
        self.assertEqual(gnu.execution_directory('-f Makefile -qp -C / --directory etc --directory=/usr'.split()), '/etc/usr')
        with self.assertRaises(ArgumentError):
            self.assertEqual(gnu.execution_directory('-f Makefile -qp -C'.split()), '/etc/usr')


