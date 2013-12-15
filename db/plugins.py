"""Utility functions for the plugins table."""

import rethinkdb as r

import db.util

r_conn = db.util.r_conn


def create_table():
    db.util.create_table('plugins')

    # TODO(david): Actually use these secondary indices in our queries (Rethink
    #     doesn't have an optimizer yet. Must use get_all().)
    db.util.create_index('plugins', 'vim_script_id')
    db.util.create_index('plugins', 'name')


def get_for_name(name):
    """Get the plugin model of the given name."""
    return db.util.get_first(r.table('plugins').filter({'name': name}))


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
