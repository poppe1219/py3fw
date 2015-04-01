#@PydevCodeAnalysisIgnore
# pylint: disable=missing-docstring
# pylint: disable=line-too-long
# pylint: disable=too-many-public-methods
# pylint: disable=invalid-name
# pylint: disable=too-many-statements
# pylint: disable=protected-access

import os
import shutil
import logging
import unittest
import tempfile
import warnings

import fw.log


class TestLog(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._test_path = os.sep.join([tempfile.gettempdir(), 'tests'])
        cls._log_path = os.sep.join([cls._test_path, 'log'])
        cls._log_file = os.sep.join([cls._log_path, 'test.log'])
        cls._log_format = ('%(asctime)-15s %(levelname)-8s %(message)s '
            '[%(name)s:line=%(lineno)s]')
        if os.path.isfile(cls._log_file):
            shutil.rmtree(cls._log_path)

    def test_1_setup_logger_default(self):
        fw.log.setup_logger(path=self._log_file, level=logging.INFO,
            log_format=self._log_format)
        logger = logging.getLogger()
        text1 = 'test_1: debug, should not be logged.'
        logger.debug(text1)
        with open(self._log_file, 'r') as f:
            logText = f.read()
        # Debug log line should not be logged.
        self.assertEqual(False, logText.find(text1) > -1)

    def test_2_setup_logger_code_warnings(self):
        fw.log.setup_logger(path=self._log_file, depr_warnings=True,
            log_format=self._log_format)
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        text1 = 'test_2: debug, should be logged.'
        logger.debug(text1)
        text2 = 'test_2: deprecation warning, should be logged.'
        warnings.warn(text2, DeprecationWarning)
        with open(self._log_file, 'r') as f:
            logText = f.read()
        # Debug log line should be logged.
        self.assertEqual(True, logText.find(text1) > -1)
        # Deprecation warning should be logged.
        self.assertEqual(True, logText.find(text2) > -1)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._log_path)


if __name__ == "__main__":
    unittest.main()
