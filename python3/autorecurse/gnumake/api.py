from autorecurse.lib.iterator import IteratorContext
from autorecurse.gnumake.implementation import Makefile, NestedMakefileLocator


class GnuMake:

    _INSTANCE = None

    @staticmethod
    def get_instance() -> 'GnuMake':
        if GnuMake._INSTANCE is None:
            GnuMake._INSTANCE = GnuMake._make()
        return GnuMake._INSTANCE

    @staticmethod
    def _make() -> 'GnuMake':
        instance = GnuMake()
        GnuMake._init_nested_makefile_locator(instance)
        return instance

    @staticmethod
    def _init_nested_makefile_locator(instance: 'GnuMake') -> None:
        locator = NestedMakefileLocator.make()
        locator.set_filename_priorities(['GNUmakefile', 'makefile', 'Makefile'])
        instance._makefile_locator = locator

    def nested_makefiles(self, directory_path: str) -> IteratorContext[Makefile]:
        return self._makefile_locator.makefile_iterator(directory_path)


