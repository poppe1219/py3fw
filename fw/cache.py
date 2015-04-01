"""Framework cache for configurations, sessions, references, etc."""
# pylint: disable=global-statement


__all__ = [
    'get_server_reference',
    'set_server_reference',
    'get_configs',
    'get_sessions',
    'get_transfers',
    'save_cached_values',
    'load_cached_values'
]

# A reference to the server instance. To allow calling methods like stop().
_SERVER_REFERENCE = None


def get_server_reference():
    """Docstring"""
    return _SERVER_REFERENCE


def set_server_reference(server):
    """Docstring"""
    global _SERVER_REFERENCE
    _SERVER_REFERENCE = server


# Globally accessible configurations.
_CONFIGURATIONS = {}


def get_configs():
    """Docstring"""
    return _CONFIGURATIONS


# Currently cached sessions.
_SESSIONS = {}


def get_sessions():
    """Docstring"""
    return _SESSIONS


# Large posts are tracked in transfers.
_TRANSFERS = {}


def get_transfers():
    """Docstring"""
    return _TRANSFERS


# Registered wsgi apps types.
_WSGI_APPS_TYPES = {}


def get_wsgi_apps_types():
    """Docstring"""
    return _WSGI_APPS_TYPES


# What the hell was I thinking here?
def save_cached_values():
    """Docstring"""
    pass


def load_cached_values():
    """Docstring"""
    pass
