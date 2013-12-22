"""A table of all known GitHub repos of vim plugins that we want to scrape."""

import rethinkdb as r

import db.util

r_conn = db.util.r_conn


_ROW_SCHEMA = {
    # Last time this repo was scraped (Unix timestamp in seconds)
    'last_scraped_at': 0,

    # Number of times scraped
    'times_scraped': 0,

    # Whether this repo should not be used for fetching plugin data
    'is_blacklisted': False,

    # Raw repo data from GitHub API
    'repo_data': {},

    # IDs of vim.org scripts where this repo was mentioned
    'from_vim_scripts': [],
}


def ensure_table():
    db.util.ensure_table('github_repos')
    db.util.ensure_index('github_repos', 'owner')
    db.util.ensure_index('github_repos', 'last_scraped_at')
    db.util.ensure_index('github_repos', 'owner_repo',
            lambda repo: [repo['owner'], repo['repo_name']])


def upsert_with_owner_repo(repo):
    """Insert or update a row using (owner, repo_name) as the key.

    Returns True if a new row was inserted.
    """
    owner = repo['owner']
    repo_name = repo['repo_name']

    assert owner
    assert repo_name

    query = r.table('github_repos').get_all([owner, repo_name],
            index='owner_repo')
    db_repo = db.util.get_first(query)

    if db_repo is None:
        repo_to_insert = dict(_ROW_SCHEMA, **repo)
        r.table('github_repos').insert(repo_to_insert).run(r_conn())
        return True
    else:
        query.update(repo).run(r_conn())
        return False
