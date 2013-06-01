import json
import logging

import flask
import rethinkdb as r

app = flask.Flask(__name__)

app.config.from_envvar('FLASK_CONFIG')


# TODO(alpert): Read port and db from app.config?
def r_conn(box=[None]):
    if box[0] is None:
        box[0] = r.connect()
        box[0].use('vim_awesome')
    return box[0]

# TODO(david): Add logging handler


@app.route('/')
def index():
    return flask.render_template('index.html', env=app.config['ENV'])


@app.route('/crash')
def crash():
    """Throw an exception to test error logging."""
    class WhatIsTorontoError(Exception):
        pass

    logging.warn("Crashing because you want me to (hit /crash)")
    raise WhatIsTorontoError("OH NOES we've crashed!!!!!!!!!! /crash was hit")


# TODO(david): Move API functions out of this file once we have too many
@app.route('/api/plugins')
def plugins():
    # TODO(alpert): Support various filter and sort query parameters
    query = r.db('vim_awesome').table('plugins').run(r_conn())
    return json.dumps(list(query))


if __name__ == '__main__':
    app.debug = True
    app.run(port=5001)
