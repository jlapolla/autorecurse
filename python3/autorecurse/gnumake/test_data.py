from autorecurse.gnumake.data import *
from io import StringIO
import unittest


class TestDefaultTargetFormatter(unittest.TestCase):

    def test_minimal_target(self):
        target = Target.make([], [], [])
        target.path = 'somepath'
        actual = self._target_to_string(target)
        expected = 'somepath: ;\n'
        self.assertEqual(actual, expected)

    def test_prerequisites_only(self):
        target = Target.make(['prereq1', 'prereq2'], [], [])
        target.path = 'somepath'
        actual = self._target_to_string(target)
        expected = 'somepath: prereq1 prereq2 ;\n'
        self.assertEqual(actual, expected)

    def test_order_only_prerequisites_only(self):
        target = Target.make([], ['ooprereq1', 'ooprereq2'], [])
        target.path = 'somepath'
        actual = self._target_to_string(target)
        expected = 'somepath: | ooprereq1 ooprereq2 ;\n'
        self.assertEqual(actual, expected)

    def test_recipe_only(self):
        target = Target.make([], [], ['recipe1', 'recipe2'])
        target.path = 'somepath'
        actual = self._target_to_string(target)
        expected = 'somepath:\n\trecipe1\n\trecipe2\n'
        self.assertEqual(actual, expected)

    def test_maximal_target(self):
        target = Target.make(['prereq1', 'prereq2'], ['ooprereq1', 'ooprereq2'], ['recipe1', 'recipe2'])
        target.path = 'somepath'
        actual = self._target_to_string(target)
        expected = 'somepath: prereq1 prereq2 | ooprereq1 ooprereq2\n\trecipe1\n\trecipe2\n'
        self.assertEqual(actual, expected)

    def _target_to_string(self, target: Target) -> str:
        with StringIO() as strbuff:
            formatter = DefaultTargetFormatter.make()
            formatter.print(target, strbuff)
            return strbuff.getvalue()


