"""Docstring"""

# Python imports.
import re
import logging
# Framework imports.
import fw.cache
import fw.config.manage as configmanage

LOG = logging.getLogger(__name__)


def get_app_config(request):
    """Doc string."""
    # Get system default, merged with customers/application type config.
    wsgi_apps_types = fw.cache.get_wsgi_apps_types()
    parts = get_path_parts(request, wsgi_apps_types)
    config = configmanage.get_app_config(parts)
    return config


def get_path_parts(request, wsgi_apps_types):
    """Doc string."""
    path = request['PATH_INFO'] or '/'
    if not path.endswith('/'):
        path = path + '/'
    parts = {}
    for type_name, type_values in wsgi_apps_types.items():
        regex = re.compile(type_values['url_regex'])
        if regex.match(path):
            parts['@type_name'] = type_name
            parts['@function'] = type_values['function']
            match = regex.match(path)
            for index in regex.groupindex:
                parts[index] = match.group(index)
            break
    return parts


def get_app_resource(session):
    """Doc string."""
    request = session['@tmp']['request']
    response = session['@tmp']['response']
    path = request['PATH_INFO']
    try:
        if path == '/favicon.ico':
            # get the file, path for default resources?
            response['binary_data'] = ''
        else:
            # Parse application path.
            # Determine path and access rights.
            # Get the file.
            response['binary_data'] = ''
    except FileNotFoundError as exc:
        response['status'] = '404 Not Found'
        LOG.exception('File "{}" not found, exc: {}.'.format(path, exc))
    except PermissionError as exc:
        response['status'] = '403 Forbidden'
        LOG.exception('Access denied to file "{}", exc: {}.'.format(path, exc))
    except Exception as exc:
        response['status'] = '500 Internal Server Error'
        LOG.exception('Failed to get file "{}", exc: {}.'.format(path, exc))
