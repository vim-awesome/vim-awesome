"""Build an index (DB table) of known GitHub repositories of Vim plugins."""

import re

import rethinkdb as r

import db

r_conn = db.util.r_conn


# Matches eg. "github.com/scrooloose/syntastic", "github.com/kien/ctrlp.vim"
_GITHUB_REPO_URL_PATTERN = re.compile(
        r'github\.com/[^/]+/[\d\w\.\%\+\-\=\:\|\~]+\b', re.IGNORECASE)

# GitHub URLs that are not repos of Vim plugins that we've manually found.
# TODO(david): This could alternatively be a dynamic blacklist by having an
#     is_blacklisted property in the GitHub repos index table instead of
#     hardcoded here.
_BLACKLISTED_GITHUB_URLS = set([
    'github.com/github/gitignore',
    'github.com/kablamo/dotfiles',
    'github.com/aemoncannon/ensime',
    'github.com/experiment/vim',
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


def extract_repos_from_vimorg_descriptions():
    """Extract URLs of GitHub repos from the long descriptions on vim.org."""
    repo_urls = set()

    all_plugins = r.table('plugins').filter({}).run(r_conn())
    for plugin in all_plugins:
        for field in ['vimorg_long_desc', 'vimorg_install_details']:
            if field in plugin:
                repo_urls |= set(_extract_github_repo_urls(plugin[field]))

    # TODO(david): This is still WIP. This just prints out a set of GitHub URLs
    #     we find from vim.org long descriptions for now.
    print '\n'.join(str(url) for url in repo_urls)


if __name__ == '__main__':
    extract_repos_from_vimorg_descriptions()
