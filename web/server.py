import logging

import flask

app = flask.Flask(__name__)

# TODO(david)
#app.config.from_envvar('FLASK_CONFIG')

# TODO(david): Add logging handler


@app.route('/')
def index():
    return flask.render_template('index.html')


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
