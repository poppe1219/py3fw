"""Docstring


"""

# Python imports.
import re
import cgi
import datetime
import tempfile
import http.cookies
import urllib.parse

# Regex from https://gist.github.com/dalethedeveloper/1503252
DETECT_MOBILE = re.compile((
    r'Mobile|iP(hone|od|ad)|Android|BlackBerry|IEMobile|Kindle|NetFront|'
    r'Silk-Accelerated|(hpw|web)OS|Fennec|Minimo|Opera M(obi|ini)|Blazer|'
    r'Dolfin|Dolphin|Skyfire|Zune'
), re.I | re.M)

# Browsers:
# r'Chrome/[0-9-_.]+'

# OS:
# r'Windows NT [0-9-_.]+'
# r'Mac OS X [0-9-_.]+'


def analyze_request_path(request, methods):
    """Doc string."""
    path = request['PATH_INFO']
    if not '/' in path:
        return methods['redirect_with_slash']  # Redirect add slash.
    parts = path.split('/')
    last_part = parts[len(parts) - 1]
    if last_part == '':
        return methods['call_to_app']  # Last character was a slash. Proceed.
    if '.' in last_part:
        return methods['resource_requested']  # A resource has been requested.
    return methods['redirect_with_slash']  # Redirect add slash.


def redirect_with_slash(session):
    """Doc string."""
    request = session['@tmp']['request']
    response = session['@tmp']['response']
    path = request['PATH_INFO'] + '/'
    query_string = request.get('QUERY_STRING', '')
    response['status'] = '301 Moved Permanently'
    response['headers'] = {
        'Location': path + query_string,
        'Content-Length': '0',
        'Content-Type': 'text/plain'
    }


def parse_query_string(request):
    """Parses the query string  into a dictionary.

    It is stored in the request dictionary with the key 'parsed.qs'.

    """
    query_string = dict(urllib.parse.parse_qsl(request['QUERY_STRING']))
    request['parsed.qs'] = query_string


def parse_cookies(request):
    """Parses the requests cookies.

    Returns the public sid from the cookies if it exists, else returns None.

    """
    cookies = http.cookies.SimpleCookie(request.get('HTTP_COOKIE', ''))
    request['parsed.cookies'] = cookies
    sid_cookie = request['parsed.cookies'].get('sid')
    if sid_cookie:
        return sid_cookie.value
    else:
        return None


def new_response(app_config):
    """Creates a response dictionary."""
    charset = app_config.get('charset', 'utf-8')
    return {
        'charset': charset,
        'cookies': http.cookies.SimpleCookie(),
        'data': [],
        'binary_data': None,
        'doctype': None,
        'errors': {},
        'headers': {
            'Content-Type': 'text/html; charset={}'.format(charset)
        },
        'server_commands': [],
        'status': '200 OK'
    }


def analyze_request_device(request):
    """Doc string."""
    user_agent = request.get('HTTP_USER_AGENT', '')
    user_info = {
            'user_agent': user_agent,
            'mobile': False,
            'browser': None,
            'orientation': None
        }
    if user_agent != '':
        match = DETECT_MOBILE.search(user_agent)
        if not match is None:
            user_info['mobile'] = True
    return user_info


def prepare_response_data(response):
    """Encodes and calculates the content length."""
    data = response.get('data', [])
    binary_data = response.get('binary_data', [])
    if data == [] and binary_data is not None:
        encoded_data = binary_data
    else:
        response_data = ''.join(data)
        encoded_data = response_data.encode(response['charset'])
        # Important to calculate the length after the data is encoded.
    content_length = len(encoded_data)
    response['headers']['Content-Length'] = content_length
    return encoded_data


def prepare_response_headers(response):
    """Translate headers to a list of tuples, adds eventual cookies."""
    response_headers = []
    for name, value in response['headers'].items():
        if type(value) == int:
            value = '{}'.format(value)
        response_headers.append((name, value))
    response_headers.extend(("set-cookie", morsel.OutputString())
                    for morsel in response['cookies'].values())
    return response_headers


def parse_form_data(request, private_sid, transfers, buffer_size=1024 * 200):
    """Parses the form data into a FieldStorage instance.

    The FieldStorage instance is stored in the request dictionary with the key
    'parsed.formdata'.
    If the content length is larger than buffer_size, the data is fed into a
    temporary file and a progress notification is continuously set in cached
    transfers.
    The progress can be read by separate ajax calls and provide feedback for
    the user.

    """
    transfer_id = None
    total_length = int(request.get('CONTENT_LENGTH', 0))
    if total_length == 0:
        return {}
    if total_length > buffer_size:
        length = total_length
        if 'upload_id' in request['parsed.qs'].keys():
            transfer_id = request['parsed.qs']['upload_id']
        else:
            transfer_id = str(datetime.datetime.now())
        if private_sid in transfers.keys():
            session_transfers = transfers[private_sid]
        else:
            session_transfers = {}
            transfers[private_sid] = session_transfers
        session_transfers[transfer_id] = 0
        stream = request['wsgi.input']
        body = tempfile.TemporaryFile(mode='w+b')
        while length > 0:
            part = stream.read(min(length, buffer_size))
            if not part:
                break
            body.write(part)
            length -= len(part)
            session_transfers[transfer_id] = length / total_length
        body.seek(0)
    else:
        body = request['wsgi.input']
    formdata = cgi.FieldStorage(environ=request, fp=body)
    if transfer_id is not None:  # If we have a completed transfer.
        del session_transfers[transfer_id]  # Clean up for this transfer.
        if len(transfers[private_sid]) == 0:  # If session no more transfers.
            del transfers[private_sid]  # Clean up all transfers for session.
    request['parsed.formdata'] = formdata
