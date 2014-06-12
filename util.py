import calendar
import time


def api_not_found(message):
    return (message, 404)


def api_bad_request(message):
    return (message, 400)


def to_timestamp(dt):
    return calendar.timegm(dt.timetuple())


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
