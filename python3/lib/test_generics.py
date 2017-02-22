from lib.generics import *
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


class TestFileLineIterator(unittest.TestCase):

    @staticmethod
    def make_file_content() -> MockFile:
        src = MockFile.make()
        src.append_line(Line.make("Hello"))
        src.append_line(Line.make("Goodbye"))
        src.append_line(Line.make(""))
        return src

    @staticmethod
    def make_file_empty() -> MockFile:
        return MockFile.make()

    def test_file_content(self):
        src = TestFileLineIterator.make_file_content()
        self.verify_trajectory_1(FileLineIterator.make(src), src)
        src = TestFileLineIterator.make_file_content()
        self.verify_trajectory_2(FileLineIterator.make(src), src)

    def test_file_empty(self):
        src = TestFileLineIterator.make_file_empty()
        self.verify_trajectory_1(FileLineIterator.make(src), src)
        src = TestFileLineIterator.make_file_empty()
        self.verify_trajectory_2(FileLineIterator.make(src), src)

    def verify_trajectory_1(self, obj: FileLineIterator, src: MockFile) -> None:
        self.verify_start_state(obj, src)
        obj.move_to_next()
        while not obj.is_at_end:
            self.verify_intermediate_state(obj, src)
            obj.move_to_next()
        self.verify_end_state(obj, src)

    def verify_trajectory_2(self, obj: FileLineIterator, src: MockFile) -> None:
        self.verify_start_state(obj, src)
        obj.move_to_end()
        self.verify_end_state(obj, src)
        obj.move_to_end()
        self.verify_end_state(obj, src)

    def verify_start_state(self, obj: FileLineIterator, src: MockFile) -> None:
        self.assertIs(obj.has_current_item, False)
        self.assertIs(obj.is_at_start, True)
        self.assertIs(obj.is_at_end, False)

    def verify_intermediate_state(self, obj: FileLineIterator, src: MockFile) -> None:
        self.assertEqual(obj.current_item, src.current_line)
        self.assertIs(obj.has_current_item, True)
        self.assertIs(obj.is_at_start, False)
        self.assertIs(obj.is_at_end, False)

    def verify_end_state(self, obj: FileLineIterator, src: MockFile) -> None:
        self.assertIsNone(src.current_line)
        self.assertIs(obj.has_current_item, False)
        self.assertIs(obj.is_at_start, False)
        self.assertIs(obj.is_at_end, True)


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


