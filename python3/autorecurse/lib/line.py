

class LineBreakError(Exception):

    def __init__(self, message: str = None) -> None:
        if message is None:
            super().__init__('String has multiple line breaks.')
        else:
            super().__init__(message)


class Line:

    @staticmethod
    def make(content: str) -> 'Line':
        instance = Line()
        Line._setup(instance, content)
        return instance

    @staticmethod
    def _setup(instance: 'Line', content: str) -> None:
        lines = content.splitlines()
        if len(lines) == 1:
            instance._content = lines[0]
        elif len(lines) == 0:
            instance._content = ''
        else:
            raise LineBreakError()
        instance._line_number = None

    @staticmethod
    def make_with_line_number(content: str, line_number: int) -> 'Line':
        instance = Line()
        Line._setup_with_line_number(instance, content, line_number)
        return instance

    @staticmethod
    def _setup_with_line_number(instance: 'Line', content: str, line_number: int) -> None:
        Line._setup(instance, content)
        instance._line_number = line_number

    @property
    def content(self) -> str:
        return self._content

    @property
    def has_line_number(self) -> bool:
        return self._line_number is not None

    @property
    def line_number(self) -> int:
        """
        ## Specification Domain

        - self.has_line_number is True
        """
        return self._line_number

    def __str__(self) -> str:
        return self.content

    def __eq__(self, other: 'Line') -> bool:
        if (other.__class__ is self.__class__) and (self.content == other.content) and (self.has_line_number is other.has_line_number):
            if self.has_line_number:
                if self.line_number == other.line_number:
                    return True
            else:
                return True
        return False

    def __hash__(self) -> int:
        if self.has_line_number:
            return hash(self.content, self.line_number)
        else:
            return hash(self.content)


