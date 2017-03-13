from autorecurse.lib.test_iterator import IteratorTests, IteratorTestWrapper
from autorecurse.lib.line import *
import unittest


class MockFile:

    @staticmethod
    def make() -> 'MockFile':
        instance = MockFile()
        MockFile._setup(instance)
        return instance

    @staticmethod
    def _setup(instance: 'MockFile') -> None:
        instance._lines = []
        instance._current_line = None
        instance._line_sep = '\r\n'

    @property
    def current_line(self) -> Line:
        return self._current_line

    def append_line(self, line: Line) -> None:
        self._lines.append(line)

    def readline(self) -> str:
        if len(self._lines) == 0:
            self._current_line = None
            return ''
        else:
            self._current_line = self._lines.pop(0)
            return ''.join([self._current_line.content, self._line_sep])


class TestLineBreakError(unittest.TestCase):

    def test_default_message(self):
        ex = LineBreakError()
        self.assertEqual(str(ex), 'String has multiple line breaks.')

    def test_custom_message(self):
        ex = LineBreakError('Custom message.')
        self.assertEqual(str(ex), 'Custom message.')


class TestLine(unittest.TestCase):

    def test_no_line_breaks(self):
        line = Line.make('Hello')
        self.assertEqual(line.content, 'Hello')

    def test_one_line_break(self):
        line = Line.make('Hello\r\n')
        self.assertEqual(line.content, 'Hello')

    def test_empty_no_line_breaks(self):
        line = Line.make('')
        self.assertEqual(line.content, '')

    def test_empty_one_line_break(self):
        line = Line.make('\r\n')
        self.assertEqual(line.content, '')

    def test_two_line_breaks(self):
        with self.assertRaises(LineBreakError):
            line = Line.make('\n\r\n')

    def test_eq_operator(self):
        line1 = Line.make('Hello')
        line2 = Line.make('Goodbye')
        line3 = Line.make('Hello')
        line4 = Exception()
        line4.content = 'Hello'
        self.assertEqual(line1, line1)
        self.assertNotEqual(line1, line2)
        self.assertEqual(line1, line3)
        self.assertNotEqual(line1, line4)


class TestFileLineIterator(unittest.TestCase):

    @staticmethod
    def make_iterator_wrapper_content() -> IteratorTestWrapper[Line]:
        file_ = MockFile.make()
        file_.append_line(Line.make('Hello'))
        file_.append_line(Line.make('Goodbye'))
        file_.append_line(Line.make(''))
        actual = FileLineIterator.make(file_)
        expected = [Line.make_with_line_number('Hello', 1), Line.make_with_line_number('Goodbye', 2), Line.make_with_line_number('', 3)]
        return IteratorTestWrapper.make(actual, expected)

    @staticmethod
    def make_iterator_wrapper_empty() -> IteratorTestWrapper[Line]:
        file_ = MockFile.make()
        actual = FileLineIterator.make(file_)
        expected = []
        return IteratorTestWrapper.make(actual, expected)

    def test_iterator_tests(self):
        IteratorTests.run_all(TestFileLineIterator.make_iterator_wrapper_content)
        IteratorTests.run_all(TestFileLineIterator.make_iterator_wrapper_empty)


class TestEmptyLineFilter(unittest.TestCase):

    def test_non_empty_line(self):
        obj = EmptyLineFilter.make()
        obj.current_item = Line.make('Hello')
        self.assertIs(obj.condition, True)
        obj.current_item = Line.make('')
        self.assertIs(obj.condition, False)

    def test_empty_line(self):
        obj = EmptyLineFilter.make()
        obj.current_item = Line.make('')
        self.assertIs(obj.condition, False)
        obj.current_item = Line.make('Hello')
        self.assertIs(obj.condition, True)


