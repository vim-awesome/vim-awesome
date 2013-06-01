import rethinkdb as r


def main():
    conn = r.connect()

    r.db_create('vim_awesome').run(conn)
    conn.use('vim_awesome')

    r.table_create('plugins').run(conn)
    r.table('plugins').insert([
        {
            'name': 'ctrlp.vim',
            'github_url': 'https://github.com/kien/ctrlp.vim',
            'vim_script_id': 3736
            'short_desc': 'Fuzzy file, buffer, mru, tag, etc finder.',
            'long_desc': """# ctrlp.vim
                Full path fuzzy __file__, __buffer__, __mru__, __tag__, __...__
                finder for Vim.

                * Written in pure Vimscript for MacVim, gVim and Vim 7.0+.
                * Full support for Vim's regexp as search patterns.
                * Built-in Most Recently Used (MRU) files monitoring.
                * Built-in project's root finder.
                * Open multiple files at once.
                * Create new files and directories.
                * [Extensible][2].""",
            'github_stars': 2021,
            'homepage': 'http://kien.github.io/ctrlp.vim/',
        },
        {
            'name': 'YouCompleteMe',
            'github_url': 'https://github.com/Valloric/YouCompleteMe',
            'vim_script_id': None,
            'description': 'A code-completion engine for Vim',
            'long_desc': """YouCompleteMe is a fast, as-you-type, fuzzy-search
            code completion engine for [Vim][]. It has several completion
            engines: an identifier-based engine that works with every
            programming language, a semantic, [Clang][]-based engine that
            provides native semantic code completion for
            C/C++/Objective-C/Objective-C++ (from now on referred to as "the
            C-family languages"), a [Jedi][]-based completion engine for Python
            and an omnifunc-based completer that uses data from Vim's
            omnicomplete system to provide semantic completions for many other
            languages (Ruby, PHP etc.).""",
            'github_stars': 1723,
            'homepage': 'http://valloric.github.io/YouCompleteMe/',
        },
    ]).run(conn)


if __name__ == '__main__':
    main()
