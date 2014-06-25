import json
import itertools
import logging
import re

import flask
from flask import request
from flask.ext.cache import Cache
import requests
import rethinkdb as r

import db
import util

try:
    import secrets
    _HIPCHAT_TOKEN = secrets.HIPCHAT_TOKEN
    _HIPCHAT_ROOM_ID = secrets.HIPCHAT_ROOM_ID
except ImportError:
    _HIPCHAT_TOKEN = None
    _HIPCHAT_ROOM_ID = None

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

    # Log all errors to HipChat as well.
    from web.hipchat_log_handler import HipChatHandler
    hipchat_handler = HipChatHandler(_HIPCHAT_TOKEN,
            _HIPCHAT_ROOM_ID, notify=True, color='red', sender='Flask')
    hipchat_handler.setLevel(logging.ERROR)
    hipchat_handler.setFormatter(formatter)
    logging.getLogger('').addHandler(hipchat_handler)


@cache.cached(timeout=60 * 60 * 4, key_prefix='search_index')
def get_search_index_cached():
    return db.plugins.get_search_index()


@cache.cached(timeout=60 * 60 * 4, key_prefix='all_categories')
def get_all_categories_cached():
    return db.categories.get_all()


# Catch-all route for single-page app. We specify our own `key_prefix` to
# @cache.cached instead of using the default `request.path` because this is
# a catch-all route for many different paths which all should have the same
# response.
# TODO(david): Alternatively serve this out of Nginx
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
@cache.cached(timeout=60 * 60, key_prefix='index.html')
def index(path):
    return flask.render_template('index.html', env=app.config['ENV'])


@app.route('/crash')
def crash():
    """Throw an exception to test error logging."""
    class WhatIsTorontoError(Exception):
        pass

    logging.warn("Crashing because you want me to (hit /crash)")
    raise WhatIsTorontoError("OH NOES we've crashed!!!!!!!!!! /crash was hit")


def _should_skip_get_plugins_cache():
    """Whether the current request to /api/plugins should not be cached."""
    page = int(request.args.get('page', 1))
    search = request.args.get('query', '')

    # Only cache empty searches for now.
    # TODO(david): Also cache simple category and tag searches. May also want
    #     to actually use a proper cache backend like Redis so we can
    #     arbitrarily cache (right now we use an in-memory cache).
    should_cache = search == '' and (1 <= page <= 10)
    return not should_cache


def _make_get_plugins_cache_key():
    """Get a cache key for the /api/plugins route.

    By default this is just request.path which ignores query params.
    """
    page = int(request.args.get('page', 1))
    search = request.args.get('query', '')
    return '%s_%s_%s' % (request.path, page, search)


# TODO(david): Move API functions out of this file once we have too many
# TODO(david): API functions should return content-type header JSON
@app.route('/api/plugins', methods=['GET'])
@cache.cached(timeout=60 * 60, key_prefix=_make_get_plugins_cache_key,
        unless=_should_skip_get_plugins_cache)
def get_plugins():
    RESULTS_PER_PAGE = 20

    page = int(request.args.get('page', 1))
    search = request.args.get('query', '')

    results = get_search_index_cached()

    if search:
        tokens = [t.lower() for t in sorted(search.split())]
        results, tokens = _apply_category_filters(results, tokens)
        results, tokens = _apply_tag_filters(results, tokens)
        results = _apply_keyword_filters(results, tokens)

    count = len(results)
    total_pages = (count + RESULTS_PER_PAGE - 1) / RESULTS_PER_PAGE  # ceil

    results = results[((page - 1) * RESULTS_PER_PAGE):
            (page * RESULTS_PER_PAGE)]

    return json.dumps({
        'plugins': results,
        'total_pages': total_pages,
        'total_results': count,
        'results_per_page': RESULTS_PER_PAGE,
    })


# TODO(david): Consider saving categories just as special tags. Would make
#     search implementation simpler but determining which category a plugin
#     belongs to harder. See discussion on
#     http://phabricator.benalpert.com/D171
def _apply_category_filters(results, tokens):
    """Consumes and applies category filters (e.g. "cat:other") to results.

    Arguments:
        results: List of search result plugins.
        tokens: Remaining search text tokens that have not been consumed.

    Returns:
        (results, tokens): Results that match the given category, and tokens
        that have not been consumed.
    """
    category_filter = lambda t: t.startswith('cat:')
    category_tokens = filter(category_filter, tokens)
    tokens = list(itertools.ifilterfalse(category_filter, tokens))

    if category_tokens:
        category_ids = set(t[len('cat:'):] for t in category_tokens)
        results = filter(lambda plugin:
                plugin['category'] in category_ids, results)

    return results, tokens


def _apply_tag_filters(results, tokens):
    """Consumes and applies tag filters (e.g. "tag:python") to search results.

    Arguments:
        results: List of search result plugins.
        tokens: Remaining search text tokens that have not been consumed.

    Returns:
        (results, tokens): Results that match the given tag, and tokens
        that have not been consumed.
    """
    tag_filter = lambda t: t.startswith('tag:')
    tag_tokens = filter(tag_filter, tokens)
    tokens = list(itertools.ifilterfalse(tag_filter, tokens))

    if tag_tokens:
        required_tags = set(t[len('tag:'):] for t in tag_tokens)
        results = filter(lambda plugin:
                required_tags <= set(plugin['tags']), results)

    return results, tokens


def _apply_keyword_filters(results, tokens):
    """Filters results that match the given keywords (tokens).

    Arguments:
        results: List of search result plugins.
        tokens: Keywords to filter results on.

    Returns:
        List of plugins that match the given keywords.
    """
    if tokens:
        # Create a regex that matches a string S iff for each keyword K in
        # `search` there is a corresponding word in S that begins with K.
        tokens_regex = (r'\b%s' % re.escape(t) for t in tokens)
        search_regex = re.compile('.*'.join(tokens_regex))

        # Surprisingly, regex matching like this is slightly faster than
        # prefix-matching two sorted lists of tokens.
        results = filter(lambda plugin:
                search_regex.search(plugin['keywords']), results)

    return results


@app.route('/api/plugins/<slug>', methods=['GET'])
def get_plugin(slug):
    plugin = r.table('plugins').get(slug).run(r_conn())

    if plugin:
        return json.dumps(db.plugins.to_json(plugin))
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
@cache.cached(timeout=60 * 60)
def get_tags():
    tags = r.table('tags').filter({}).run(r_conn())
    return json.dumps(list(tags))


@app.route('/api/categories', methods=['GET'])
@cache.cached(timeout=60 * 60)
def get_categories():
    return json.dumps(get_all_categories_cached())


@app.route('/api/plugins/<slug>/category/<category>', methods=['PUT'])
def update_plugin_category(slug, category):
    plugin = r.table('plugins').get(slug).run(r_conn())
    if not plugin:
        return util.api_not_found('No plugin with slug %s' % slug)

    if not category in [c['id'] for c in get_all_categories_cached()]:
        return util.api_bad_request('No such category %s' % category)

    # TODO(david): Also update search index (stale cache)
    plugin['category'] = category
    r.table('plugins').update(plugin).run(r_conn())
    return json.dumps({'category': plugin['category']})


@app.route('/api/submit', methods=['POST'])
def submit_plugin():
    plugin_data = flask.request.form.to_dict()
    plugin_data['tags'] = json.loads(plugin_data['tags'])
    db.submitted_plugins.insert(plugin_data)

    # Notify HipChat of this submission.
    # TODO(david): Also have email notifications.
    if _HIPCHAT_TOKEN and _HIPCHAT_ROOM_ID:
        message = "Someone just submitted a plugin!\n%s" % (
               json.dumps(plugin_data, indent=4))  # JSON for pretty-printing
        payload = {
           'auth_token': _HIPCHAT_TOKEN,
           'notify': 1,
           'color': 'green',
           'from': 'Vim Awesome',
           'room_id': _HIPCHAT_ROOM_ID,
           'message': message,
           'message_format': 'text',
        }

        try:
            requests.post('https://api.hipchat.com/v1/rooms/message',
                    data=payload, timeout=10)
        except Exception:
            logging.exception('Failed to notify HipChat of plugin submisson')

    return flask.redirect('/thanks-for-submitting')


if __name__ == '__main__':
    app.debug = True
    app.run(port=5001)
