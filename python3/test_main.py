import unittest

def suite():
    return unittest.defaultTestLoader.discover('.')

if __name__ == '__main__':
    suite().run(unittest.TestResult())

