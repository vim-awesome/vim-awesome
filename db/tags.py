"""Utility functions for the tags table."""

import rethinkdb as r

import db

r_conn = db.util.r_conn


def ensure_table():
    db.util.ensure_table('tags')


def add_tag(tag_id):
    """Increment count of given tag_id. Create row if does not exist."""
    tag = r.table('tags').get(tag_id).run(r_conn())

    if tag:
        tag['count'] += 1
        r.table('tags').update(tag).run(r_conn())
    else:
        r.table('tags').insert({
            'id': tag_id,
            'count': 1,
        }).run(r_conn())


def remove_tag(tag_id):
    """Decrement count of given tag_id."""
    tag = r.table('tags').get(tag_id).run(r_conn())

    if tag:
        tag['count'] = max(0, tag['count'] - 1)
        r.table('tags').update(tag).run(r_conn())


def aggregate_tags():
    """Aggregate the counts of all tags from each plugin.

    This is intended to be run daily in a cron job to mitigate the effects of
    race conditions and to clear out 0-count tags.
    """
    # Clear out all 0-count tags.
    r.table('tags').filter({'count': 0}).delete().run(r_conn())

    # Reset all counts.
    r.table('tags').update({'count': 0}).run(r_conn())

    # TODO(david): This can definitely be optimized if necessary, eg. by
    #     batching inserts/updates in Rethink or using Python's Counter class
    #     to aggregate counts in-memory first
    # TODO(david): Figure out why Rethink 1.11 is giving the following error if
    #     we don't call list() on the result set:
    #     RqlClientError: Token 14 not in stream cache.
    all_plugins = list(r.table('plugins').run(r_conn()))
    for plugin in all_plugins:
        if 'tags' not in plugin:
            plugin['tags'] = []
            r.table('plugins').update(plugin).run(r_conn())
        for tag in plugin['tags']:
            add_tag(tag)
