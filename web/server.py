import json
import logging
import re

import flask
from flask import request
from flask.ext.cache import Cache
import rethinkdb as r

import db
import util

r_conn = db.util.r_conn


app = flask.Flask(__name__)
app.config.from_envvar('FLASK_CONFIG')
cache = Cache(app)


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
    RESULTS_PER_PAGE = 20

    page = int(request.args.get('page', 1))
    search = request.args.get('query', '')

    results = db.plugins.get_search_index()

    if search:
        # Create a regex that matches a string S iff for each keyword K in
        # `search` there is a corresponding word in S that begins with K.
        tokens = (t.lower() for t in sorted(search.split()))
        tokens_regex = (r'\b%s' % re.escape(t) for t in tokens)
        search_regex =  re.compile('.*'.join(tokens_regex))

        # Surprisingly, regex matching like this is slightly faster than
        # prefix-matching two sorted lists of tokens.
        results = filter(lambda plugin:
                search_regex.search(plugin['keywords']), results)

    count = len(results)
    total_pages = (count + RESULTS_PER_PAGE - 1) / RESULTS_PER_PAGE  # ceil

    results = results[((page - 1) * RESULTS_PER_PAGE):
            (page * RESULTS_PER_PAGE)]

    return json.dumps({
        'plugins': results,
        'total_pages': total_pages,
    })


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
