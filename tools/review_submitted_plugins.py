"""Prints out submitted plugins that we don't already know about.

Also deletes any empty submissions.
"""

import json
import re

import rethinkdb as r

import db.github_repos
import db.util

r_conn = db.util.r_conn


_GITHUB_LINK_REGEX = re.compile(r'github.com/(.*?)/([^/?#]*)')


def delete_empty_submissions():
    """Delete submitted plugins that don't have enough info for us to act on.

    Since we have no form validation, many submissions are just people who
    click the "submit" button.
    """
    deleted = r.table('submitted_plugins').filter({
        'name': '',
        'author': '',
        'github-link': '',
        'vimorg-link': '',
    }).delete().run(r_conn())

    print 'Deleted empty submissions:'
    print deleted


def main():
    delete_empty_submissions()

    known_vimorg_plugins = []
    known_github_plugins = []
    new_plugins = []
    unparseable_plugins = []

    submissions = r.table('submitted_plugins').run(r_conn())
    for submission in submissions:
        if submission['vimorg-link']:
            known_vimorg_plugins.append(submission)
            continue

        github_link = submission['github-link']
        if github_link:
            matches = _GITHUB_LINK_REGEX.findall(github_link)
            if not matches:
                unparseable_plugins.append(submission)
                continue

            repo_owner, repo_name = matches[0]
            db_repo = db.github_repos.PluginGithubRepos.get_with_owner_repo(
                    repo_owner, repo_name)

            if db_repo:
                known_github_plugins.append(submission)
            else:
                new_plugins.append(submission)

    print
    print '%s submissions are known vim.org plugins' % len(
            known_vimorg_plugins)
    print '%s submissions are known github.com plugins' % len(
            known_github_plugins)

    print
    print '%s submissions have unparseable github.com links:' % len(
            unparseable_plugins)
    for submission in unparseable_plugins:
        print submission

    print
    print '%s submissions are new plugins:' % len(new_plugins)
    for submission in new_plugins:
        print json.dumps(submission, indent=2)


if __name__ == '__main__':
    main()
