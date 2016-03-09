import unittest

from mock import patch
from test.utils import fixture_data, mock_api_response
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
        Bundle 'https://github.com/Raimondi/delimitMate/'

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
            'https://github.com/Raimondi/delimitMate/'
        ]

        rx = github._VUNDLE_PLUGIN_REGEX
        self.assertEquals(rx.findall(vimrc), expected_matches)

    def test_neobundle_plugin_regex(self):
        vimrc = """
        NeoBundle 'scrooloose/nerdtree'
        NeoBundleFetch 'Shougo/neobundle.vim'
        NeoBundleLazy 'Shougo/unite.vim'
        """

        expected_matches = [
            'scrooloose/nerdtree',
            'Shougo/neobundle.vim',
            'Shougo/unite.vim',
        ]

        rx = github._NEOBUNDLE_PLUGIN_REGEX
        self.assertEquals(rx.findall(vimrc), expected_matches)

    def test_bundle_owner_repo_regex(self):
        rx = github._BUNDLE_OWNER_REPO_REGEX

        def test(bundle, expected):
            self.assertEquals(rx.search(bundle).groups(), expected)

        test('gmarik/vundle', ('gmarik', 'vundle'))
        test('gmarik/vundle/', ('gmarik', 'vundle'))
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
        test('https://github.com/vim-scripts/The-NERD-tree.git',
            ('vim-scripts', 'The-NERD-tree'))
        test('https://github.com/Raimondi/delimitMate/',
            ('Raimondi', 'delimitMate'))

    def test_submodule_is_bundle_regex(self):
        s = github._SUBMODULE_IS_BUNDLE_REGEX.search

        self.assertIsNotNone(s('submodule "bundle/ropevim"'))
        self.assertIsNotNone(s('submodule "vim/bundle/handlebars"'))
        self.assertIsNotNone(s('submodule "available-bundles/unimpaired"'))
        self.assertIsNotNone(s(
            'submodule "vim/vim.symlink/bundle/vim-pathogen"'))
        self.assertIsNotNone(s('submodule "submodules/vim_plugins/ag.vim"'))
        self.assertIsNotNone(s(
            'submodule "submodules/vim-plugins/python-mode"'))

        self.assertIsNone(s('submodule ".emacs.d/packages/groovy"'))
        self.assertIsNone(s('submodule "theme/sundown"'))
        self.assertIsNone(s('submodule "jedi"'))

    def test_extract_bundle_repos_from_file(self):
        file_contents = """
        Plug 'tpope/fugitive.vim'
        Plug 'https://github.com/Valoric/YouCompleteMe'

        Bundle 'ownerName/repository'
        NeoBundle 'anotherOwner/anotherRepo'
        """

        actual = github._extract_bundle_repos_from_file(file_contents)

        expected = github.ReposByManager(
            [('ownerName', 'repository')],
            [('anotherOwner', 'anotherRepo')],
            [('tpope', 'fugitive.vim'), ('Valoric', 'YouCompleteMe')])

        self.assertEqual(actual, expected)

    @patch('tools.scrape.github.get_api_page')
    def test_extract_vimplug_bundle_repos_from_dir(self, mock_get_api_page):
        mock_get_api_page.side_effect = mock_api_response

        dir_data = fixture_data('/repos/captbaritone/dotfiles/contents')
        actual = github._extract_bundle_repos_from_dir(dir_data).vimplug

        expected = [
            ('captbaritone', 'molokai'),
            ('chriskempson', 'vim-tomorrow-theme'),
            ('altercation', 'vim-colors-solarized'),
            ('fxn', 'vim-monochrome'),
            ('chriskempson', 'base16-vim'),
            ('NLKNguyen', 'papercolor-theme'),
            ('tpope', 'vim-git'),
            ('cakebaker', 'scss-syntax.vim'),
            ('xsbeats', 'vim-blade'),
            ('qrps', 'lilypond-vim'),
            ('plasticboy', 'vim-markdown'),
            ('mattn', 'emmet-vim'),
            ('edsono', 'vim-matchit'),
            ('ervandew', 'supertab'),
            ('scrooloose', 'syntastic'),
            ('tpope', 'vim-unimpaired'),
            ('bling', 'vim-airline'),
            ('ctrlpvim', 'ctrlp.vim'),
            ('rking', 'ag.vim'),
            ('tpope', 'vim-eunuch'),
            ('tpope', 'vim-commentary'),
            ('tpope', 'vim-sleuth'),
            ('bkad', 'CamelCaseMotion'),
            ('AndrewRadev', 'splitjoin.vim'),
            ('gcmt', 'taboo.vim'),
            ('christoomey', 'vim-tmux-navigator'),
            ('tpope', 'vim-surround'),
            ('tpope', 'vim-repeat'),
            ('michaeljsmith', 'vim-indent-object'),
            ('bkad', 'CamelCaseMotion'),
            ('vim-scripts', 'argtextobj.vim'),
            ('tpope', 'vim-fugitive'),
            ('airblade', 'vim-gitgutter'),
            ('projects', 'vim-vigilant'),
            ('benmills', 'vimux'),
            ('davidhalter', 'jedi-vim'),
            ('vimwiki', 'vimwiki'),
            ('vim-scripts', 'pythonhelper'),
            ('pangloss', 'vim-javascript'),
            ('reedes', 'vim-pencil'),
            ('mbbill', 'undotree'),
            ('parkr', 'vim-jekyll'),
            ('mattn', 'webapi-vim'),
            ('mattn', 'gist-vim')]

        self.assertEqual(actual, expected)

    @patch('db.github_repos.DotfilesGithubRepos.get_with_owner_repo')
    @patch('db.github_repos.DotfilesGithubRepos.upsert_with_owner_repo')
    @patch('tools.scrape.github.get_api_page')
    def test_get_plugin_repose_from_dotfiles(self, mock_get_api_page,
            mock_get_dotfiles, mock_upsert_dotfiles):

        mock_get_api_page.side_effect = mock_api_response
        mock_get_dotfiles.return_value = {}
        mock_upsert_dotfiles.return_value = {}

        dotfiles = {
            'full_name': 'captbaritone/dotfiles',
            'pushed_at': '2015'}

        actual = github._get_plugin_repos_from_dotfiles(dotfiles, 'search')

        expected = {
            'neobundle_repos_count': 0,
            'pathogen_repos_count': 0,
            'vimplug_repos_count': 44,
            'vundle_repos_count': 0}

        self.assertDictEqual(actual, expected)

    @patch('tools.scrape.github.get_api_page')
    def test_extract_pathogen_repos(self, mock_get_api_page):
        mock_get_api_page.side_effect = mock_api_response

        dir_data = fixture_data('/repos/jemiahlee/dotfiles/contents')
        actual = github._extract_pathogen_repos(dir_data)

        expected = [
            ('takac', 'vim-hardtime'),
            ('klen', 'python-mode'),
            ('rking', 'ag.vim'),
            ('hdima', 'python-syntax')
        ]

        self.assertListEqual(actual, expected)
