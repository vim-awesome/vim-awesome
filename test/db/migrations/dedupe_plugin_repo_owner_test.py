import unittest
import itertools
from db.migrations.dedupe_plugin_repo_owner import merge_plugins


def dummy_plugin(**kwargs):
    default = {
            'slug': 'slug',
            'category': 'uncategorized',
            'tags': [],
            'github_bundles': 0,
            'vimorg_id': None}

    for key, value in kwargs.iteritems():
        default[key] = value

    return default


class MergePluginsTest(unittest.TestCase):

    def _test_merge(self, plugins, expected):
        """ Assert that a list of plugins will get merged into `expected`
        independent of order """

        # For every permutation ...
        for plugins_perm in itertools.permutations(plugins):
            actual = merge_plugins(plugins_perm)
            self.assertEquals(actual['slug'], expected['slug'])
            self.assertEquals(actual['category'], expected['category'])
            self.assertItemsEqual(actual['tags'], expected['tags'])
            self.assertEqual(actual['github_bundles'], expected['github_bundles'])
            self.assertEqual(actual['vimorg_id'], expected['vimorg_id'])

    def test_preserves_category(self):
        plugins = [
            dummy_plugin(),
            dummy_plugin(category='color')]

        expected = dummy_plugin(category='color')

        self._test_merge(plugins, expected)

    def test_preserves_shortes_slug(self):
        plugins = [
            dummy_plugin(slug='short-slug'),
            dummy_plugin(slug='medium-slug'),
            dummy_plugin(slug='much-longer-slug')]

        expected = dummy_plugin(slug='short-slug')
        self._test_merge(plugins, expected)

    def test_merges_tags(self):
        plugins = [
            dummy_plugin(tags=['a', 'b', 'c']),
            dummy_plugin(tags=[]),
            dummy_plugin(tags=['z'])]

        expected = dummy_plugin(tags=['a', 'b', 'c', 'z'])
        self._test_merge(plugins, expected)

    def test_collects_github_bundles(self):
        plugins = [
            dummy_plugin(github_bundles=1),
            dummy_plugin(github_bundles=0),
            dummy_plugin(github_bundles=8),
            dummy_plugin(github_bundles=8)]

        expected = dummy_plugin(github_bundles=17)
        self._test_merge(plugins, expected)

    def test_preserves_vimorg_id(self):
        plugins = [
            dummy_plugin(vimorg_id=None),
            dummy_plugin(vimorg_id="1234")]

        expected = dummy_plugin(vimorg_id="1234")
        self._test_merge(plugins, expected)
