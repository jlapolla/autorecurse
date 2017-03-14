from autorecurse.lib.iterator import *
from abc import ABCMeta, abstractmethod
from typing import Callable, Generic, Iterable, TypeVar
import unittest


T = TypeVar('T')


class IteratorTestWrapper(unittest.TestCase, Iterator[T]):

    @staticmethod
    def make(actual: Iterator[T], expected: Iterable[T]) -> 'IteratorTestWrapper':
        instance = IteratorTestWrapper()
        IteratorTestWrapper._setup(instance, actual, expected)
        return instance

    @staticmethod
    def _setup(instance: 'IteratorTestWrapper', actual: Iterator[T], expected: Iterable[T]) -> None:
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


class TestListIterator(unittest.TestCase):

    @staticmethod
    def make_iterator_wrapper_content() -> IteratorTestWrapper[object]:
        expected = [None, 'Hello', 3, None]
        actual = ListIterator.make(expected)
        return IteratorTestWrapper.make(actual, expected)

    @staticmethod
    def make_iterator_wrapper_empty() -> IteratorTestWrapper[object]:
        expected = []
        actual = ListIterator.make(expected)
        return IteratorTestWrapper.make(actual, expected)

    def test_iterator_tests(self):
        IteratorTests.run_all(TestListIterator.make_iterator_wrapper_content)
        IteratorTests.run_all(TestListIterator.make_iterator_wrapper_empty)


del T


