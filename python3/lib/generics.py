from abc import ABCMeta, abstractmethod
from typing import TypeVar, Generic


T_co = TypeVar('T_co', covariant=True)
class Iterator(Generic[T_co], metaclass=ABCMeta):

    @property
    @abstractmethod
    def current_item(self) -> T_co:
        pass

    @property
    @abstractmethod
    def has_current_item(self) -> bool:
        pass

    @property
    @abstractmethod
    def is_at_start(self) -> bool:
        pass

    @property
    @abstractmethod
    def is_at_start(self) -> bool:
        pass

    @abstractmethod
    def move_to_next(self) -> None:
        pass

    @abstractmethod
    def move_to_end(self) -> None:
        pass
del T_co


