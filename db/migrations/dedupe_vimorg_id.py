"""De-duplicate the vimorg_id column in the plugins table."""

import re

import rethinkdb as r

import db.plugins
import db.util

r_conn = db.util.r_conn


if __name__ == '__main__':
    grouped_plugins = r.table('plugins').group('vimorg_id').run(r_conn())

    for vimorg_id, plugins in grouped_plugins.iteritems():
        if not vimorg_id:
            continue

        # We only need to concern ourselves with duplicated vim.org IDs
        if len(plugins) == 1:
            continue

        print '\nPlugin with vim.org ID %s occurs %s times' % (vimorg_id,
                len(plugins))

        to_delete = []
        to_keep = []

        for plugin in plugins:
            # Plugins scraped from github.com/vim-scripts that don't have
            # a vimorg_url must have not been successfully matched to the
            # corresponding vim.org plugin. These can be removed.
            if (plugin['github_vim_scripts_repo_name'] and not
                    plugin['vimorg_url']):
                print ('Delete %s because it is an unmatched '
                        'github.com/vim-scripts plugin' % (plugin['slug']))
                to_delete.append(plugin)
                continue

            # If no GitHub info is available for this plugin, it's probably
            # a duplicate vim.org plugin scraped after the original
            if (not plugin['github_owner'] and not
                    plugin['github_vim_scripts_repo_name']):
                print ('Delete %s because it is an extra vim.org plugin' %
                        plugin['slug'])
                to_delete.append(plugin)
                continue

            # Otherwise, we have an original plugin that should be preserved
            print 'Keep plugin %s' % plugin['slug']
            to_keep.append(plugin)

        # We expect to keep at least two plugins because plugins with the same
        # vim.org ID can only accumulate when there is already a duplicate
        # (these original duplicates arose due to mistakenly associating
        # vim.org IDs with GitHub repos whose homepages were vim.org URLs).
        assert len(to_keep) >= 2

        # Delete the newly-scraped extra plugins that accumulated due to
        # existing duplicates.
        for plugin in to_delete:
            r.table('plugins').get(plugin['slug']).delete().run(r_conn())

        # Out of the ones to keep, only one should get the vim.org ID. Pick the
        # one that has the most users.
        most_used = max(to_keep, key=lambda p: max(p['github_bundles'],
                p['github_vim_scripts_bundles']))
        for plugin in to_keep:
            if plugin['slug'] != most_used['slug']:
                r.table('plugins').get(plugin['slug']).update(
                        {'vimorg_id': ''}).run(r_conn())

        print 'Plugin %s gets to keep its vim.org ID' % most_used['slug']
