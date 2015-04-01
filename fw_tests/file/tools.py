# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods
# pylint: disable=invalid-name
# pylint: disable=too-many-statements

import os
import re
import json
import shutil
import unittest
import tempfile

import fw.file.tools as fileTools


def _prepare_for_diff(data):
    result = json.dumps(data, indent=4, sort_keys=True)
    result = re.sub(r'time": [0-9]+\.[0-9]+,', 'time": xxxxx.xxxxx,',
        result)
    with open('/tmp/foo.txt', 'w+') as f:
        f.write(result)
    return result


class TestFileTools1(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._testPath = os.sep.join([tempfile.gettempdir(), 'tests'])
        cls._fileToolsPath = os.sep.join([cls._testPath, 'file_tools'])

    def test_1_join_path(self):
        # Strings.
        path = fileTools.join_path()
        self.assertEqual(path, '')
        path = fileTools.join_path('')
        self.assertEqual(path, '')
        path = fileTools.join_path('', '')
        self.assertEqual(path, '/')
        path = fileTools.join_path('foo')
        self.assertEqual(path, 'foo')
        path = fileTools.join_path('foo', 'bar')
        self.assertEqual(path, 'foo/bar')
        path = fileTools.join_path('foo', 'bar', 'file.txt')
        self.assertEqual(path, 'foo/bar/file.txt')

        # Lists and strings.
        path = fileTools.join_path([])
        self.assertEqual(path, '')
        path = fileTools.join_path(['foo'])
        self.assertEqual(path, 'foo')
        path = fileTools.join_path(['foo', 'bar'])
        self.assertEqual(path, 'foo/bar')
        path = fileTools.join_path(['foo', 'bar', 'file.txt'])
        self.assertEqual(path, 'foo/bar/file.txt')
        path = fileTools.join_path(['foo'], ['bar'], ['file.txt'])
        self.assertEqual(path, 'foo/bar/file.txt')
        path = fileTools.join_path(['foo', 'bar'], ['file.txt'])
        self.assertEqual(path, 'foo/bar/file.txt')
        path = fileTools.join_path(['foo'], ['bar', 'file.txt'])
        self.assertEqual(path, 'foo/bar/file.txt')
        path = fileTools.join_path('foo', ['bar', 'file.txt'])
        self.assertEqual(path, 'foo/bar/file.txt')
        path = fileTools.join_path(['foo', 'bar'], 'file.txt')
        self.assertEqual(path, 'foo/bar/file.txt')

        # Tuples and strings.
        path = fileTools.join_path(())
        self.assertEqual(path, '')
        path = fileTools.join_path(('foo'))
        self.assertEqual(path, 'foo')
        path = fileTools.join_path(('foo', 'bar'))
        self.assertEqual(path, 'foo/bar')
        path = fileTools.join_path(('foo', 'bar', 'file.txt'))
        self.assertEqual(path, 'foo/bar/file.txt')
        path = fileTools.join_path(('foo'), ('bar'), ('file.txt'))
        self.assertEqual(path, 'foo/bar/file.txt')
        path = fileTools.join_path(('foo', 'bar'), ('file.txt'))
        self.assertEqual(path, 'foo/bar/file.txt')
        path = fileTools.join_path(('foo'), ('bar', 'file.txt'))
        self.assertEqual(path, 'foo/bar/file.txt')
        path = fileTools.join_path('foo', ('bar', 'file.txt'))
        self.assertEqual(path, 'foo/bar/file.txt')
        path = fileTools.join_path(('foo', 'bar'), 'file.txt')
        self.assertEqual(path, 'foo/bar/file.txt')

        # List, tuple and string.
        path = fileTools.join_path(['foo'], ('bar'), 'file.txt')
        self.assertEqual(path, 'foo/bar/file.txt')

        # Exceptions, illegal types.
        self.assertRaises(TypeError, fileTools.join_path, 'foo', 123)
        self.assertRaises(TypeError, fileTools.join_path, ['foo', 123])

    def test_2_verify_dir(self):
        testPath = fileTools.join_path(self._fileToolsPath, 'verify_dir')
        # Check non-existing path.
        result = fileTools.verify_dir(testPath)
        self.assertEqual(result, False)
        # Create path.
        result = fileTools.verify_dir(testPath, createifnotexists=True)
        self.assertEqual(result, True)
        # Check existing path.
        result = fileTools.verify_dir(testPath)
        self.assertEqual(result, True)

        # Exception, illegal type.
        self.assertRaises(TypeError, fileTools.verify_dir, 0)

        # Remove created directory.
        if os.path.isdir(testPath):
            shutil.rmtree(testPath)

    def test_3_verify_file(self):
        testPath = fileTools.join_path(self._fileToolsPath, 'verify_file')
        testFile = fileTools.join_path(testPath, 'file.txt')
        # Check non-existing path.
        result = fileTools.verify_file(testFile)
        self.assertEqual(result, False)
        # Create path.
        result = fileTools.verify_file(testFile, createifnotexists=True)
        self.assertEqual(result, True)
        # Check existing path.
        result = fileTools.verify_file(testFile)
        self.assertEqual(result, True)

        # Exception, illegal type.
        self.assertRaises(TypeError, fileTools.verify_file, 0)

        # Remove created directory.
        if os.path.isdir(testPath):
            shutil.rmtree(testPath)

    @classmethod
    def tearDownClass(cls):
        if os.path.isdir(cls._fileToolsPath):
            shutil.rmtree(cls._fileToolsPath)


class TestFileTools2(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._testPath = os.sep.join([tempfile.gettempdir(), 'tests'])
        cls._fileToolsPath = os.sep.join([cls._testPath, 'file_tools'])
        # Build all paths.
        cls._testPathL1 = fileTools.join_path(cls._fileToolsPath,
            'dir_content')
        cls._testPathRW = fileTools.join_path(cls._fileToolsPath,
            'read_write')
        cls._testFile1 = fileTools.join_path(cls._testPathL1, 'file1.txt')
        cls._testFile2 = fileTools.join_path(cls._testPathL1, '.file2')
        cls._testPathL2Empty = fileTools.join_path(cls._testPathL1,
            'level2empty')
        cls._testPathL2 = fileTools.join_path(cls._testPathL1, 'level2')
        cls._testFile3 = fileTools.join_path(cls._testPathL2, 'file3.txt')
        cls._testFile4 = fileTools.join_path(cls._testPathL2, 'file4.txt')
        cls._testPathL3 = fileTools.join_path(cls._testPathL2, '.level3')
        cls._testFile5 = fileTools.join_path(cls._testPathL3, 'file5.txt')
        cls._testFile6 = fileTools.join_path(cls._testPathL3, 'file6.txt')
        # Create files and paths.
        fileTools.verify_file(cls._testFile1, createifnotexists=True)
        fileTools.verify_file(cls._testFile2, createifnotexists=True)
        fileTools.verify_file(cls._testFile3, createifnotexists=True)
        fileTools.verify_file(cls._testFile4, createifnotexists=True)
        fileTools.verify_file(cls._testFile5, createifnotexists=True)
        fileTools.verify_file(cls._testFile6, createifnotexists=True)
        fileTools.verify_dir(cls._testPathL2Empty, createifnotexists=True)

    def test_1_dir_content(self):
        self.maxDiff = None
        result = fileTools.dir_content(self._testPathL1)
        result = _prepare_for_diff(result)
        self.assertEqual(result, """[
    {
        "ctime": xxxxx.xxxxx,
        "mtime": xxxxx.xxxxx,
        "name": "level2",
        "path": "level2",
        "size": 4096,
        "type": "dir"
    },
    {
        "ctime": xxxxx.xxxxx,
        "mtime": xxxxx.xxxxx,
        "name": "level2empty",
        "path": "level2empty",
        "size": 4096,
        "type": "dir"
    },
    {
        "ctime": xxxxx.xxxxx,
        "mtime": xxxxx.xxxxx,
        "name": ".file2",
        "path": ".file2",
        "size": 0,
        "type": "file"
    },
    {
        "ctime": xxxxx.xxxxx,
        "mtime": xxxxx.xxxxx,
        "name": "file1.txt",
        "path": "file1.txt",
        "size": 0,
        "type": "file"
    }
]""")

    def test_2_dir_content(self):
        result = fileTools.dir_content(self._testPathL1, files_only=True)
        result = _prepare_for_diff(result)
        self.assertEqual(result, """[
    {
        "ctime": xxxxx.xxxxx,
        "mtime": xxxxx.xxxxx,
        "name": ".file2",
        "path": ".file2",
        "size": 0,
        "type": "file"
    },
    {
        "ctime": xxxxx.xxxxx,
        "mtime": xxxxx.xxxxx,
        "name": "file1.txt",
        "path": "file1.txt",
        "size": 0,
        "type": "file"
    }
]""")

    def test_3_dir_content(self):
        result = fileTools.dir_content(self._testPathL1, dirs_only=True)
        result = _prepare_for_diff(result)
        self.assertEqual(result, """[
    {
        "ctime": xxxxx.xxxxx,
        "mtime": xxxxx.xxxxx,
        "name": "level2",
        "path": "level2",
        "size": 4096,
        "type": "dir"
    },
    {
        "ctime": xxxxx.xxxxx,
        "mtime": xxxxx.xxxxx,
        "name": "level2empty",
        "path": "level2empty",
        "size": 4096,
        "type": "dir"
    }
]""")

    def test_4_dir_content(self):
        result = fileTools.dir_content(self._testPathL1, recursive=True)
        result = _prepare_for_diff(result)
        self.assertEqual(result, """[
    {
        "content": [
            {
                "content": [
                    {
                        "ctime": xxxxx.xxxxx,
                        "mtime": xxxxx.xxxxx,
                        "name": "file5.txt",
                        "path": "level2/.level3/file5.txt",
                        "size": 0,
                        "type": "file"
                    },
                    {
                        "ctime": xxxxx.xxxxx,
                        "mtime": xxxxx.xxxxx,
                        "name": "file6.txt",
                        "path": "level2/.level3/file6.txt",
                        "size": 0,
                        "type": "file"
                    }
                ],
                "ctime": xxxxx.xxxxx,
                "mtime": xxxxx.xxxxx,
                "name": ".level3",
                "path": "level2/.level3",
                "size": 4096,
                "type": "dir"
            },
            {
                "ctime": xxxxx.xxxxx,
                "mtime": xxxxx.xxxxx,
                "name": "file3.txt",
                "path": "level2/file3.txt",
                "size": 0,
                "type": "file"
            },
            {
                "ctime": xxxxx.xxxxx,
                "mtime": xxxxx.xxxxx,
                "name": "file4.txt",
                "path": "level2/file4.txt",
                "size": 0,
                "type": "file"
            }
        ],
        "ctime": xxxxx.xxxxx,
        "mtime": xxxxx.xxxxx,
        "name": "level2",
        "path": "level2",
        "size": 4096,
        "type": "dir"
    },
    {
        "content": [],
        "ctime": xxxxx.xxxxx,
        "mtime": xxxxx.xxxxx,
        "name": "level2empty",
        "path": "level2empty",
        "size": 4096,
        "type": "dir"
    },
    {
        "ctime": xxxxx.xxxxx,
        "mtime": xxxxx.xxxxx,
        "name": ".file2",
        "path": ".file2",
        "size": 0,
        "type": "file"
    },
    {
        "ctime": xxxxx.xxxxx,
        "mtime": xxxxx.xxxxx,
        "name": "file1.txt",
        "path": "file1.txt",
        "size": 0,
        "type": "file"
    }
]""")

    def test_5_dir_content(self):
        result = fileTools.dir_content(self._testPathL1, recursive=True,
            dirs_only=True)
        result = _prepare_for_diff(result)
        self.assertEqual(result, """[
    {
        "content": [
            {
                "content": [],
                "ctime": xxxxx.xxxxx,
                "mtime": xxxxx.xxxxx,
                "name": ".level3",
                "path": "level2/.level3",
                "size": 4096,
                "type": "dir"
            }
        ],
        "ctime": xxxxx.xxxxx,
        "mtime": xxxxx.xxxxx,
        "name": "level2",
        "path": "level2",
        "size": 4096,
        "type": "dir"
    },
    {
        "content": [],
        "ctime": xxxxx.xxxxx,
        "mtime": xxxxx.xxxxx,
        "name": "level2empty",
        "path": "level2empty",
        "size": 4096,
        "type": "dir"
    }
]""")

    def test_6_dir_content(self):
        # Exception, illegal combination of parameters, recursive & filesOnly.
        self.assertRaises(AttributeError, fileTools.dir_content,
            self._testPathL1, recursive=True, files_only=True)
        # Filter out '.*' items.
        result = fileTools.dir_content(self._testPathL1, recursive=True,
            filter_out=r'\.[.]*')
        result = _prepare_for_diff(result)
        self.assertEqual(result, """[
    {
        "content": [
            {
                "ctime": xxxxx.xxxxx,
                "mtime": xxxxx.xxxxx,
                "name": "file3.txt",
                "path": "level2/file3.txt",
                "size": 0,
                "type": "file"
            },
            {
                "ctime": xxxxx.xxxxx,
                "mtime": xxxxx.xxxxx,
                "name": "file4.txt",
                "path": "level2/file4.txt",
                "size": 0,
                "type": "file"
            }
        ],
        "ctime": xxxxx.xxxxx,
        "mtime": xxxxx.xxxxx,
        "name": "level2",
        "path": "level2",
        "size": 4096,
        "type": "dir"
    },
    {
        "content": [],
        "ctime": xxxxx.xxxxx,
        "mtime": xxxxx.xxxxx,
        "name": "level2empty",
        "path": "level2empty",
        "size": 4096,
        "type": "dir"
    },
    {
        "ctime": xxxxx.xxxxx,
        "mtime": xxxxx.xxxxx,
        "name": "file1.txt",
        "path": "file1.txt",
        "size": 0,
        "type": "file"
    }
]""")

    def test_7_dir_content(self):
        # Filter out '*.txt' items.
        result = fileTools.dir_content(self._testPathL1, recursive=True,
            filter_out=r'(.)+\.txt')
        result = _prepare_for_diff(result)
        self.assertEqual(result, """[
    {
        "content": [
            {
                "content": [],
                "ctime": xxxxx.xxxxx,
                "mtime": xxxxx.xxxxx,
                "name": ".level3",
                "path": "level2/.level3",
                "size": 4096,
                "type": "dir"
            }
        ],
        "ctime": xxxxx.xxxxx,
        "mtime": xxxxx.xxxxx,
        "name": "level2",
        "path": "level2",
        "size": 4096,
        "type": "dir"
    },
    {
        "content": [],
        "ctime": xxxxx.xxxxx,
        "mtime": xxxxx.xxxxx,
        "name": "level2empty",
        "path": "level2empty",
        "size": 4096,
        "type": "dir"
    },
    {
        "ctime": xxxxx.xxxxx,
        "mtime": xxxxx.xxxxx,
        "name": ".file2",
        "path": ".file2",
        "size": 0,
        "type": "file"
    }
]""")

    @classmethod
    def tearDownClass(cls):
        if os.path.isdir(cls._fileToolsPath):
            shutil.rmtree(cls._fileToolsPath)


if __name__ == '__main__':
    unittest.main()
