"""A table of all known GitHub repos of vim plugins that we want to scrape."""

import rethinkdb as r

import db.util

r_conn = db.util.r_conn


class GithubRepos(object):
    """Abstract base class of class methods to handle a table of GitHub
    repositories.
    """

    # Subclasses must override this.
    _TABLE_NAME = None

    # Fields we want to track for every GitHub repo. This can be extended with
    # extra fields for subclasses.
    _ROW_SCHEMA = {

        # Last time this repo was scraped (Unix timestamp in seconds)
        'last_scraped_at': 0,

        # Number of times scraped
        'times_scraped': 0,

        # Whether this repo should not be used for fetching plugin data
        'is_blacklisted': False,

        # Raw repo data from GitHub API
        'repo_data': {},

    }

    # Override this with URLs that should not be scraped.
    _BLACKLISTED_GITHUB_REPOS = []

    @classmethod
    def ensure_table(cls):
        db.util.ensure_table(cls._TABLE_NAME)

        db.util.ensure_index(cls._TABLE_NAME, 'owner')
        db.util.ensure_index(cls._TABLE_NAME, 'last_scraped_at')
        db.util.ensure_index(cls._TABLE_NAME, 'owner_repo',
                lambda repo: [repo['owner'], repo['repo_name']])

        cls.ensure_blacklisted_repos()

    @classmethod
    def ensure_blacklisted_repos(cls):
        """Make sure all blacklisted GitHub repos have an entry in the DB
        marking them as such.
        """
        for owner_repo in cls._BLACKLISTED_GITHUB_REPOS:
            owner, repo_name = owner_repo.split('/')
            cls.upsert_with_owner_repo({
                'owner': owner,
                'repo_name': repo_name,
                'is_blacklisted': True,
            })

    @classmethod
    def upsert_with_owner_repo(cls, repo):
        """Insert or update a row using (owner, repo_name) as the key.

        Returns True if a new row was inserted.
        """
        owner = repo['owner']
        repo_name = repo['repo_name']

        assert owner
        assert repo_name

        query = r.table(cls._TABLE_NAME).get_all([owner, repo_name],
                index='owner_repo')
        db_repo = db.util.get_first(query)

        if db_repo is None:
            repo_to_insert = dict(cls._ROW_SCHEMA, **repo)
            r.table(cls._TABLE_NAME).insert(repo_to_insert).run(r_conn())
            return True
        else:
            query.update(repo).run(r_conn())
            return False


class PluginGithubRepos(GithubRepos):
    """GitHub repositories of Vim plugins."""

    _TABLE_NAME = 'plugin_github_repos'

    _ROW_SCHEMA = dict(GithubRepos._ROW_SCHEMA, **{

        # IDs of vim.org scripts where this repo was mentioned
        'from_vim_scripts': [],

    })

    # GitHub repos that are not Vim plugins that we've manually found.
    # TODO(david): We should probably have some heuristic to test if a repo is
    #     actually a vim plugin... there's a bunch of repos referenced from
    #     vim.org descrptions that are not vim plugins.
    # TODO(david): Make it easy to post-blacklist a plugin that we discover on
    #     the live site.
    _BLACKLISTED_GITHUB_REPOS = set([
        'github/gitignore',
        'kablamo/dotfiles',
        'aemoncannon/ensime',
        'experiment/vim',
        'ggreer/the_silver_searcher',
        'pry/pry',
        'sitaramc/gitolite',
        'sstephenson/bats',
    ])
