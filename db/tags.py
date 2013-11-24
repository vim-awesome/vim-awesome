"""Utility functions for the tags table."""

import rethinkdb as r

import util

r_conn = util.r_conn


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
    """Aggregate the counts of all tags from each plugin."""
    util.db_create_table('tags')
    r.table('tags').update({'count': 0}).run(r_conn())

    # TODO(david): This can definitely be optimized if necessary, eg. by
    #     batching inserts/updates in Rethink or using Python's Counter class
    #     to aggregate counts in-memory first
    all_plugins = r.table('plugins').filter({}).run(r_conn())
    for plugin in all_plugins:
        if 'tags' not in plugin: continue
        for tag in plugin['tags']:
            add_tag(tag)
