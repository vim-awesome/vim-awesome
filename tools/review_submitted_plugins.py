"""Interactively review user-submitted plugins to add to our DB.

Will display a user submission and ask if it should be inserted. If yes, will
insert, else, will record it was rejected.

Will only present plugins that we don't already know about and were not
previously rejected. Deletes any empty submissions.
"""

import json
import re
import sys

import rethinkdb as r

import db.github_repos
import db.util
import util

r_conn = db.util.r_conn


_GITHUB_LINK_REGEX = re.compile(r'github.com/(.*?)/([^/?#]*)')


# From http://stackoverflow.com/a/3041990
def _query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


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


def review_vimorg_submission(submission):
    """Prompts whether to insert data about a plugin with a vimorg_id.

    Displays info about that submission, and displays an interactive prompt
    whether to add submitted data about it. If no, will add a field to the
    submission that it was rejected. If yes, will make the submission data
    searchable by adding a vimorg_id field so that data from it can be added
    when scraping vim.org plugins.
    """
    print
    print json.dumps(submission, indent=2)

    if not _query_yes_no("Add info about this vim.org submission?"):
        submission['rejected'] = True
        r.table('submitted_plugins').insert(submission,
                conflict='replace').run(r_conn())
        return

    print "Ok, will update from this submission data on next vim.org scrape"
    vimorg_id = util.get_vimorg_id_from_url(submission['vimorg-link'])
    submission['vimorg_id'] = vimorg_id
    r.table('submitted_plugins').insert(submission,
            conflict='replace').run(r_conn())


def review_github_submission(submission, repo_owner, repo_name):
    """Prompts whether to insert a GitHub-sourced plugin submission.

    Displays info about that submission, and displays an interactive prompt
    whether to insert or not. If no, will add a field to the submission that it
    was rejected. If yes, will insert a new row into the plugin_github_repos
    table.
    """
    print
    print json.dumps(submission, indent=2)
    # It'd be nice to webbrowser.open(submission['github-link']) here, but this
    # needs to work ssh'ed

    if not _query_yes_no("Add this GitHub submission?"):
        submission['rejected'] = True
        r.table('submitted_plugins').insert(submission,
                conflict='replace').run(r_conn())
        return

    print "Ok, inserting new GitHub-sourced plugin %s/%s" % (repo_owner,
            repo_name)
    db.github_repos.PluginGithubRepos.upsert_with_owner_repo({
        'owner': repo_owner,
        'repo_name': repo_name,
        'from_submission': submission,
    })


def main():
    delete_empty_submissions()

    rejected_plugins = []
    known_github_plugins = []
    new_github_plugins = []
    known_vimorg_plugins = []
    new_vimorg_plugins = []
    unparseable_plugins = []

    submissions = r.table('submitted_plugins').run(r_conn())
    for submission in submissions:
        if submission.get('rejected'):
            rejected_plugins.append(submission)
            continue

        if submission['vimorg-link']:
            if submission.get('vimorg_id'):
                known_vimorg_plugins.append(submission)
            else:
                new_vimorg_plugins.append(submission)
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
                new_github_plugins.append((submission, repo_owner, repo_name))

    # TODO(david): Don't discard data about known vim.org plugins. That can be
    #     used to associate vim.org plugins with their GitHub repos.
    print
    print '%s submissions were previously rejected' % len(rejected_plugins)
    print '%s submissions are known vim.org plugins' % len(
            known_vimorg_plugins)

    # Update vim.org submissions with the vimorg_id for easy searching.
    print '%s submissions are new vim.org plugins' % len(new_vimorg_plugins)
    for submission in new_vimorg_plugins:
        review_vimorg_submission(submission)

    print '%s submissions are known github.com plugins' % len(
            known_github_plugins)

    print
    print '%s submissions have unparseable github.com links:' % len(
            unparseable_plugins)
    for submission in unparseable_plugins:
        print submission

    print
    print '%s submissions are new GitHub-sourced plugins:' % len(
            new_github_plugins)
    for submission, repo_owner, repo_name in new_github_plugins:
        review_github_submission(submission, repo_owner, repo_name)


if __name__ == '__main__':
    main()
