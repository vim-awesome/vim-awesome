"""Utility functions for the API """

import json
import flask


def jsonify(data):
    """Returns a flask.Response of data, JSON-stringified.

    This is basically Flask's jsonify
    (https://github.com/mitsuhiko/flask/blob/master/flask/json.py), but plugs
    an XSS hole.
    """
    indent = None if flask.request.is_xhr else 2

    jsonified = json.dumps(data, indent=indent)
    jsonified_safe = jsonified.replace('</', '<\\/')

    return flask.current_app.response_class(jsonified_safe,
            mimetype='application/json')


def api_not_found(message):
    return (message, 404)


def api_bad_request(message):
    return (message, 400)
