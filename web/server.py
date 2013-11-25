import json
import logging
import re

import flask
from flask import request
import rethinkdb as r

import db
import util

app = flask.Flask(__name__)

app.config.from_envvar('FLASK_CONFIG')

r_conn = util.r_conn

# TODO(david): Add logging handler

# Catch-all route for single-page app
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    return flask.render_template('index.html', env=app.config['ENV'])


@app.route('/crash')
def crash():
    """Throw an exception to test error logging."""
    class WhatIsTorontoError(Exception):
        pass

    logging.warn("Crashing because you want me to (hit /crash)")
    raise WhatIsTorontoError("OH NOES we've crashed!!!!!!!!!! /crash was hit")


# TODO(david): Move API functions out of this file once we have too many
# TODO(david): API functions should return content-type header JSON
@app.route('/api/plugins', methods=['GET'])
def get_plugins():
    search = request.args.get('query', '')
    query = r.table('plugins')

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


@app.route('/api/plugins/<name>', methods=['GET'])
def get_plugin(name):
    plugin = db.plugins.get_for_name(name)
    if plugin:
        return json.dumps(plugin)
    else:
        return util.api_not_found('No plugin with name %s' % name)


# TODO(david): Make it not so easy for an attacker to completely obliterate all
#     of our tags, or at least be able to recover from it.
@app.route('/api/plugins/<name>/tags', methods=['POST', 'PUT'])
def update_plugin_tags(name):
    data = json.loads(flask.request.data)
    plugin = db.plugins.get_for_name(name)
    db.plugins.update_tags(plugin, data['tags'])
    return json.dumps({'tags': plugin['tags']})


@app.route('/api/tags', methods=['GET'])
def get_tags():
    tags = r.table('tags').filter({}).run(r_conn())
    return json.dumps(list(tags))


if __name__ == '__main__':
    app.debug = True
    app.run(port=5001)
