"""Derived from:
    gitapi
    https://github.com/haard/gitapi
    MIT/BSD license. Copyright Fredrik Haard.

Bug fixed and modified extensively.

"""
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods
# pylint: disable=invalid-name
# pylint: disable=too-many-statements

import os
import shutil
import tempfile
import unittest

import fw.git.api as gitapi


class TestGitAPI(unittest.TestCase):

    @classmethod
    def _delete_and_create(cls, path):
        if os.path.exists(path):
            shutil.rmtree(path)
        os.mkdir(path)
        assert os.path.exists(path)

    @classmethod
    def setUpClass(cls):
        tempPath = tempfile.gettempdir()
        cls.path = os.sep.join([tempPath, 'tests', 'git'])
        cls._delete_and_create(cls.path)
        TestGitAPI._delete_and_create(cls.get_path("test"))
        TestGitAPI._delete_and_create(cls.get_path("test-clone"))
        TestGitAPI._delete_and_create(cls.get_path("test-clone-bare"))
        cls.repo = gitapi.create_repo(cls.get_path("test"),
            user="Testuser <test@example.com>")
        cls.clone = {
            'path': cls.get_path("test-clone"),
            'user': "Testuser <test@example.com>"
        }
        cls.bareclone = {
            'path': cls.get_path("test-clone-bare"),
            'user': "Testuser <test@example.com>"
        }
        # patch for Python 3
        if hasattr(cls, "assertEqual"):
            setattr(cls, "assertEquals", cls.assertEqual)
            setattr(cls, "assertNotEquals", cls.assertNotEqual)

    @classmethod
    def get_path(cls, path):
        """Doc String"""
        return os.sep.join([cls.path, path])

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.path, ignore_errors=True)

    def test_005_Init(self):
        gitapi.init(self.repo)
        self.assertTrue(os.path.exists(self.get_path("test/.git")))

    def test_020_Add(self):
        with open(self.get_path("test/file.txt"), "w") as out:
            out.write("stuff")
        gitapi.add(self.repo, "file.txt")

    def test_030_Commit(self):
        # Commit and check that we're on a real revision
        gitapi.commit(self.repo, "adding", user="test <test@example.com>")
        gitid = gitapi.sha1(self.repo)
        self.assertNotEquals(gitid, "000000000000")

        # write some more to file
        with open(self.get_path("test/file.txt"), "w+") as out:
            out.write("more stuff")

        # Commit and check that changes have been made
        gitapi.commit(self.repo, "modifying", user="test <test@example.com>")
        gitid2 = gitapi.sha1(self.repo)
        self.assertNotEquals(gitid, gitid2)

    def test_040_Log(self):
        rev = gitapi.revision(self.repo, gitapi.sha1(self.repo))
        self.assertEquals(rev['desc'], "modifying")
        self.assertEquals(rev['author'], "test")
        self.assertEquals(len(rev['parents']), 1)

#     def test_050_Checkout(self):
#         node = gitapi.sha1(self.repo)

#         gitapi.checkout(self.repo, 'HEAD~1')
#         self.assertNotEquals(gitapi.sha1(self.repo), node)
#         gitapi.checkout(self.repo, node)
#         self.assertEquals(gitapi.sha1(self.repo), node)

    def test_070_Config(self):
        for key, value in (("test.stuff.otherstuff", "tsosvalue"),
                  ("test.stuff.debug", "true"),
                  ("test.stuff.verbose", "false"),
                  ("test.stuff.list", "one two three")):
            gitapi.command(self.repo, "config", key, value)
        #re-read config
        gitapi.read_config(self.repo)
        self.assertEquals(gitapi.config(self.repo, 'test', 'stuff.otherstuff'),
                          "tsosvalue")

    def test_071_ConfigBool(self):
        self.assertTrue(gitapi.configbool(self.repo, 'test', 'stuff.debug'))
        self.assertFalse(gitapi.configbool(self.repo, 'test', 'stuff.verbose'))

    def test_072_ConfigList(self):
        self.assertTrue(gitapi.configlist(self.repo, 'test', 'stuff.list'),
                        ["one", "two", "three"])

    def test_090_ModifiedStatus(self):
        #write some more to file
        with open(self.get_path("test/file.txt"), "a") as out:
            out.write("stuff stuff stuff")
        status = gitapi.status(self.repo)
        self.assertEquals(status, {'M': ['file.txt']})

    def test_100_CleanStatus(self):
        #commit file created in 090
        gitapi.commit(self.repo, "Comitting changes",
            user="Test <test@example.com>")
        #Assert status is empty
        self.assertEquals(gitapi.status(self.repo), {})

    def test_110_UntrackedStatus(self):
        #Create a new file
        with open(self.get_path("test/file2.txt"), "w") as out:
            out.write("stuff stuff stuff")
        status = gitapi.status(self.repo)
        self.assertEquals(status, {'??': ['file2.txt']})

    def test_120_AddedStatus(self):
        #Add file created in 110
        gitapi.add(self.repo, "file2.txt")
        status = gitapi.status(self.repo)
        self.assertEquals(status, {'A': ['file2.txt']})

    def test_130_MissingStatus(self):
        #Commit file created in 120
        gitapi.commit(self.repo, "Added file")
#         import os
        os.unlink(self.get_path("test/file2.txt"))
        status = gitapi.status(self.repo)
        self.assertEquals(status, {'D': ['file2.txt']})

    def test_140_RemovedStatus(self):
        #Remove file from repo
        gitapi.remove(self.repo, "file2.txt")
        status = gitapi.status(self.repo)
        self.assertEquals(status, {'D': ['file2.txt']})

    def test_140_EmptyStatus(self):
        gitapi.reset(self.repo)
        status = gitapi.status(self.repo)
        self.assertEquals(status, {})

    def test_150_ForkAndMerge(self):
        #Store this version
        gitapi.sha1(self.repo)
        #creates new branch
        gitapi.branch(self.repo, "test", "HEAD~2")
        gitapi.checkout(self.repo, "test")
        with open(self.get_path("test/file3.txt"), "w") as out:
            out.write("this is more stuff")
        gitapi.add(self.repo, "file3.txt")
        gitapi.commit(self.repo, "adding head")
        branches = gitapi.branches(self.repo)
        self.assertTrue("test" in branches)

        #merge the changes
        gitapi.checkout(self.repo, "master")
        gitapi.merge(self.repo, "test")

        with open(self.get_path("test/file3.txt"), "r") as src:
            self.assertEqual(src.read(), "this is more stuff")

    def test_300_clone(self):
        # clone test to test clone
        self.clone = gitapi.clone(self.get_path("test"),
            self.get_path("test-clone"))
        self.assertEquals(self.clone['path'], self.repo['path'] + "-clone")

    def test_310_pull(self):
        # add a new directory with some files in test repo first
        os.mkdir(self.get_path("test/cities"))
        with open(self.get_path("test/cities/brussels.txt"), "w") as out:
            out.write("brussel")
        with open(self.get_path("test/cities/antwerp.txt"), "w") as out:
            out.write("antwerpen")
        gitapi.add(self.repo, "cities")
        message = "[TEST] Added two cities."
        gitapi.commit(self.repo, message)
        gitapi.pull(self.clone, self.get_path("test"))

        self.assertEquals(gitapi.sha1(self.clone), gitapi.sha1(self.repo))
        # check summary of pulled tip
        self.assertTrue(message in gitapi.log(self.clone, identifier="HEAD"))

    def test_320_push(self):
        # Make a bare clone of test.
        gitapi.clone(self.get_path('test'),
            self.get_path('test-clone-bare'), '--bare')
        # add another file in test-clone first
        with open(self.get_path("test-clone/cities/ghent.txt"), "w") as out:
            out.write("gent")
        gitapi.add(self.clone, 'cities')
        message = "[CLONE] Added one file."
        gitapi.commit(self.clone, message)
        gitapi.push(self.clone, self.get_path("test-clone-bare"),
            branch_name="master")

        self.assertEquals(gitapi.sha1(self.clone), gitapi.sha1(self.bareclone))
        # check summary of pushed tip
        self.assertTrue(message in gitapi.log(self.bareclone,
            identifier="HEAD"))


if __name__ == "__main__":
    unittest.main()
