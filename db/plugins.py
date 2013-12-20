"""Utility functions for the plugins table."""

import rethinkdb as r

import db.util

r_conn = db.util.r_conn


def ensure_table():
    db.util.ensure_table('plugins')

    db.util.ensure_index('plugins', 'vim_script_id')
    db.util.ensure_index('plugins', 'name')
    db.util.ensure_index('plugins', 'github_stars')


# TODO(david): Yep, using an ODM enforcing a consistent schema would be great.
def insert(plugins, *args, **kwargs):
    """Insert or update a plugin or list of plugins.

    Although this would be more accurately named "upsert", this is a wrapper
    around http://www.rethinkdb.com/api/python/#insert that ensures
    a consistent plugin schema before inserting into DB.
    """
    if not isinstance(plugins, list):
        plugins = [plugins]

    mapped_plugins = []
    for plugin in plugins:
        plugin_with_defaults = dict({
            'tags': [],
            'homepage': '',
            'author': '',
            'created_at': 0,  # Timestamp in seconds
            'updated_at': 0,  # Timestamp in seconds
            'vim_script_id': None,  # Integer >= 1
            'vimorg_url': '',
            'vimorg_type': '',
            'vimorg_rating': 0,  # Integer
            'vimorg_num_raters': 0,  # Integer >= 0
            'vimorg_downloads': 0,  # Integer >= 0
            'vimorg_short_desc': '',
            'vimorg_long_desc': '',
            'vimorg_install_details': '',
            'github_stars': 0,  # Integer >= 0
            'github_url': '',
            'github_short_desc': '',
            'github_readme': '',
        }, **plugin)

        assert plugin_with_defaults['name']

        mapped_plugins.append(plugin_with_defaults)

    return r.table('plugins').insert(mapped_plugins, *args, **kwargs).run(
            r_conn())


def get_for_name(name):
    """Get the plugin model of the given name."""
    return db.util.get_first(r.table('plugins').get_all(name, index='name'))


def update_tags(plugin, tags):
    """Updates a plugin's tags to the given set, and updates aggregate tag
    counts.
    """
    plugin_tags = plugin['tags']
    added_tags = set(tags) - set(plugin_tags)
    removed_tags = set(plugin_tags) - set(tags)

    # TODO(david): May have to hold a lock while doing this
    map(db.tags.add_tag, added_tags)
    map(db.tags.remove_tag, removed_tags)

    plugin['tags'] = tags
    r.table('plugins').update(plugin).run(r_conn())


def is_more_authoritative(repo1, repo2):
    """Returns whether repo1 is a different and more authoritative GitHub repo
    about a certain plugin than repo2.

    For example, the original author's GitHub repo for Syntastic
    (https://github.com/scrooloose/syntastic) is more authoritative than
    vim-scripts's mirror (https://github.com/vim-scripts/Syntastic).
    """
    # If we have two different GitHub repos, take the latest updated, and break
    # ties by # of stars.
    if (repo1.get('github_url') and repo2.get('github_url') and
            repo1['github_url'] != repo2['github_url']):
        if repo1.get('updated_at', 0) > repo2.get('updated_at', 0):
            return True
        elif repo1.get('updated_at', 0) == repo2.get('updated_at', 0):
            return repo1.get('github_stars', 0) > repo2.get('github_stars', 0)
        else:
            return False
    else:
        return False


def update_plugin(old_plugin, new_plugin):
    """Merges properties of new_plugin onto old_plugin, much like a dict
    update.

    This is used to reconcile differences of data that we might get from
    multiple sources about the same plugin, such as from vim.org, vim-scripts
    GitHub repo, and the author's original GitHub repo.

    Does not mutate any arguments. Returns the updated plugin.
    """
    # If the old_plugin is constituted from information from a more
    # authoritative GitHub repo (eg. the author's) than new_plugin, then we
    # want to use old_plugin's data where possible.
    if is_more_authoritative(old_plugin, new_plugin):
        updated_plugin = dict(new_plugin, **old_plugin)
    else:
        updated_plugin = dict(old_plugin, **new_plugin)

    # Keep the latest updated date.
    if old_plugin.get('updated_at') and new_plugin.get('updated_at'):
        updated_plugin['updated_at'] = max(old_plugin['updated_at'],
                new_plugin['updated_at'])

    # Keep the earliest created date.
    if old_plugin.get('created_at') and new_plugin.get('created_at'):
        updated_plugin['created_at'] = min(old_plugin['created_at'],
                new_plugin['created_at'])

    return updated_plugin
