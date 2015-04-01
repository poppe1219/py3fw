#@PydevCodeAnalysisIgnore
# pylint: disable=missing-docstring
# pylint: disable=line-too-long
# pylint: disable=too-many-public-methods
# pylint: disable=invalid-name
# pylint: disable=too-many-statements

import unittest
import unittest.mock as mock

import fw.wsgi.apps as wsgiapps

APP_ROUTES = {
    'e_service': {
        'function': 'axiom.web.e_service.entry',
        'url_regex':
            (r'^/(?P<customer_name>[a-z0-9._-]+)/e-service/'
                r'(?P<service_name>[a-z0-9._-]+)/$')
    },
    'notes': {
        'function': 'amnesia.web.notes.entry',
        'url_regex':
            r'^/(?P<user_name>[a-z0-9._-]+)/notes/(?P<note>[a-z0-9._-]+)/$'
    },
    'my_pages': {
        'function': 'axiom.web.my_pages.entry',
        'url_regex': r'^/(?P<customer_name>[a-z0-9._-]+)/mina-sidor/$'
    }
}


def get_routes(wsgi_apps_types):
    routes = []
    for type_value in wsgi_apps_types.values():
        routes.append(type_value['url_regex'])
    return routes


class TestSessionManage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def test_01_get_path_parts_default(self):
        request = {'PATH_INFO': ''}
        parts = wsgiapps.get_path_parts(request, APP_ROUTES)
        self.assertEqual(parts, {})
        request = {'PATH_INFO': '/'}
        parts = wsgiapps.get_path_parts(request, APP_ROUTES)
        self.assertEqual(parts, {})

    def test_02_get_path_parts_default(self):
        request = {'PATH_INFO': '/mina-sidor/'}
        parts = wsgiapps.get_path_parts(request, APP_ROUTES)
        self.assertEqual(parts, {})

    def test_03_get_path_parts_default(self):
        request = {'PATH_INFO': '/foobar/mina-sidor/'}
        parts = wsgiapps.get_path_parts(request, APP_ROUTES)
        self.assertEqual(parts, {
            '@function': 'axiom.web.my_pages.entry',
            '@type_name': 'my_pages',
            'customer_name': 'foobar'
        })

    def test_04_get_path_parts_default(self):
        request = {'PATH_INFO': '/foobar/e-service/feedback/'}
        parts = wsgiapps.get_path_parts(request, APP_ROUTES)
        self.assertEqual(parts, {
            '@function': 'axiom.web.e_service.entry',
            '@type_name': 'e_service',
            'customer_name': 'foobar',
            'service_name': 'feedback'
        })

    @mock.patch('fw.config.manage.get_app_config', autospec=True)
    @mock.patch('fw.cache.get_wsgi_apps_types', autospec=True)
    def test_05_get_app_config(self, get_wsgi_apps_types, get_apt_config):
        get_apt_config.return_value = {'@foo': 'bar'}  # Fake config.
        get_wsgi_apps_types.return_value = APP_ROUTES
        request = {'PATH_INFO': '/foobar/e-service/feedback/'}
        config = wsgiapps.get_app_config(request)
        get_apt_config.assert_called_with({
            '@function': 'axiom.web.e_service.entry',
            '@type_name': 'e_service',
            'customer_name': 'foobar',
            'service_name': 'feedback'
        })
        self.assertEqual(config, {'@foo': 'bar'})  # Fake config.

    @classmethod
    def tearDownClass(cls):
        pass


if __name__ == '__main__':
    unittest.main()
