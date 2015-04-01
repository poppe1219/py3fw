#@PydevCodeAnalysisIgnore
# pylint: disable=missing-docstring
# pylint: disable=line-too-long
# pylint: disable=too-many-public-methods
# pylint: disable=invalid-name
# pylint: disable=too-many-statements
# pylint: disable=protected-access

import os
import shutil
import unittest
import tempfile

import fw.config
import fw.config.manage as configmanage
import fw.file.tools as filetools
import fw.git.api as gitapi
import fw.git.manage as gitmanage


def verify_content(path, content):
    with open(path, "r") as file:
        file_content = file.read()
    return file_content == content


class TestGitManage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._testPath = os.sep.join([tempfile.gettempdir(), 'tests'])
        cls._ignorePath = os.sep.join([cls._testPath, 'ignore'])
        cls._repoPathAlpha = os.sep.join([cls._testPath, 'repo_alpha'])
        cls._repoPathBeta = os.sep.join([cls._testPath, 'repo_beta'])
        configmanage.register_config_package(fw.config)

    def test_01a_write_git_ignore(self):
        # With default content.
        path = filetools.join_path(self._ignorePath, ".gitignore")
        filename = gitmanage.write_git_ignore(self._ignorePath)
        content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
"""
        self.assertEqual(path, filename)
        self.assertEqual(True, verify_content(path, content))

    def test_01b_write_git_ignore(self):
        # With custom content.
        path = filetools.join_path(self._ignorePath, ".gitignore")
        content = """__pycache__/
*.py[cod]
notes/
foobar.py
"""
        filename = gitmanage.write_git_ignore(self._ignorePath,
            ignore_content=content)
        self.assertEqual(path, filename)
        self.assertEqual(True, verify_content(path, content))

    def test_02a_new_repo(self):
        config = gitmanage.new_repo(self._repoPathAlpha, 'Repo 1')
        revision = gitapi.revision(config)
        description = 'Created new repo: {}.'.format(config['@config_id'])
        self.assertEqual(revision['desc'], description)
        self.assertEqual(config['name'], 'Repo 1')
        log = gitapi.log(config)
        self.assertIn('commit ', log)
        self.assertIn('Author: ', log)
        self.assertIn('Date: ', log)
        self.assertIn(description, log)

    def test_02b_new_repo(self):
        ignore_content = """foobar/
"""
        config = gitmanage.new_repo(self._repoPathAlpha, 'Repo 2',
            user='Foo Bar <foo@bar.com>', repo_id='my_special_repo',
            ignore_content=ignore_content)
        revision = gitapi.revision(config)
        description = 'Created new repo: my_special_repo.'
        self.assertEqual(revision['desc'], description)
        self.assertEqual(config['name'], 'Repo 2')
        log = gitapi.log(config)
        self.assertIn('commit ', log)
        self.assertIn('Author: Foo Bar <foo@bar.com>', log)
        self.assertIn('Date: ', log)
        self.assertIn(description, log)
        ignore_path = filetools.join_path(config['path'], ".gitignore")
        self.assertEqual(True, verify_content(ignore_path, ignore_content))

    def test_03_move_repo(self):
        config = gitmanage.new_repo(self._repoPathAlpha, 'Repo 3')
        gitmanage.move_repo(config, self._repoPathBeta)
        # Verify the moved repo.
        new_path = filetools.join_path(self._repoPathBeta,
            config['@config_id'])
        revision = gitapi.revision(config)
        description = 'Created new repo: {}.'.format(config['@config_id'])
        self.assertEqual(config['path'], new_path)
        self.assertEqual(revision['desc'], description)
        self.assertEqual(config['name'], 'Repo 3')
        log = gitapi.log(config)
        self.assertIn('commit ', log)
        self.assertIn('Author: ', log)
        self.assertIn('Date: ', log)
        self.assertIn(description, log)

    def test_04_remove_repo(self):
        config = gitmanage.new_repo(self._repoPathAlpha, 'Repo 4')
        revision = gitapi.revision(config)
        description = 'Created new repo: {}.'.format(config['@config_id'])
        self.assertEqual(revision['desc'], description)
        # Removed repo.
        gitmanage.remove_repo(config)
        self.assertEqual(False, os.path.isdir(config['path']))

    @classmethod
    def tearDownClass(cls):
        if os.path.isdir(cls._ignorePath):
            shutil.rmtree(cls._ignorePath)
        if os.path.isdir(cls._repoPathAlpha):
            shutil.rmtree(cls._repoPathAlpha)
        if os.path.isdir(cls._repoPathBeta):
            shutil.rmtree(cls._repoPathBeta)


if __name__ == '__main__':
    unittest.main()
