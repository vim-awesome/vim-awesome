import calendar


def api_not_found(message):
    return (message, 404)


def to_timestamp(dt):
    return calendar.timegm(dt.timetuple())
