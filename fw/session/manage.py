"""Docstring"""

# Python imports.
import logging
import datetime
# Framework imports.
import fw.uuid
import fw.cache
import fw.http.tools as httptools

LOG = logging.getLogger(__name__)


def get_session(request, response, app_config):
    """Doc string."""
    sid_cookie = request.get('parsed.cookies', {}).get('sid')
    if sid_cookie is not None:
        public_sid = sid_cookie.value
        session = _retrieve_session(public_sid)
        if session is None:
            session = _init_session(request, response, app_config)
            session['events']['unhandled'].append(
                'Session not found: "{}"'.format(public_sid)
            )
            _store_session(session)
        else:
            update_session(session, request, response)
    else:
        session = _init_session(request, response, app_config)
        _store_session(session)
    return session


def _retrieve_session(public_sid):
    """Doc string."""
    sessions = fw.cache.get_sessions()
    session = sessions.get(public_sid)
    return session


def _store_session(session):
    """Doc string."""
    public_sid = session['@sid_public']
    sessions = fw.cache.get_sessions()
    if public_sid in sessions.keys():
        raise KeyError('Session public sid already exists.')
    sessions[public_sid] = session


def _init_session(request, response, app_config):
    """Creates a session dictionary."""
    return {
        '@api': {
            'type': 'jconf',
            'name': 'WebSession',
            'version': '1.0.0',
            'prev_version': None
        },
        '@app_config': app_config,
        '@sid_private': fw.uuid.get_unique_id(1),
        '@sid_public': fw.uuid.get_unique_id(2),
        '@time_created': datetime.datetime.now(),
        '@time_expires': str(
            datetime.datetime.now() + datetime.timedelta(hours=1, minutes=0)
        ),
        '@tmp': {
            'response': response,
            'request': request
        },
        'events': {
            'unhandled': [],
            'handled': []
        },
        'data': None,
        'new_session': True,
        'user': httptools.analyze_request_device(request)
    }


def update_session(session, request, response):
    session['@tmp']['response'] = response  # Override previous response.
    session['@tmp']['request'] = request  # Override previous request.
    if session['new_session'] == True:
        session['new_session'] = False
    request = session['@tmp']['request']
    user_agent = request.get('HTTP_USER_AGENT', '')
    if session['user']['user_agent'] != user_agent:
        if not session['user']['user_agent'] is None:
            LOG.info('Session changed user agent')
        session['user'] = httptools.analyze_request_device(request)
