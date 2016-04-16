import logging
import calendar
import re
import requests
import time

from requests.exceptions import HTTPError

try:
    import secrets
    GITTER_TOKEN = getattr(secrets, 'GITTER_TOKEN', None)
    GITTER_ROOM_ID = getattr(secrets, 'GITTER_ROOM_ID', None)
except ImportError:
    GITTER_TOKEN = None
    GITTER_ROOM_ID = None


_VIMORG_ID_FROM_URL_REGEX = re.compile(
        r'vim.org/scripts/script.php\?script_id=(\d+)')


def api_not_found(message):
    return (message, 404)


def api_bad_request(message):
    return (message, 400)


def to_timestamp(dt):
    return calendar.timegm(dt.timetuple())


def get_vimorg_id_from_url(url):
    """Returns the vim.org script_id from a URL if it's of a vim.org script,
    otherwise, returns None.
    """
    match = _VIMORG_ID_FROM_URL_REGEX.search(url or '')
    if match:
        return match.group(1)

    return None


def time_it(func):
    """Simple decorator to print out the execution time of a function."""
    def wrapped(*args, **kwargs):
        time_start = time.time()
        result = func(*args, **kwargs)
        time_end = time.time()

        print ('%s called with (%s, %s) took %.3f sec' %
              (func.__name__, args, kwargs, time_end - time_start))

        return result

    return wrapped


def log_to_gitter(message):
    if not GITTER_TOKEN or not GITTER_ROOM_ID:
        logging.info('Missing either room id or auth token for Gitter')
        return

    headers = {
        'Authorization': 'Bearer %s' % GITTER_TOKEN,
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': 'application/json'}

    body = {'text': message}

    url = 'https://api.gitter.im/v1/rooms/%s/chatMessages' % GITTER_ROOM_ID

    r = requests.post(url, headers=headers, json=body)
    try:
        r.raise_for_status()
    except HTTPError:
        logging.exception('Bad response from Gitter.im sending: %s' % message)
        return False

    return True
