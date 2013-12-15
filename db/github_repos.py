"""A table of all known GitHub repos of vim plugins that we want to scrape."""

import rethinkdb as r

import db.util

r_conn = db.util.r_conn


def create_table():
    db.util.create_table('github_repos')
    db.util.create_index('github_repos', 'owner_repo',
            lambda repo: [repo['owner'], repo['repo_name']])


def insert_with_owner_repo(owner, repo_name):
    """Insert a new row with the given owner and repo names if not already
    present.

    Returns True if a new row was inserted, False if a repo with the given
    arguments already exists.
    """
    query = r.table('github_repos').get_all([owner, repo_name],
            index='owner_repo')
    repo = db.util.get_first(query)

    if repo is None:
        r.table('github_repos').insert({
            'owner': owner,
            'repo_name': repo_name,
            'last_scraped_at': 0,
            'times_scraped': 0,
            'is_blacklisted': False,
            'normalized_plugin_name': '',
        }).run(r_conn())
        return True
    else:
        return False
