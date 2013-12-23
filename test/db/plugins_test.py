import unittest

import db.plugins


class PluginsTest(unittest.TestCase):

    def test_is_more_authoritative(self):
        ima = db.plugins.is_more_authoritative

        # Plugins are not all generated from GitHub data. Cannot compare.
        self.assertFalse(ima({}, {}))
        self.assertFalse(ima({'github_url': 'old'}, {}))
        self.assertFalse(ima({}, {'github_url': 'new'}))

        # Generated from the same GitHub repo. Not more authoritative.
        self.assertFalse(ima({'github_url': 'It was rare, I was there'},
                             {'github_url': 'It was rare, I was there'}))

        # More recently updated repo is more authoritative.
        self.assertFalse(ima(
                {'github_url': 'old', 'updated_at': 1},
                {'github_url': 'new', 'updated_at': 1}))
        self.assertFalse(ima(
                {'github_url': 'old', 'updated_at': 1},
                {'github_url': 'new', 'updated_at': 5}))
        self.assertTrue(ima(
                {'github_url': 'old', 'updated_at': 5},
                {'github_url': 'new', 'updated_at': 1}))

        # ... regardless of # of stars.
        self.assertFalse(ima(
                {'github_url': 'old', 'updated_at': 1, 'github_stars': 1},
                {'github_url': 'new', 'updated_at': 5, 'github_stars': 1}))
        self.assertFalse(ima(
                {'github_url': 'old', 'updated_at': 1, 'github_stars': 1},
                {'github_url': 'new', 'updated_at': 5, 'github_stars': 5}))
        self.assertFalse(ima(
                {'github_url': 'old', 'updated_at': 1, 'github_stars': 5},
                {'github_url': 'new', 'updated_at': 5, 'github_stars': 1}))
        self.assertTrue(ima(
                {'github_url': 'old', 'updated_at': 5, 'github_stars': 1},
                {'github_url': 'new', 'updated_at': 1, 'github_stars': 1}))
        self.assertTrue(ima(
                {'github_url': 'old', 'updated_at': 5, 'github_stars': 1},
                {'github_url': 'new', 'updated_at': 1, 'github_stars': 5}))
        self.assertTrue(ima(
                {'github_url': 'old', 'updated_at': 5, 'github_stars': 5},
                {'github_url': 'new', 'updated_at': 1, 'github_stars': 1}))

        # Break ties with # of stars.
        self.assertFalse(ima(
                {'github_url': 'old', 'github_stars': 1},
                {'github_url': 'new', 'github_stars': 1}))
        self.assertFalse(ima(
                {'github_url': 'old', 'github_stars': 1},
                {'github_url': 'new', 'github_stars': 5}))
        self.assertTrue(ima(
                {'github_url': 'old', 'github_stars': 5},
                {'github_url': 'new', 'github_stars': 1}))
        self.assertFalse(ima(
                {'github_url': 'old', 'updated_at': 1, 'github_stars': 1},
                {'github_url': 'new', 'updated_at': 1, 'github_stars': 1}))
        self.assertFalse(ima(
                {'github_url': 'old', 'updated_at': 1, 'github_stars': 1},
                {'github_url': 'new', 'updated_at': 1, 'github_stars': 5}))
        self.assertTrue(ima(
                {'github_url': 'old', 'updated_at': 1, 'github_stars': 5},
                {'github_url': 'new', 'updated_at': 1, 'github_stars': 1}))

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

        # Should keep GitHub URL of the more authoritative repo.
        assert_update({'github_url': 'old'}, {}, {'github_url': 'old'})
        assert_update({}, {'github_url': 'new'}, {'github_url': 'new'})
        assert_update({'github_url': 'old'}, {'github_url': 'new'},
                {'github_url': 'new'})
        assert_update({'github_url': 'old'},
                {'github_url': 'new', 'updated_at': 5},
                {'github_url': 'new', 'updated_at': 5})
        assert_update({'github_url': 'old', 'updated_at': 1},
                {'github_url': 'new', 'updated_at': 5},
                {'github_url': 'new', 'updated_at': 5})
        assert_update({'github_url': 'old', 'updated_at': 5},
                {'github_url': 'new', 'updated_at': 1},
                {'github_url': 'old', 'updated_at': 5})

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
