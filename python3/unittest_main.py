import os
import sys
import unittest


def script_dir() -> str:
    return os.path.realpath(sys.path[0])


def autorecurse_path() -> str:
    return os.path.join(script_dir(), 'src')


def suite():
    return unittest.defaultTestLoader.discover(script_dir())


if __name__ == '__main__':
    if autorecurse_path() not in sys.path:
        sys.path.append(autorecurse_path())
    unittest.TextTestRunner().run(suite())


