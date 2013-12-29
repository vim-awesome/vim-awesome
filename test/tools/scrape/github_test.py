import unittest

from tools.scrape import github


class GithubTest(unittest.TestCase):

    def test_vundle_plugin_regex(self):
        vimrc = """Bundle 'gmarik/vundle0'
        Bundle 'gmarik/vundle1'
        Bundle    'gmarik/vundle2'
                \tBundle   'gmarik/vundle3'
        Bundle 'gmarik/vundle4' " Comment: Merry Swiftmas!!!!
        Bundle "gmarik/vundle5"
        Bundle 'taglist'
        Bundle 'ervandew/supertab.git'
        Bundle 'git://github.com/scrooloose/nerdtree'
        Bundle 'git://github.com/kien/ctrlp.vim.git'
        Bundle 'calendar.vim--Matsumoto'
        Bundle 'git://git.wincent.com/command-t.git'
        Bundle 'git@github.com:Valloric/YouCompleteMe.git'
        Bundle 'rstacruz/sparkup', {'rtp': 'vim/'}

        Bundle 'uh/oh
        "Bundle 'commented/out'
        """

        expected_matches = [
            'gmarik/vundle0',
            'gmarik/vundle1',
            'gmarik/vundle2',
            'gmarik/vundle3',
            'gmarik/vundle4',
            'gmarik/vundle5',
            'taglist',
            'ervandew/supertab.git',
            'git://github.com/scrooloose/nerdtree',
            'git://github.com/kien/ctrlp.vim.git',
            'calendar.vim--Matsumoto',
            'git://git.wincent.com/command-t.git',
            'git@github.com:Valloric/YouCompleteMe.git',
            'rstacruz/sparkup',
        ]

        rx = github._VUNDLE_PLUGIN_REGEX
        self.assertEquals(rx.findall(vimrc), expected_matches)

    def test_bundle_owner_repo_regex(self):
        rx = github._BUNDLE_OWNER_REPO_REGEX

        def test(bundle, expected):
            self.assertEquals(rx.search(bundle).groups(), expected)

        test('gmarik/vundle', ('gmarik', 'vundle'))
        test('taglist', (None, 'taglist'))
        test('ervandew/supertab.git', ('ervandew', 'supertab'))
        test('git://github.com/scrooloose/nerdtree',
                ('scrooloose', 'nerdtree'))
        test('git://github.com/kien/ctrlp.vim.git', ('kien', 'ctrlp.vim'))
        test('calendar.vim--Matsumoto', (None, 'calendar.vim--Matsumoto'))

        # Don't care about non-GitHub repos. They'll just 404 when we scrape.
        test('git://git.wincent.com/command-t.git',
                ('git.wincent.com', 'command-t'))

        test('git@github.com:Valloric/YouCompleteMe.git',
                ('Valloric', 'YouCompleteMe'))
