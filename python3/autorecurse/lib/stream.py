from autorecurse.lib.iterator import Iterator
from abc import ABCMeta, abstractmethod
from typing import TypeVar, Generic


T = TypeVar('T')
T_contra = TypeVar('T_contra', contravariant=True)


class Condition(Generic[T_contra], metaclass=ABCMeta):
    """
    Stateful stream evaluator.

    ## Transition System Definition

    ### States

    - S = Start condition
    - Y = Condition is True
    - N = Condition is False

    ### Transition Labels

    - Recieve = Client calls current_item (setter)

    ### Transitions Grouped by Label

    - Recieve
      - S -> Y
      - S -> N
      - Y -> Y
      - Y -> N
      - N -> Y
      - N -> N

    ## Call Validity

    For each method listed, client is allowed to call the method in the
    given states.

    - current_item (setter): S Y N
    - condition (getter): Y N

    ## Call Results

    For each state listed, calling the specified method will return the
    given result.

    - Y
      - condition (getter): True
    - N
      - condition (getter): False
    """

    @abstractmethod
    def _set_current_item(self, value: T_contra) -> None:
        pass

    current_item = property(None, _set_current_item)

    @property
    @abstractmethod
    def condition(self) -> bool:
        pass

del Condition._set_current_item


class ConditionFilter(Iterator[T]):

    @staticmethod
    def make(iterator: Iterator[T], condition: Condition[T]) -> 'ConditionFilter':
        instance = ConditionFilter()
        ConditionFilter._setup(instance, iterator, condition)
        return instance

    @staticmethod
    def _setup(instance: 'ConditionFilter', iterator: Iterator[T], condition: Condition[T]) -> None:
        instance._iterator = iterator
        instance._condition = condition

    @property
    def current_item(self) -> T:
        return self._iterator.current_item

    @property
    def has_current_item(self) -> bool:
        return self._iterator.has_current_item

    @property
    def is_at_start(self) -> bool:
        return self._iterator.is_at_start

    @property
    def is_at_end(self) -> bool:
        return self._iterator.is_at_end

    def move_to_next(self) -> None:
        found_item = False
        self._iterator.move_to_next()
        while (found_item is False) and (not self.is_at_end):
            self._condition.current_item = self.current_item
            if self._condition.condition:
                found_item = True
            else:
                self._iterator.move_to_next()


del T_contra
del T


