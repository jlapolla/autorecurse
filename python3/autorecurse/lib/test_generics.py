from autorecurse.lib.generics import *
from abc import ABCMeta, abstractmethod
from typing import TypeVar, Generic, Callable
import typing
import unittest


T = TypeVar('T')
class IteratorTestWrapper(unittest.TestCase, Iterator[T]):

    @staticmethod
    def make(actual: Iterator[T], expected: typing.Iterable[T]) -> 'IteratorTestWrapper':
        instance = IteratorTestWrapper()
        IteratorTestWrapper._setup(instance, actual, expected)
        return instance

    @staticmethod
    def _setup(instance: 'IteratorTestWrapper', actual: Iterator[T], expected: typing.Iterable[T]) -> None:
        instance._actual = actual
        instance._expected = list(expected)

    def assert_start_state(self) -> None:
        self.assertIs(self.has_current_item, False)
        self.assertIs(self.is_at_start, True)
        self.assertIs(self.is_at_end, False)

    def assert_intermediate_state(self) -> None:
        self.assertEqual(self.current_item, self._expected[0])
        self.assertIs(self.has_current_item, True)
        self.assertIs(self.is_at_start, False)
        self.assertIs(self.is_at_end, False)

    def assert_end_state(self) -> None:
        self.assertEqual(len(self._expected), 0)
        self.assertIs(self.has_current_item, False)
        self.assertIs(self.is_at_start, False)
        self.assertIs(self.is_at_end, True)

    @property
    def current_item(self) -> T:
        return self._actual.current_item

    @property
    def has_current_item(self) -> bool:
        return self._actual.has_current_item

    @property
    def is_at_start(self) -> bool:
        return self._actual.is_at_start

    @property
    def is_at_end(self) -> bool:
        return self._actual.is_at_end

    def move_to_next(self) -> None:
        if not self.is_at_start:
            self._expected.pop(0)
        self._actual.move_to_next()

    def move_to_end(self) -> None:
        self._expected.clear()
        self._actual.move_to_end()


class IteratorTrajectoryTest(Generic[T], metaclass=ABCMeta):

    @abstractmethod
    def run(self, iterator: IteratorTestWrapper[T]) -> None:
        pass


class IteratorTrajectoryNextTest(IteratorTrajectoryTest[T]):

    @staticmethod
    def make() -> 'IteratorTrajectoryNextTest':
        return IteratorTrajectoryNextTest()

    def run(self, iterator: IteratorTestWrapper[T]) -> None:
        iterator.assert_start_state()
        iterator.move_to_next()
        while not iterator.is_at_end:
            iterator.assert_intermediate_state()
            iterator.move_to_next()
        iterator.assert_end_state()


class IteratorTrajectoryEndTest(IteratorTrajectoryTest[T]):

    @staticmethod
    def make() -> 'IteratorTrajectoryEndTest':
        return IteratorTrajectoryEndTest()

    def run(self, iterator: IteratorTestWrapper[T]) -> None:
        iterator.assert_start_state()
        iterator.move_to_end()
        iterator.assert_end_state()
        iterator.move_to_end()
        iterator.assert_end_state()

class IteratorTrajectoryNextEndTest(IteratorTrajectoryTest[T]):

    @staticmethod
    def make() -> 'IteratorTrajectoryNextEndTest':
        return IteratorTrajectoryNextEndTest()

    def run(self, iterator: IteratorTestWrapper[T]) -> None:
        iterator.assert_start_state()
        iterator.move_to_next()
        iterator.move_to_end()
        iterator.assert_end_state()


class IteratorTests:

    @staticmethod
    def run_all(factory: Callable[..., IteratorTestWrapper]) -> None:
        IteratorTrajectoryNextTest.make().run(factory())
        IteratorTrajectoryEndTest.make().run(factory())
        IteratorTrajectoryNextEndTest.make().run(factory())

del T


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


class TestListIterator(unittest.TestCase):

    @staticmethod
    def make_iterator_wrapper_content() -> IteratorTestWrapper[Line]:
        expected = [None, 'Hello', 3, None]
        actual = ListIterator.make(expected)
        return IteratorTestWrapper.make(actual, expected)

    @staticmethod
    def make_iterator_wrapper_empty() -> IteratorTestWrapper[Line]:
        expected = []
        actual = ListIterator.make(expected)
        return IteratorTestWrapper.make(actual, expected)

    def test_iterator_tests(self):
        IteratorTests.run_all(TestListIterator.make_iterator_wrapper_content)
        IteratorTests.run_all(TestListIterator.make_iterator_wrapper_empty)


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
        expected = []
        return IteratorTestWrapper.make(actual, expected)

    @staticmethod
    def make_iterator_wrapper_empty() -> IteratorTestWrapper[Line]:
        condition = EmptyLineFilter.make()
        iterator = ListIterator.make([])
        actual = ConditionFilter.make(iterator, condition)
        expected = []
        return IteratorTestWrapper.make(actual, expected)

    def test_iterator_tests(self):
        IteratorTests.run_all(TestConditionFilter.make_iterator_wrapper_content)
        IteratorTests.run_all(TestConditionFilter.make_iterator_wrapper_content_no_padding)
        IteratorTests.run_all(TestConditionFilter.make_iterator_wrapper_content_blank)
        IteratorTests.run_all(TestConditionFilter.make_iterator_wrapper_empty)


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


