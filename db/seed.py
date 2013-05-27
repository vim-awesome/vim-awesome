import rethinkdb as r


def main():
    conn = r.connect()

    r.db_create('vim_awesome').run(conn)
    conn.use('vim_awesome')

    r.table_create('plugins').run(conn)
    r.table('plugins').insert([
        {
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
        },
    ]).run(conn)


if __name__ == '__main__':
    main()
