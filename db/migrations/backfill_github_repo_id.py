"""Backfills tables to populate GitHub's repo ID."""

import rethinkdb as r

import db.plugins
import db.util

r_conn = db.util.r_conn


def backfill_github_plugin_repos():
    """Adds the 'repo_id' field from the repo_data field if available."""
    r.table('plugin_github_repos').update({
        'repo_id': r.row['repo_data']['id'].default('').coerce_to('string')
    }).run(r_conn())


def backfill_plugins():
    """Backfill rows of the plugin table with github_repo_id.

    Populated from the corresponding rows of the plugin_github_repos table,
    joining on the key (github_owner, github_repo_name).
    """
    r.table('plugins').update({'github_repo_id': ''}).run(r_conn())

    repos = r.table('plugin_github_repos').pluck(
           'repo_id', 'owner', 'repo_name').run(r_conn())

    for i, repo in enumerate(repos):
        if repo['repo_id'] == '':
            continue

        query = r.table('plugins').get_all([repo['owner'], repo['repo_name']],
               index='github_owner_repo')
        plugin = db.util.get_first(query)
        if not plugin:
            continue

        plugin['github_repo_id'] = repo['repo_id']
        db.plugins.insert(plugin)

        print '%s\tBackfilled %s' % (i, plugin['slug'])


if __name__ == '__main__':
    backfill_github_plugin_repos()
    backfill_plugins()
