import codecs
import os

import rethinkdb as r

import db.init_db
import db.plugins
import db.util
import tags


def main():
    conn = r.connect()

    try:
        r.db_create('vim_awesome').run(conn)
    except r.RqlRuntimeError:
        pass  # Ignore db already created
    conn.use('vim_awesome')

    db.init_db.ensure_tables_and_indices()

    def read_file(filename):
        full_path = os.path.join(os.path.dirname(__file__), filename)
        with codecs.open(full_path, encoding='utf-8', mode='r') as f:
            return f.read()

    ctrlp_readme = read_file('ctrlp.md')
    youcompleteme_readme = read_file('youcompleteme.md')

    db.plugins.insert([
        {
            'id': 'ctrlp-example-plugin',
            'name': 'ctrlp.vim',
            'github_url': 'https://github.com/kien/ctrlp.vim',
            'vim_script_id': 3736,
            'github_short_desc': 'Fuzzy file, buffer, mru, tag, etc finder.',
            'github_readme': ctrlp_readme,
            'github_stars': 2021,
            'homepage': 'http://kien.github.io/ctrlp.vim/',
            'tags': ['buffer', 'file', 'mru', 'fuzzy', 'finder'],
        },
        {
            'id': 'youcompleteme-example-plugin',
            'name': 'YouCompleteMe',
            'github_url': 'https://github.com/Valloric/YouCompleteMe',
            'vim_script_id': None,
            'github_short_desc': 'A code-completion engine for Vim',
            'github_readme': youcompleteme_readme,
            'github_stars': 1723,
            'homepage': 'http://valloric.github.io/YouCompleteMe/',
            'tags': ['autocomplete', 'fuzzy', 'C'],
        },
    ], upsert=True)

    # TODO(david): Add other fields like friendly name, description
    r.table('tags').insert([{
        'id': 'buffer',
        'count': 1,
    }])

    tags.aggregate_tags()

if __name__ == '__main__':
    main()
