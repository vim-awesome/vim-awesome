import json
import logging
import re

import flask
from flask import request
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
    search = request.args.get('query', '')
    query = r.db('vim_awesome').table('plugins')

    if search:
        needles = [t.lower() for t in re.findall(r'\w+', search)]
        needles.sort()
        query = query.filter(r.js(r"""(function(row) {
            var needles = %s;

            var name = row.name || "";
            var desc = row.short_desc || "";
            var tokens = (name + " " + desc).toLowerCase().match(/\w+/g) || [];
            tokens.sort();
            tokens.forEach(function(token) {
                // if needles and token.startswith(needles[0]):
                if (needles.length && token.lastIndexOf(needles[0], 0) === 0) {
                    needles.shift();
                }
            });

            return needles.length === 0;
        })""" % json.dumps(needles)))

    return json.dumps(list(query.run(r_conn())))


if __name__ == '__main__':
    app.debug = True
    app.run(port=5001)
