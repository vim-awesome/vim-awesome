"""Adds the vimplug_repos fields to plugin dotfiles github repos."""

import rethinkdb as r

import db.util

r_conn = db.util.r_conn


if __name__ == '__main__':
    # TODO(jeldredge): Should only assign if fields are missing.
    r.table('dotfiles_github_repos').update({'vimplug_repos': []}).run(r_conn())
