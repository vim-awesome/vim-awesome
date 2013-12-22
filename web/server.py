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

r_conn = db.util.r_conn


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
    query = r.table('plugins')

    # This will actually sort with github_stars taking precedence because it's
    # an index: http://www.rethinkdb.com/api/python/order_by/
    query = query.order_by(r.desc('vimorg_rating'),
            index=r.desc('github_stars'))

    # Specify a projection to limit fields returned to reduce network and
    # serialize/deserialize costs.
    query = query.pluck(['id', 'name', 'created_at', 'updated_at', 'tags',
        'homepage', 'author', 'vim_script_id', 'vimorg_rating',
        'vimorg_short_desc', 'github_stars', 'github_url',
        'github_short_desc'])

    if search:
        # TODO(david): Also search through tags. Figure out how to prioritize
        #     that in results ordering.
        # TODO(david): More optimization ideas:
        #     - add a field that's the space-delimited sort-uniqued tokens from
        #       the other fields that we want to search through (eg.
        #       descriptions, name, tags), and only search through that.
        #     - in-memory cache of plugins (~5000 plugins will fit). Could use
        #       a trie or prefix tree.
        #     - look into elasticsearch or similar
        #     - unfortunately, indexing a field does not make regex matching
        #       any faster

        # Wrap each token in the search string in a beginning-of-word regex.
        tokens_regex = (r'\b%s' % re.escape(t) for t in search.split())

        # (?i) means case-insensitive. See rethinkdb.com/api/python/match
        search_regex =  r'(?i)%s' % '.*'.join(tokens_regex)

        query = query.filter(lambda plugin:
                plugin['name'].match(search_regex) |
                plugin['github_short_desc'].match(search_regex) |
                plugin['vimorg_short_desc'].match(search_regex)
        )

    # TODO(david): Seriously need to optimize searches. This count query
    #     doubles the time. Or, don't show total pages and just tell the client
    #     whether there's a next page or not.
    count = query.count().run(r_conn())
    total_pages = (count + RESULTS_PER_PAGE - 1) / RESULTS_PER_PAGE  # ceil

    query = query.skip((page - 1) * RESULTS_PER_PAGE).limit(RESULTS_PER_PAGE)

    # TODO(david): Figure out why Rethink returns less results than count (eg.
    #     Rethink will report 7 pages of "python" plugins but show 2 plugins on
    #     page 3 and 2 plugins on page 4.). Or just throw out Rethink and do
    #     the search in-memory. :)
    return json.dumps({
        'plugins': list(query.run(r_conn())),
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
