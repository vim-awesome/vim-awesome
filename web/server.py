import json
import logging

import flask

app = flask.Flask(__name__)

app.config.from_envvar('FLASK_CONFIG')

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
    # TODO(david): (actually Ben) actually query the db. We'll probably also
    #     want to support various filter and sort query parameters.
    return json.dumps([{
        'name': 'ctrlp.vim',
        'description': 'Full path fuzzy file, buffer, mru, tag, ... '
            'finder for Vim.',
        'github_url': 'https://github.com/kien/ctrlp.vim',
        'url': 'http://kien.github.io/ctrlp.vim/',
    },
    {
        'name': 'YouCompleteMe',
        'description': 'YouCompleteMe is a fast, as-you-type, fuzzy-'
            'search code completion engine for Vim.',
        'github_url': 'https://github.com/Valloric/YouCompleteMe',
    }] * 10)


if __name__ == '__main__':
    app.debug = True
    app.run(port=5001)
