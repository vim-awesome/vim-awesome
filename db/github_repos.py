"""A table of all known GitHub repos of vim plugins that we want to scrape."""

import time

import rethinkdb as r

import db.util

r_conn = db.util.r_conn


# TODO(david): Using a proper ODM to do inheritance, enforce constraints, and
#     ensure a schema would be really nice.
class GithubRepos(object):
    """Abstract base class of class methods to handle a table of GitHub
    repositories.
    """

    # Subclasses must override this.
    _TABLE_NAME = None

    # Fields we want to track for every GitHub repo. This can be extended with
    # extra fields for subclasses.
    _ROW_SCHEMA = {

        # GitHub's repo ID. Only unique with (owner, repo_name)
        'repo_id': '',

        # Last time this repo was scraped (Unix timestamp in seconds)
        'last_scraped_at': 0,

        # Number of times scraped
        'times_scraped': 0,

        # Whether this repo should not be used for fetching plugin data
        'is_blacklisted': False,

        # Raw repo data from GitHub API
        'repo_data': {},

        # Number of Vundle, Pathogen, NeoBundle, etc. users
        'plugin_manager_users': 0,

        # If this repo has been renamed, the "owner/repo_name" of the new
        # location of this repo
        'redirects_to': '',

        # If another repo redirects here, the "owner/repo_name" of that repo
        # TODO(david): This should be a list.
        'redirects_from': '',

    }

    # Override this with URLs that should not be scraped.
    _BLACKLISTED_GITHUB_REPOS = []

    @classmethod
    def ensure_table(cls):
        db.util.ensure_table(cls._TABLE_NAME)

        db.util.ensure_index(cls._TABLE_NAME, 'owner')
        db.util.ensure_index(cls._TABLE_NAME, 'repo_id')
        db.util.ensure_index(cls._TABLE_NAME, 'redirects_to')
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
    def get_with_owner_repo(cls, owner, repo_name):
        """Returns the repository with the given owner and repo_name."""
        assert owner
        assert repo_name

        query = r.table(cls._TABLE_NAME).get_all([owner, repo_name],
                index='owner_repo')
        return db.util.get_first(query)

    @classmethod
    def upsert_with_owner_repo(cls, repo):
        """Insert or update a row using (owner, repo_name) as the key.

        Returns True if a new row was inserted.
        """
        assert repo['owner']
        assert repo['repo_name']

        if repo.get('id'):
            db_repo = r.table(cls._TABLE_NAME).get(repo['id']).run(r_conn())
        else:
            db_repo = cls.get_with_owner_repo(repo['owner'], repo['repo_name'])

        if db_repo is None:
            repo_to_insert = dict(cls._ROW_SCHEMA, **repo)
            r.table(cls._TABLE_NAME).insert(repo_to_insert).run(r_conn())
            return True
        else:
            db_repo.update(repo)
            # TODO(david): Figure out if there's any difference between doing
            #     table().replace(db_repo), and if so, which is preferred.
            r.table(cls._TABLE_NAME).insert(db_repo, upsert=True).run(r_conn())
            return False

    @classmethod
    def log_scrape(cls, repo):
        """Update a repo's fields to note that it has just been scraped."""
        repo['last_scraped_at'] = int(time.time())
        repo['times_scraped'] = repo.get('times_scraped', 0) + 1


class PluginGithubRepos(GithubRepos):
    """GitHub repositories of Vim plugins."""

    _TABLE_NAME = 'plugin_github_repos'

    _ROW_SCHEMA = dict(GithubRepos._ROW_SCHEMA, **{

        # We don't generally care about scraping from forks.
        'is_fork': False,

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
        'git.wincent.com/command-t',
        'contrib/mpvim',
        'svn/trunk',

        # TODO(david): This repo actually contains a Vim plugin nested in
        #     https://github.com/mozilla/rust/tree/master/src/etc/vim, but
        #     showing the top-level repo and description ("a safe, concurrent,
        #     practical language") appears out of place, especially since it
        #     has about 3K stars. Figure out what to do with it. If we default
        #     sort by # of users instead of GitHub stars, we can probably
        #     un-blacklist this.
        'mozilla/rust',
    ])


class DotfilesGithubRepos(GithubRepos):
    """GitHub repositories of dotfiles (*nix config) repos."""

    _TABLE_NAME = 'dotfiles_github_repos'

    _ROW_SCHEMA = dict(GithubRepos._ROW_SCHEMA, **{

        # Last time this repo was pushed (Unix timestamp in seconds).
        'pushed_at': 0,

        # The keyword that was used to find this repo.
        'search_keyword': '',

        # References to GitHub plugin repos as strings. eg. "kien/ctrlp.vim"
        'vundle_repos': [],
        'neobundle_repos': [],
        'pathogen_repos': [],

    })

    @classmethod
    def ensure_table(cls):
        super(DotfilesGithubRepos, cls).ensure_table()
        db.util.ensure_index(cls._TABLE_NAME, 'search_keyword')
        db.util.ensure_index(cls._TABLE_NAME, 'pushed_at')

    @classmethod
    def get_latest_with_keyword(cls, search_keyword):
        # Looks like we can't chain a get_all with an order_by, so we can't use
        # the search_keyword index.
        query = (r.table(cls._TABLE_NAME)
                .order_by(index=r.desc('pushed_at'))
                .filter({'search_keyword': search_keyword}))
        return db.util.get_first(query)
