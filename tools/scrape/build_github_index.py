"""Build an index (DB table) of known GitHub repositories of Vim plugins."""

import argparse
import collections
import logging
import re

import rethinkdb as r

import db.util
from db.github_repos import PluginGithubRepos

r_conn = db.util.r_conn


# Matches eg. "github.com/scrooloose/syntastic", "github.com/kien/ctrlp.vim"
# TODO(david): Debug why this overmatches "1155063 ... [extra cruft]" and
#     "steveno) ..." and "3278077 ..."
_GITHUB_REPO_URL_PATTERN = re.compile(
        r'github\.com/[^/]+/[\d\w\.\%\+\-\=\:\|\~]+\b', re.IGNORECASE)


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

    return True


def _extract_github_repo_urls(text):
    """Extracts URLs of GitHub repositories from a string of text."""
    matches = _GITHUB_REPO_URL_PATTERN.findall(text)
    normalized_matches = map(_normalize_github_url, matches)
    return filter(_is_github_url_allowed, normalized_matches)


def get_repos_from_vimorg_descriptions():
    """Extract URLs of GitHub repos from the long descriptions on vim.org."""
    print "Discovering GitHub repos from vim.org long descriptions ..."

    # A map of repo URL to the vimorg_ids they were found in.
    repo_urls_dict = collections.defaultdict(set)

    all_plugins = r.table('plugins').run(r_conn())
    for plugin in all_plugins:
        for field in ['vimorg_long_desc', 'vimorg_install_details']:
            if field in plugin and plugin[field]:
                repo_urls = set(_extract_github_repo_urls(plugin[field]))
                vimorg_id = plugin['vimorg_id']
                assert vimorg_id
                for repo_url in repo_urls:
                    repo_urls_dict[repo_url].add(vimorg_id)

    num_inserted = 0
    for repo_url, vimorg_ids in repo_urls_dict.iteritems():
        _, owner, repo_name = repo_url.split('/')
        inserted = PluginGithubRepos.upsert_with_owner_repo({
            'owner': owner,
            'repo_name': repo_name,
            'from_vim_scripts': list(vimorg_ids),
        })
        num_inserted += int(inserted)

    print "Found %s GitHub repos; inserted %s new ones." % (
            len(repo_urls_dict), num_inserted)


def aggregate_repos_from_dotfiles():
    """Aggregate plugin references scraped from dotfiles repos on GitHub.

    Adds newly-discovered GitHub repos of plugins and also updates each GitHub
    plugin repo with the number of plugin manager users. Prints out some stats
    at the end.
    """
    # Counter of how many users for each of Pathogen/Vundle/NeoBundle.
    users_counter = collections.Counter()

    # Counter of how many times a repo occurs.
    repos_counter = collections.Counter()

    # Counter of total bundles for each of Pathogen/Vundle/NeoBundle.
    manager_counter = collections.Counter()

    # Map of plugin manager name to column name in dotfiles_github_repos table.
    managers = {
        'vundle': 'vundle_repos',
        'pathogen': 'pathogen_repos',
        'neobundle': 'neobundle_repos',
    }

    query = r.table('dotfiles_github_repos').pluck(managers.values())
    all_dotfiles = query.run(r_conn())

    for dotfiles_repo in all_dotfiles:
        for manager, field in managers.iteritems():
            plugin_repos = dotfiles_repo[field]
            users_counter[manager] += 1 if plugin_repos else 0
            manager_counter[manager] += len(plugin_repos)

            for owner_repo in plugin_repos:
                repos_counter[owner_repo] += 1

    num_inserted = 0

    for owner_repo, num_users in repos_counter.iteritems():
        owner, repo_name = owner_repo.split('/')
        repo = {
            'owner': owner,
            'repo_name': repo_name,
            'plugin_manager_users': num_users,
        }

        newly_inserted = PluginGithubRepos.upsert_with_owner_repo(repo)
        num_inserted += int(newly_inserted)

    most_used_repos = '\n'.join(map(str, repos_counter.most_common(10)))
    print 'Most used plugins:', most_used_repos
    print 'Users per manager:', users_counter
    print 'Plugins per manager:', manager_counter
    print 'Dotfile repos scraped:', query.count().run(r_conn())
    print 'New plugin repos inserted:', num_inserted
    print 'Unique plugin bundles found:', len(repos_counter)
    print 'Total plugin bundles found:', sum(manager_counter.values())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    extract_fns = {
        "vim.org": get_repos_from_vimorg_descriptions,
        "dotfiles": aggregate_repos_from_dotfiles,
    }

    parser.add_argument("--source", "-s", choices=extract_fns.keys(),
            default="all", help="Source to extract from (default: all)")

    args = parser.parse_args()

    sources = extract_fns.keys() if args.source == "all" else [args.source]
    for source in sources:
        extract_fn = extract_fns[source]
        try:
            extract_fn()
        except Exception:
            logging.exception("build_github_index.py: error in %s " % (
                    extract_fn))
