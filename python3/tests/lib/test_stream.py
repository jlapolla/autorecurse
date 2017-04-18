from autorecurse.lib.stream import *
from autorecurse.lib.line import Line, EmptyLineFilter
from autorecurse.lib.iterator import ListIterator
from autorecurse.lib.test_iterator import IteratorTests, IteratorTestWrapper
from typing import List
import unittest


class TestConditionFilter(unittest.TestCase):

    @staticmethod
    def make_iterator_wrapper_content() -> IteratorTestWrapper[Line]:
        blank_line = Line.make('')
        line1 = Line.make('Hello')
        line2 = Line.make('Goodbye')
        line3 = Line.make('Goodbye again')
        condition = EmptyLineFilter.make()
        iterator = ListIterator.make([blank_line, line1, line2, blank_line, line3, blank_line])
        actual = ConditionFilter.make(iterator, condition)
        expected = [line1, line2, line3]
        return IteratorTestWrapper.make(actual, expected)

    @staticmethod
    def make_iterator_wrapper_content_no_padding() -> IteratorTestWrapper[Line]:
        blank_line = Line.make('')
        line1 = Line.make('Hello')
        line2 = Line.make('Goodbye')
        line3 = Line.make('Goodbye again')
        condition = EmptyLineFilter.make()
        iterator = ListIterator.make([line1, line2, blank_line, line3])
        actual = ConditionFilter.make(iterator, condition)
        expected = [line1, line2, line3]
        return IteratorTestWrapper.make(actual, expected)

    @staticmethod
    def make_iterator_wrapper_content_blank() -> IteratorTestWrapper[Line]:
        blank_line = Line.make('')
        condition = EmptyLineFilter.make()
        iterator = ListIterator.make([blank_line, blank_line, blank_line])
        actual = ConditionFilter.make(iterator, condition)
        expected = [] # type: List[Line]
        return IteratorTestWrapper.make(actual, expected)

    @staticmethod
    def make_iterator_wrapper_empty() -> IteratorTestWrapper[Line]:
        condition = EmptyLineFilter.make()
        iterator = ListIterator.make([]) # type: ListIterator[Line]
        actual = ConditionFilter.make(iterator, condition)
        expected = [] # type: List[Line]
        return IteratorTestWrapper.make(actual, expected)

    def test_iterator_tests(self):
        IteratorTests.run_all(TestConditionFilter.make_iterator_wrapper_content)
        IteratorTests.run_all(TestConditionFilter.make_iterator_wrapper_content_no_padding)
        IteratorTests.run_all(TestConditionFilter.make_iterator_wrapper_content_blank)
        IteratorTests.run_all(TestConditionFilter.make_iterator_wrapper_empty)


