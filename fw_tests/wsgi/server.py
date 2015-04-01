#@PydevCodeAnalysisIgnore
# pylint: disable=missing-docstring
# pylint: disable=line-too-long
# pylint: disable=too-many-public-methods
# pylint: disable=invalid-name
# pylint: disable=too-many-statements

# import os
# import shutil
import unittest
# import tempfile

import fw.wsgi.server as wsgiserver


class ServerMock:
    """Mock class for the wsgi server."""
    def __init__(self, bind_address, apps):
        self._address = bind_address[0]
        self._port = bind_address[1]
        self._apps = apps
        self._started = False

    def start(self):
        self._started = True

    def stop(self):
        self._started = True

    def __repr__(self):
        return '{}: {}:{}, {}.'.format(self.__class__.__name__, self._address,
            self._port, self._started)


def _test_entry_method(_, start_response):
    """Method for testing the server."""
    response = 'Foobar'
    encoded_data = response.encode('utf-8')
    content_length = len(encoded_data)
    status = '200 OK'
    response_headers = [
        ('Content-Type', 'text/plain'),
        ('Content-Length', '{}'.format(content_length))
    ]
    start_response(status, response_headers)
    return [encoded_data]  # Send response data.


class TestGitManage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def test_01_start_wsgi_server(self):
        address = 'localhost'
        port = 8080
        apps = {
            '/': _test_entry_method
        }
        server = wsgiserver.start_wsgi(address, port, apps,
            server_class=ServerMock)
        self.assertEqual('ServerMock: localhost:8080, True.', str(server))

    @classmethod
    def tearDownClass(cls):
        pass


if __name__ == '__main__':
    unittest.main()
