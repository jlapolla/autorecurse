import os
import sys


"""
Add local autorecurse directory to sys.path to allow access to
autorecurse packages.
"""


def script_dir() -> str:
    return os.path.realpath(sys.path[0])


def autorecurse_path() -> str:
    return os.path.join(script_dir(), 'src')


if autorecurse_path() not in sys.path:
    sys.path.append(autorecurse_path())


