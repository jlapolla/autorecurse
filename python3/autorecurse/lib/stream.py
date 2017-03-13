from abc import ABCMeta, abstractmethod
from typing import TypeVar, Generic


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
del T_contra


