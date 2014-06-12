import os

import yaml


categories = None


def get_all():
    global categories

    if not categories:
        filename = os.path.join(os.path.dirname(__file__), 'categories.yaml')
        with open(filename) as f:
            categories = yaml.safe_load(f)

    # TODO(david): Need to load all tags that go under each category

    return categories
