import collections
import os

import rethinkdb as r
import yaml

import db.util

r_conn = db.util.r_conn


def get_all():
    filename = os.path.join(os.path.dirname(__file__), 'categories.yaml')
    with open(filename) as f:
        categories = yaml.safe_load(f)

    _aggregate_category_tags(categories)

    return categories


def _aggregate_category_tags(categories):
    """Mutates categories with the tags that belong to each category.

    For each category, we derive all the tags that belong to that category by
    merging the tags of all the plugins of that category.
    """
    for category in categories:
        category_plugins = r.table('plugins').filter(
                {'category': category['id']}).pluck('tags').run(r_conn())

        tags_counter = collections.Counter()
        for plugin in category_plugins:
            tags_counter.update(plugin['tags'])

        category['tags'] = [
                {'id': k, 'count': v} for k, v in tags_counter.most_common()]
