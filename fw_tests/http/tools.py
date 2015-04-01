#@PydevCodeAnalysisIgnore
# pylint: disable=missing-docstring
# pylint: disable=line-too-long
# pylint: disable=too-many-public-methods
# pylint: disable=invalid-name
# pylint: disable=too-many-statements

import unittest

import fw.http.tools as httptools

METHODS = {
    'call_to_app': 'call_to_app',
    'redirect_with_slash': 'redirect_with_slash',
    'resource_requested': 'resource_requested',
}


class TestSessionManage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def test_01_analyze_request_path(self):
        request = {'PATH_INFO': ''}
        result = httptools.analyze_request_path(request, METHODS)
        self.assertEqual(result, 'redirect_with_slash')

    def test_02_analyze_request_path(self):
        request = {'PATH_INFO': '/'}
        result = httptools.analyze_request_path(request, METHODS)
        self.assertEqual(result, 'call_to_app')

    def test_03_analyze_request_path(self):
        request = {'PATH_INFO': '/foo'}
        result = httptools.analyze_request_path(request, METHODS)
        self.assertEqual(result, 'redirect_with_slash')

    def test_04_analyze_request_path(self):
        request = {'PATH_INFO': '/foo/'}
        result = httptools.analyze_request_path(request, METHODS)
        self.assertEqual(result, 'call_to_app')

    def test_05_analyze_request_path(self):
        request = {'PATH_INFO': '/favicon.ico'}
        result = httptools.analyze_request_path(request, METHODS)
        self.assertEqual(result, 'resource_requested')

    def test_06_analyze_request_path(self):
        request = {'PATH_INFO': '/foo/css/main.css'}
        result = httptools.analyze_request_path(request, METHODS)
        self.assertEqual(result, 'resource_requested')

    def test_07_analyze_request_path(self):
        request = {'PATH_INFO': '/foo/css/main.foo'}
        result = httptools.analyze_request_path(request, METHODS)
        self.assertEqual(result, 'resource_requested')

    @classmethod
    def tearDownClass(cls):
        pass


if __name__ == '__main__':
    unittest.main()
