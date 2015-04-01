# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods
# pylint: disable=invalid-name
# pylint: disable=too-many-statements

import os
import shutil
import unittest
import tempfile

import fw.config
import fw.file.tree as fileTree
import fw.file.tools as fileTools
import fw.config.manage as configManage


class TestFileTree(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._empty = {
            "@api": {
                "type": "jconf",
                "name": "FileTree",
                "prev_version": None,
                "version": "1.0.0"
            },
            "root_path": "-WILL BE REPLACED-",
            "visible_name": "Empty Tree",
            "tree_id": "abcdef1234567890abcdef1234567890a"
        }

        cls._foldersOnly = {
            "@api": {
                "type": "jconf",
                "name": "FileTree",
                "prev_version": None,
                "version": "1.0.0"
            },
            "root_path": "-WILL BE REPLACED-",
            "visible_name": "Folders Only Tree",
            "tree_id": "abcdef1234567890abcdef1234567890b",
            "content": [
                {
                    "name": "level1a",
                    "type": "dir",
                    "content": [
                        {
                            "name": "level2a",
                            "type": "dir"
                        },
                        {
                            "name": "level2b",
                            "type": "dir"
                        }
                    ]
                },
                {
                    "name": "level1b",
                    "type": "dir",
                    "content": [
                        {
                            "name": "level2c",
                            "type": "dir",
                            "content": [
                                {
                                    "name": "level3a",
                                    "type": "dir"
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        cls._emptyFiles = {
            "@api": {
                "type": "jconf",
                "name": "FileTree",
                "prev_version": None,
                "version": "1.0.0"
            },
            "root_path": "-WILL BE REPLACED-",
            "visible_name": "Files Tree",
            "tree_id": "abcdef1234567890abcdef1234567890c",
            "content": [
                {
                    "name": "level1a",
                    "type": "dir",
                    "content": [
                        {
                            "name": "config.cfg",
                            "type": "file"
                        },
                        {
                            "name": "some text.txt",
                            "type": "file"
                        }
                    ]
                },
                {
                    "name": "static.html",
                    "type": "file"
                }
            ]
        }
        cls._testPath = os.sep.join([tempfile.gettempdir(), 'tests'])
        cls._fileTreePath = os.sep.join([cls._testPath, 'file_tree'])
        configManage.register_config_package(fw.config)
        cls._empty['root_path'] = cls._fileTreePath
        result = configManage.validate_config(cls._empty)
        if result['status'] == 'error':
            raise result['errors'][0]
        cls._foldersOnly['root_path'] = cls._fileTreePath
        result = configManage.validate_config(cls._foldersOnly)
        if result['status'] == 'error':
            raise result['errors'][0]
        cls._emptyFiles['root_path'] = cls._fileTreePath
        result = configManage.validate_config(cls._emptyFiles)
        if result['status'] == 'error':
            raise result['errors'][0]

    def test_1_create_tree(self):
        result = fileTree.create_tree(self._empty)
        self.assertEqual(result['status'], 'ok')
        path = self._empty['path']
        # Fetch folder content for verification.
        result = fileTools.dir_content(path, recursive=True)
        self.assertEqual(result, [])

    def test_2_create_tree(self):
        result = fileTree.create_tree(self._foldersOnly)
        self.assertEqual(result['status'], 'ok')
        path = self._foldersOnly['path']
        # Fetch folder content for verification.
        result = fileTools.dir_content(path, recursive=True)
        self.assertEqual(result[0]['path'], 'level1a')
        self.assertEqual(result[0]['content'][0]['path'], 'level1a/level2a')
        self.assertEqual(result[0]['content'][1]['path'], 'level1a/level2b')
        self.assertEqual(result[1]['path'], 'level1b')
        self.assertEqual(result[1]['content'][0]['path'], 'level1b/level2c')

    def test_3_create_tree(self):
        result = fileTree.create_tree(self._emptyFiles)
        self.assertEqual(result['status'], 'ok')
        path = self._emptyFiles['path']
        # Fetch folder content for verification.
        result = fileTools.dir_content(path, recursive=True)
        self.assertEqual(result[0]['path'], 'level1a')
        self.assertEqual(result[0]['content'][0]['path'], 'level1a/config.cfg')
        self.assertEqual(result[0]['content'][1]['path'],
            'level1a/some text.txt')
        self.assertEqual(result[1]['path'], 'static.html')

    def test_4_move_tree(self):
        oldTreePath = self._emptyFiles['path']
        fileTreePath2 = os.sep.join([self._testPath, 'file_tree2'])
        fileTree.move_tree(self._emptyFiles, fileTreePath2)
        # Verify that the old tree is gone.
        exception = None
        try:
            fileTools.dir_content(oldTreePath, recursive=True)
        except NotADirectoryError as exc:
            exception = exc
        self.assertEqual(type(exception), NotADirectoryError)
        # Verify the new path values in the tree config.
        rootPath = self._emptyFiles['root_path']
        self.assertEqual(rootPath.endswith(
            '/tests/file_tree2'), True)
        path = self._emptyFiles['path']
        self.assertEqual(path.endswith(
            '/tests/file_tree2/abcdef1234567890abcdef1234567890c'), True)
        # Fetch folder content from the new location for verification.
        result = fileTools.dir_content(path, recursive=True)
        self.assertEqual(result[0]['path'], 'level1a')
        self.assertEqual(result[0]['content'][0]['path'], 'level1a/config.cfg')
        self.assertEqual(result[0]['content'][1]['path'],
            'level1a/some text.txt')
        self.assertEqual(result[1]['path'], 'static.html')
        shutil.rmtree(fileTreePath2)

    @classmethod
    def tearDownClass(cls):
        if os.path.isdir(cls._fileTreePath):
            shutil.rmtree(cls._fileTreePath)


if __name__ == '__main__':
    unittest.main()
