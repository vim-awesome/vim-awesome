import logging

import flask
from cache import cache
from raven.contrib.flask import Sentry

import db
import web.api.api as api


try:
    import secrets
    _HIPCHAT_TOKEN = secrets.HIPCHAT_TOKEN
    _HIPCHAT_ROOM_ID = secrets.HIPCHAT_ROOM_ID
    _SENTRY_DSN = secrets.SENTRY_DSN
except ImportError:
    _HIPCHAT_TOKEN = None
    _HIPCHAT_ROOM_ID = None
    _SENTRY_DSN = None

r_conn = db.util.r_conn


app = flask.Flask(__name__)
app.config.from_envvar('FLASK_CONFIG')
app.register_blueprint(api.api)
cache.init_app(app)
# Initialize the Sentry plugin
Sentry(app, dsn=_SENTRY_DSN)


# Add logging handlers on the production server.
if app.config['ENV'] == 'prod':
    from logging.handlers import TimedRotatingFileHandler
    logging.basicConfig(level=logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s in'
            ' %(module)s:%(lineno)d %(message)s')

    # Log everything at the INFO level or higher to file.
    file_handler = TimedRotatingFileHandler(filename=app.config['LOG_PATH'],
            when='D')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)
    logging.getLogger('').addHandler(file_handler)  # Root handler

    # Log all errors to HipChat as well.
    from web.hipchat_log_handler import HipChatHandler
    hipchat_handler = HipChatHandler(_HIPCHAT_TOKEN,
            _HIPCHAT_ROOM_ID, notify=True, color='red', sender='Flask')
    hipchat_handler.setLevel(logging.ERROR)
    hipchat_handler.setFormatter(formatter)
    logging.getLogger('').addHandler(hipchat_handler)


# Catch-all route for single-page app. We specify our own `key_prefix` to
# @cache.cached instead of using the default `request.path` because this is
# a catch-all route for many different paths which all should have the same
# response.
# TODO(david): Alternatively serve this out of Nginx
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
@cache.cached(timeout=60 * 60 * 28, key_prefix='index.html')
def index(path):
    return flask.render_template('index.html', env=app.config['ENV'])


@app.route('/crash')
def crash():
    """Throw an exception to test error logging."""
    class WhatIsTorontoError(Exception):
        pass

    logging.warn("Crashing because you want me to (hit /crash)")
    raise WhatIsTorontoError("OH NOES we've crashed!!!!!!!!!! /crash was hit")


if __name__ == '__main__':
    app.debug = True
    app.run(port=5001)
