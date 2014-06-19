import json
import itertools
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


@cache.cached(timeout=60 * 60 * 4)
def get_search_index_cached():
    return db.plugins.get_search_index()


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

    results = get_search_index_cached()

    if search:
        tokens = [t.lower() for t in sorted(search.split())]

        # Look for any tag meta-keywords (e.g. tag:python)
        tag_filter = lambda t: t.startswith('tag:')
        tag_tokens = filter(tag_filter, tokens)
        tokens = list(itertools.ifilterfalse(tag_filter, tokens))

        # ... and apply these tag filters to the results
        if tag_tokens:
            required_tags = set(t[len('tag:'):] for t in tag_tokens)
            results = filter(lambda plugin:
                    required_tags <= set(plugin['tags']), results)

        # Create a regex that matches a string S iff for each keyword K in
        # `search` there is a corresponding word in S that begins with K.
        tokens_regex = (r'\b%s' % re.escape(t) for t in tokens)
        search_regex = re.compile('.*'.join(tokens_regex))

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


@app.route('/api/plugins/<slug>', methods=['GET'])
def get_plugin(slug):
    plugin = r.table('plugins').get(slug).run(r_conn())

    if plugin:
        return json.dumps(db.plugins.to_json(plugin, extended=True))
    else:
        return util.api_not_found('No plugin with slug %s' % slug)


# TODO(david): Make it not so easy for an attacker to completely obliterate all
#     of our tags, or at least be able to recover from it.
@app.route('/api/plugins/<slug>/tags', methods=['POST', 'PUT'])
def update_plugin_tags(slug):
    data = json.loads(flask.request.data)
    plugin = r.table('plugins').get(slug).run(r_conn())

    if not plugin:
        return util.api_not_found('No plugin with slug %s' % slug)

    db.plugins.update_tags(plugin, data['tags'])
    return json.dumps({'tags': plugin['tags']})


@app.route('/api/tags', methods=['GET'])
def get_tags():
    tags = r.table('tags').filter({}).run(r_conn())
    return json.dumps(list(tags))


@app.route('/api/categories', methods=['GET'])
def get_categories():
    return json.dumps(db.categories.get_all())


@app.route('/api/plugins/<slug>/category/<category>', methods=['PUT'])
def update_plugin_category(slug, category):
    plugin = r.table('plugins').get(slug).run(r_conn())
    if not plugin:
        return util.api_not_found('No plugin with slug %s' % slug)

    if not category in [c['id'] for c in db.categories.get_all()]:
        return util.api_bad_request('No such category %s' % category)

    # TODO(david): Also update search index (stale cache)
    plugin['category'] = category
    r.table('plugins').update(plugin).run(r_conn())
    return json.dumps({'category': plugin['category']})


if __name__ == '__main__':
    app.debug = True
    app.run(port=5001)
