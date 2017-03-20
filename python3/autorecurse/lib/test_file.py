from autorecurse.lib.file import *
import os
import shutil
import unittest


class TestUniqueFileCreator(unittest.TestCase):

    SUBDIR_REL = os.path.normpath('test_sample/unique_file')
    SUBDIR_ABS = os.path.realpath(os.path.join(os.getcwd(), SUBDIR_REL))

    def setUp(self):
        self.tearDown()
        os.makedirs(TestUniqueFileCreator.SUBDIR_REL)

    def tearDown(self):
        if os.path.isdir(TestUniqueFileCreator.SUBDIR_REL):
            shutil.rmtree(TestUniqueFileCreator.SUBDIR_REL)

    def test_operation(self):
        file_creator_1 = self._new_file_creator()
        file_creator_1.create_file()
        self.assertIs(os.path.isfile(file_creator_1.file_path), True)
        self.assertEqual(os.path.dirname(file_creator_1.file_path), TestUniqueFileCreator.SUBDIR_ABS)
        file_creator_2 = self._new_file_creator()
        file_creator_2.create_file()
        self.assertIs(os.path.isfile(file_creator_2.file_path), True)
        self.assertEqual(os.path.dirname(file_creator_2.file_path), TestUniqueFileCreator.SUBDIR_ABS)
        with open(file_creator_1.file_path, 'w', encoding='utf-8') as file:
            file.write('File 1\n')
        with open(file_creator_2.file_path, 'w', encoding='utf-8') as file:
            file.write('File 2\n')
        with open(file_creator_1.file_path, 'r', encoding='utf-8') as file:
            line = file.readline()
            self.assertEqual(line, 'File 1\n')
            line = file.readline()
            self.assertEqual(line, '')
        with open(file_creator_2.file_path, 'r', encoding='utf-8') as file:
            line = file.readline()
            self.assertEqual(line, 'File 2\n')
            line = file.readline()
            self.assertEqual(line, '')

    def _new_file_creator(self):
        file_creator = UniqueFileCreator.make()
        file_creator.file_name_prefix = 'test.'
        file_creator.file_name_suffix = '.txt'
        file_creator.directory = TestUniqueFileCreator.SUBDIR_REL
        return file_creator


class TestFileLifetimeManager(unittest.TestCase):

    SUBDIR_REL = os.path.normpath('test_sample/file_lifetime')
    SUBDIR_ABS = os.path.realpath(os.path.join(os.getcwd(), SUBDIR_REL))

    def setUp(self):
        self.tearDown()
        os.makedirs(TestFileLifetimeManager.SUBDIR_REL)

    def tearDown(self):
        if os.path.isdir(TestFileLifetimeManager.SUBDIR_REL):
            shutil.rmtree(TestFileLifetimeManager.SUBDIR_REL)

    def test_operation(self):
        file_creator = self._new_file_creator()
        with FileLifetimeManager.make(file_creator) as file_manager:
            self.assertIs(os.path.isfile(file_creator.file_path), True)
            self.assertEqual(os.path.dirname(file_creator.file_path), TestFileLifetimeManager.SUBDIR_ABS)
            with file_manager.open_file('w', encoding='utf-8') as file:
                file.write('File\n')
            with file_manager.open_file('r', encoding='utf-8') as file:
                line = file.readline()
                self.assertEqual(line, 'File\n')
                line = file.readline()
                self.assertEqual(line, '')
        self.assertIs(os.path.isfile(file_creator.file_path), False)

    def _new_file_creator(self):
        file_creator = UniqueFileCreator.make()
        file_creator.file_name_prefix = 'test.'
        file_creator.file_name_suffix = '.txt'
        file_creator.directory = TestFileLifetimeManager.SUBDIR_REL
        return file_creator


