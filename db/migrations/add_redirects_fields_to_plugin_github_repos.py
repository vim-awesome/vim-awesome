"""Adds the redirects_from and redirects_to fields to plugin github repos."""

import rethinkdb as r

import db.plugins
import db.util

r_conn = db.util.r_conn


if __name__ == '__main__':
    # TODO(david): Should only assign if fields are missing.
    r.table('plugin_github_repos').update(
            {'redirects_to': '', 'redirects_from': ''}).run(r_conn())
