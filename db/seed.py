import codecs
import os

import rethinkdb as r


def main():
    conn = r.connect()

    try:
        r.db_create('vim_awesome').run(conn)
    except r.RqlRuntimeError:
        pass  # Ignore db already created
    conn.use('vim_awesome')

    try:
        r.table_create('plugins').run(conn)
    except r.RqlRuntimeError:
        pass  # Ignore table already created

    def read_file(filename):
        full_path = os.path.join(os.path.dirname(__file__), filename)
        with codecs.open(full_path, encoding='utf-8', mode='r') as f:
            return f.read()

    ctrlp_readme = read_file('ctrlp.md')
    youcompleteme_readme = read_file('youcompleteme.md')

    r.table('plugins').insert([
        {
            'id': 'ctrlp-example-plugin',
            'name': 'ctrlp.vim',
            'github_url': 'https://github.com/kien/ctrlp.vim',
            'vim_script_id': 3736,
            'short_desc': 'Fuzzy file, buffer, mru, tag, etc finder.',
            'long_desc': ctrlp_readme,
            'github_stars': 2021,
            'homepage': 'http://kien.github.io/ctrlp.vim/',
        },
        {
            'id': 'youcompleteme-example-plugin',
            'name': 'YouCompleteMe',
            'github_url': 'https://github.com/Valloric/YouCompleteMe',
            'vim_script_id': None,
            'short_desc': 'A code-completion engine for Vim',
            'long_desc': youcompleteme_readme,
            'github_stars': 1723,
            'homepage': 'http://valloric.github.io/YouCompleteMe/',
        },
    ], upsert=True).run(conn)


if __name__ == '__main__':
    main()
