import calendar
import re
import time


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
