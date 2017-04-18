from autorecurse.gnumake.grammar.filter import *
import unittest


class TestFileSectionFilter(unittest.TestCase):

    def test_content(self):
        obj = FileSectionFilter.make()
        obj.current_item = Line.make('Hello')
        self.assertIs(obj.condition, False)
        obj.current_item = Line.make('# Files')
        self.assertIs(obj.condition, False)
        obj.current_item = Line.make('Hello')
        self.assertIs(obj.condition, True)
        obj.current_item = Line.make('Goodbye')
        self.assertIs(obj.condition, True)
        obj.current_item = Line.make('# files hash-table stats:')
        self.assertIs(obj.condition, False)
        obj.current_item = Line.make('Hello')
        self.assertIs(obj.condition, False)
        obj.current_item = Line.make('Hello')
        self.assertIs(obj.condition, False)
        obj.current_item = Line.make('# Files')
        self.assertIs(obj.condition, False)
        obj.current_item = Line.make('Hello')
        self.assertIs(obj.condition, False)
        obj.current_item = Line.make('Goodbye')
        self.assertIs(obj.condition, False)
        obj.current_item = Line.make('# files hash-table stats:')
        self.assertIs(obj.condition, False)
        obj.current_item = Line.make('Hello')
        self.assertIs(obj.condition, False)


