"""Module for starting and stopping the wsgi Web server."""

# Python imports.
import logging
if __name__ == '__main__':
    import os
    import sys
    PARTS = __file__.split(os.path.sep)
    PARTS = PARTS[:-3]
    PATH = os.path.sep.join(PARTS)
    if not PATH in sys.path:
        sys.path.insert(0, PATH)
# System imports.
import fw.externals.wsgiserver as wsgiserver

LOG = logging.getLogger(__name__)


def start_wsgi(address, port, apps_list,
    server_class=wsgiserver.CherryPyWSGIServer):
    """Start up the wsgi server."""
    apps = wsgiserver.WSGIPathInfoDispatcher(apps_list)
    server = server_class((address, port, ), apps)
    LOG.info('Starting wsgi server, {}:{}.'.format(address, port))
    _run_wsgi(server)
    return server


def _run_wsgi(server):
    """Method that encapsulates the exception handling of the server."""
    try:
        server.start()
        LOG.info('Normal execution exit...')
    except KeyboardInterrupt:
        LOG.info(os.linesep)  # Continue to the finally-clause.
    except SystemExit:
        LOG.critical('SystemExit')
    except Exception as exc:
        LOG.critical('Exception: {}'.format(exc))
    except:
        LOG.critical('Without exception object.')
    finally:
        server.stop()  # Gracefully shut down the thread pool.
        LOG.info('Server stopped.')


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


if __name__ == '__main__':
    APPS = {
        '/': _test_entry_method
    }
    start_wsgi('localhost', 8080, APPS)
