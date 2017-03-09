import sys


_sys_int_wrap_increment = sys.maxsize + sys.maxsize + 2


def _wrap_to_sys_int(value: int) -> int:
    while True:
        if 0 <= value: # Positive
            if value <= sys.maxsize: # In range
                return int(value)
            else: # Out of range
                value = value - _sys_int_wrap_increment
        else: # Negative
            if (0 - sys.maxsize - 1) <= value: # In range
                return int(value)
            else: # Out of range
                value = value + _sys_int_wrap_increment


class ValueFactorHashCodeCombiner:

    @staticmethod
    def make() -> 'ValueFactorHashCodeCombiner':
        # The constants 1009 and 9176 provide low hash collision rates
        # for common use cases.
        #
        # http://stackoverflow.com/a/34006336
        return ValueFactorHashCodeCombiner.make_with_seed_and_factor(1009, 9176)

    @staticmethod
    def make_with_seed_and_factor(seed: int, factor: int) -> 'ValueFactorHashCodeCombiner':
        instance = ValueFactorHashCodeCombiner()
        ValueFactorHashCodeCombiner._setup_with_seed_and_factor(instance, seed, factor)
        return instance

    @staticmethod
    def _setup_with_seed_and_factor(instance: 'ValueFactorHashCodeCombiner', seed: int, factor: int):
        instance._value = seed
        instance._factor = factor

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, value: int) -> None:
        self._value = value

    @property
    def factor(self) -> int:
        return self._factor

    @factor.setter
    def factor(self, value: int) -> None:
        self._factor = value

    def put(self, field: object) -> None:
        self.value = _wrap_to_sys_int((self.value * self.factor) + hash(field))


