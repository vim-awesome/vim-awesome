"""Build an index (DB table) of known GitHub repositories of Vim plugins."""

import argparse
import logging
import re

import rethinkdb as r

import db.util
import db.github_repos
from tools.scrape.github import get_api_page

r_conn = db.util.r_conn


# Matches eg. "github.com/scrooloose/syntastic", "github.com/kien/ctrlp.vim"
_GITHUB_REPO_URL_PATTERN = re.compile(
        r'github\.com/[^/]+/[\d\w\.\%\+\-\=\:\|\~]+\b', re.IGNORECASE)

# GitHub URLs that are not repos of Vim plugins that we've manually found.
# TODO(david): This could alternatively be a dynamic blacklist by having an
#     is_blacklisted property in the GitHub repos index table instead of
#     hardcoded here.
# TODO(david): We should probably have some heuristic to test if a repo is
#     actually a vim plugin... there's a bunch of repos referenced from vim.org
#     descrptions that are not vim plugins.
_BLACKLISTED_GITHUB_URLS = set([
    'github.com/github/gitignore',
    'github.com/kablamo/dotfiles',
    'github.com/aemoncannon/ensime',
    'github.com/experiment/vim',
    'github.com/ggreer/the_silver_searcher',
    'github.com/pry/pry',
    'github.com/sitaramc/gitolite',
])


def _normalize_github_url(url):
    """Normalize a GitHub url so that there is one unique URL representation
    per repo.
    """
    url = re.sub(r'\.git$', '', url)  # Strip trailing .git
    url = re.sub(r'\.$', '', url)  # Strip trailing period
    return url.lower()


def _is_github_url_allowed(url):
    """Whether this is a possible well-formed URL of a GitHub repo that we want
    to index.
    """
    parts = url.split('/')

    # TODO(david): Need to figure out a way to identify whether the github repo
    #     is a vim plugin or not

    # Disallow malformed repo URLs.
    if len(parts) != 3 or len(parts[2]) < 1 or parts[2] == '\\':
        return False

    # We don't want links to vim-scripts.
    if parts[1] == 'vim-scripts':
        return False

    # GitHub static assets are not GitHub repos.
    if parts[1] == 'assets':
        return False

    if url in _BLACKLISTED_GITHUB_URLS:
        return False

    return True


def _extract_github_repo_urls(text):
    """Extracts URLs of GitHub repositories from a string of text."""
    matches = _GITHUB_REPO_URL_PATTERN.findall(text)
    normalized_matches = map(_normalize_github_url, matches)
    return filter(_is_github_url_allowed, normalized_matches)


def get_repos_from_vimorg_descriptions():
    """Extract URLs of GitHub repos from the long descriptions on vim.org."""
    print "Discovering GitHub repos from vim.org long descriptions ..."

    repo_urls = set()

    all_plugins = r.table('plugins').filter({}).run(r_conn())
    for plugin in all_plugins:
        for field in ['vimorg_long_desc', 'vimorg_install_details']:
            if field in plugin:
                repo_urls |= set(_extract_github_repo_urls(plugin[field]))

    num_inserted = 0
    for repo_url in repo_urls:
        _, owner, repo_name = repo_url.split('/')
        if db.github_repos.upsert_with_owner_repo(owner, repo_name):
            num_inserted += 1

    print "Found %s GitHub repos; inserted %s of which are new." % (
            len(repo_urls), num_inserted)


def get_vim_scripts_repos():
    """Retrieve all of the repos from the vim-scripts GitHub user."""
    print "Discovering repositories from https://github.com/vim-scripts ..."
    _, user_data = get_api_page('users/vim-scripts')

    # Calculate how many pages of repositories there are.
    num_repos = user_data['public_repos']
    num_pages = (num_repos + 99) / 100  # ceil(num_repos / 100.0)

    num_inserted = 0

    for page in range(num_pages):
        _, repos_data = get_api_page('users/vim-scripts/repos',
                page=(page + 1))

        for repo_data in repos_data:
            if db.github_repos.upsert_with_owner_repo('vim-scripts',
                    repo_data['name'], repo_data):
                num_inserted += 1

    print ("Found %s vim-scripts GitHub repos; "
            "inserted %s of which are new." % (num_repos, num_inserted))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    extract_fns = {
        "vim.org": get_repos_from_vimorg_descriptions,
        "vim-scripts": get_vim_scripts_repos,
    }

    parser.add_argument("--source", "-s", choices=extract_fns.keys(),
            default="all", help="Source to extract from (default: all)")

    args = parser.parse_args()

    sources = extract_fns.keys() if args.source == "all" else [args.source]
    for source in sources:
        extract_fn = extract_fns[source]
        try:
            extract_fn()
        except:
            logging.exception("build_github_index.py: error in %s " % (
                    extract_fn))
