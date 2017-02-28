from lib.generics import ListIterator, Iterator
from app.antlr.parsemakefilerule import MakefileRuleParser


class Makefile:

    @staticmethod
    def make(path: str, exec_path: str) -> 'Makefile':
        instance = Makefile()
        Makefile._setup(instance, path, exec_path)
        return instance

    @staticmethod
    def _setup(instance: 'Makefile', path: str, exec_path: str) -> None:
        instance._path = path
        instance._exec_path = exec_path

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, value: str) -> None:
        self._path = value

    @property
    def exec_path(self) -> str:
        return self._exec_path

    @exec_path.setter
    def exec_path(self, value: str) -> None:
        self._exec_path = value


class MakefileTarget:

    @staticmethod
    def make_from_parse_context(context: MakefileRuleParser.MakefileRuleContext, target_index: int) -> 'MakefileTarget':
        instance = MakefileTarget()
        MakefileTarget._setup_from_parse_context(instance, context, target_index)
        return instance

    @staticmethod
    def _setup_from_parse_context(instance: 'MakefileTarget', context: MakefileRuleParser.MakefileRuleContext, target_index: int) -> None:
        instance._file = None
        instance._path = context.target(target_index).IDENTIFIER().symbol.text
        instance._prerequisites = []
        for prerequisite in context.prerequisite():
            instance._prerequisites.append(prerequisite.IDENTIFIER().symbol.text)
        instance._order_only_prerequisites = []
        for order_only_prerequisite in context.orderOnlyPrerequisite():
            instance._order_only_prerequisites.append(order_only_prerequisite.IDENTIFIER().symbol.text)

    @property
    def file(self) -> Makefile:
        return self._file

    @file.setter
    def file(self, value: Makefile) -> None:
        self._file = value

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, value: str) -> None:
        self._path = value

    @property
    def prerequisites(self) -> Iterator[str]:
        return ListIterator.make(self._prerequisites)

    @property
    def order_only_prerequisites(self) -> Iterator[str]:
        return ListIterator.make(self._order_only_prerequisites)


