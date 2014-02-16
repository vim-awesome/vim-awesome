# -*- coding: utf-8 -*-

import unittest

import db.plugins


class PluginsTest(unittest.TestCase):

    def test_update_plugin(self):
        def assert_update(old, new, expected):
            updated = db.plugins.update_plugin(old, new)
            self.assertEquals(updated, expected)

        # Ensure we get basic dict.update behavior.
        assert_update({'a': 1, 'b': 1}, {'a': 2, 'c': 1},
                {'a': 2, 'b': 1, 'c': 1})

        # Should keep latest updated date.
        assert_update({'updated_at': 1}, {}, {'updated_at': 1})
        assert_update({}, {'updated_at': 5}, {'updated_at': 5})
        assert_update({'updated_at': 1}, {'updated_at': 5}, {'updated_at': 5})

        # Should keep earliest created date.
        assert_update({'created_at': 1}, {}, {'created_at': 1})
        assert_update({}, {'created_at': 5}, {'created_at': 5})
        assert_update({'created_at': 1}, {'created_at': 5}, {'created_at': 1})

    def test_merge_dict_except_none(self):
        merge = db.plugins._merge_dict_except_none

        # Basic merge works
        self.assertEquals(merge({'a': 1}, {}), {'a': 1})
        self.assertEquals(merge({'a': 1}, {'b': 2}), {'a': 1, 'b': 2})
        self.assertEquals(merge({'a': 1}, {'a': 2}), {'a': 2})
        self.assertEquals(merge({'a': 1, 'b': 2}, {'a': 3}), {'a': 3, 'b': 2})

        # Does not merge in any None values
        self.assertEquals(merge({'a': 1}, {'a': None}), {'a': 1})
        self.assertEquals(merge({'a': 1}, {'b': None}), {'a': 1})
        self.assertEquals(merge({'a': 1}, {'a': None, 'b': 2}),
                {'a': 1, 'b': 2})

        # Make sure we don't mutate arguments
        a = {'a': 1, 'b': 2}
        b = {'a': 3, 'c': 4}
        self.assertEquals(merge(a, b), {'a': 3, 'b': 2, 'c': 4})
        self.assertEquals(a, {'a': 1, 'b': 2})
        self.assertEquals(b, {'a': 3, 'c': 4})

    def test_generate_normalized_name(self):
        def test(name, expected):
            gen = db.plugins._normalize_name
            self.assertEquals(gen({'vimorg_name': name}), expected)

        test('nerdcommenter', 'nerdcommenter')
        test('The NERD Commenter', 'nerdcommenter')
        test('The-NERD-Commenter', 'nerdcommenter')
        test('The-vim-NERD-Commenter.vim', 'nerdcommenter')  # This I made up
        test('NERD_tree', 'nerdtree')
        test(u'oh-l\xe0-l\xe0', 'ohlala')
        test(u'\u2605darkZ\u2605', 'darkz')
        test('abc-vim', 'abc')
        test('cscope.vim', 'cscope')
        test('vim-powerline', 'powerline')
        test('systemverilog.vim--Kanovsky', 'systemverilog')
        test('Ruby/Sinatra', 'rubysinatra')
        test('bufexplorer.zip', 'bufexplorer')
        test('runzip', 'runzip')

    def test_is_similar_author_name(self):
        similar = db.plugins._is_similar_author_name

        self.assertTrue(similar('Tim Pope', 'Tim Pope'))
        self.assertTrue(similar(u'Kim Silkeb\xe6kken', u'Kim Silkeb\xe6kken'))
        self.assertTrue(similar('nanotech', 'NanoTech'))
        self.assertTrue(similar('Marty Grenfell', 'Martin Grenfell'))
        self.assertTrue(similar('gmarik', 'gmarik gmarik'))
        self.assertTrue(similar('Miles Sterrett', 'Miles Z. Sterrett'))
        self.assertTrue(similar('Suan', 'Suan Yeo'))
        self.assertTrue(similar('jlanzarotta', 'jeff lanzarotta'))

        # Unfortunately, the following will cause some assertions below to fail
        #self.assertTrue(similar('Shougo', 'Shougo Matsushita'))

        self.assertFalse(similar('Bob', 'Joe'))
        self.assertFalse(similar('Paul Graham', 'Paul Bucheit'))
        self.assertFalse(similar('Taylor Swift', 'Barack Obama'))

    def test_are_plugins_different(self):
        diff = db.plugins._are_plugins_different

        self.assertTrue(diff({'vimorg_id': 1}, {'vimorg_id': 2}))
        self.assertTrue(diff(
                {'github_owner': 'tpope', 'github_repo_name': 'Red'},
                {'github_owner': 'tpope', 'github_repo_name': 'Long Live'}))
        self.assertTrue(diff(
                {'github_owner': 'tpope', 'github_repo_name': 'bbq'},
                {'github_owner': 'sjl', 'github_repo_name': 'bbq'}))
        self.assertTrue(diff(
                {'vimorg_id': 1, 'github_owner': 2, 'github_repo_name': 2},
                {'vimorg_id': 1, 'github_owner': 3, 'github_repo_name': 3}))
        self.assertTrue(diff(
                {'vimorg_id': 2, 'github_owner': 1, 'github_repo_name': 1},
                {'vimorg_id': 3, 'github_owner': 1, 'github_repo_name': 1}))

        self.assertFalse(diff({}, {}))
        self.assertFalse(diff({'vimorg_id': 1}, {}))
        self.assertFalse(diff({}, {'vimorg_id': 1}))
        self.assertFalse(diff({'vimorg_id': 1}, {'vimorg_id': 1}))
        self.assertFalse(diff({},
                {'github_owner': 'sjl', 'github_repo_name': 'Gundo'}))
        self.assertFalse(diff(
            {'github_owner': 'sjl', 'github_repo_name': 'Gundo'}, {}))
        self.assertFalse(diff(
                {'github_owner': 'sjl', 'github_repo_name': 'Gundo'},
                {'github_owner': 'sjl', 'github_repo_name': 'Gundo'}))
        self.assertFalse(diff({'vimorg_id': 1},
                {'github_owner': 'sjl', 'github_repo_name': 'Gundo'}))
