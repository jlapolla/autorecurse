import os
import sys


"""
Add autorecurse directory to sys.path to allow access to autorecurse
packages.
"""


def autorecurse_path() -> str:
    root_build_util = os.path.realpath(sys.path[0])
    root = os.path.dirname(os.path.dirname(root_build_util))
    return os.path.join(root, 'python3')


if autorecurse_path() not in sys.path:
    sys.path.append(autorecurse_path())


