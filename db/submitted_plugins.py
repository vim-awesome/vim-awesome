"""Utility functions for the submitted plugins table."""

import time

import rethinkdb as r

import db

r_conn = db.util.r_conn


def ensure_table():
    db.util.ensure_table('submitted_plugins')
    db.util.ensure_index('submitted_plugins', 'submitted_at')


def insert(plugin_data):
    if not plugin_data.get('submitted_at'):
        plugin_data['submitted_at'] = int(time.time())

    r.table('submitted_plugins').insert(plugin_data).run(r_conn())
