

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
        return instance


