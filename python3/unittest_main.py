#!/usr/bin/env python3
import autorecurse_path
import os
import sys
import unittest


def script_dir() -> str:
    return os.path.realpath(sys.path[0])


def test_suite():
    return unittest.defaultTestLoader.discover(os.path.join(script_dir(), 'tests'))


if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())


