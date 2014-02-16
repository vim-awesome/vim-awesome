# TODO(david): Rename this file or just move into plugins.py.

import rethinkdb as r

import db.util
import db.plugins

r_conn = db.util.r_conn


class MultiplePluginsWithSameNormalizedNameError(Exception):
    pass


def _update_by_vim_script_id(plugin):
    """Try to update a plugin by the given vim.org script id.

    Returns whether it updated an existing plugin.
    """
    query = r.table('plugins').get_all(plugin['vim_script_id'],
            index='vim_script_id')
    db_plugin = db.util.get_first(query)
    return _update_db_plugin(db_plugin, plugin)


def _update_by_name(plugin, query_filter=None):
    """Attempts to update an existing plugin in our DB of the same or similar
    name as the given plugin.

    Returns whether it updated an existing plugin.
    """
    db_plugin = _find_by_similar_name(plugin['name'], query_filter)
    return _update_db_plugin(db_plugin, plugin)


def _update_db_plugin(db_plugin, plugin):
    """Updates an existing DB plugin with plugin.

    Returns whether db_plugin exists.
    """
    if db_plugin:
        updated_plugin = db.plugins.update_plugin(db_plugin, plugin)
        db.plugins.insert(updated_plugin, upsert=True)
        return True
    else:
        return False


# TODO(david): Need to write a unit test for this.
def _find_by_similar_name(name, query_filter=None):
    """Attempt to find a plugin by the given name in a filtered query.

    If an exact name match cannot be found, a plugin with a similar name will
    be returned if one can be found. For example, if name is "vim-powerline",
    that will match a plugin with the name "powerline" or "powerline.vim" if
    "vim-powerline" cannot be found.

    Raises an error if multiple plugins in the DB have the same normalized
    name.

    Arguments:
        name: The name to attempt to match.
        query_filter: An optional predicate to limit the set of plugins that we
            attempt to match on. Will be passed to Rethink's filter().
    """
    query_filter = {} if query_filter is None else query_filter

    # First, attempt an exact match.
    query = r.table('plugins').get_all(name, index='name').filter(query_filter)
    db_plugin = db.util.get_first(query)
    if db_plugin:
        return db_plugin

    # Attempt to match by normalized name: no .vim suffix or vim- prefix.
    # TODO(david): This can be optimized by caching the value of normalized
    #     name on the plugin document in the DB.
    name_regex = _get_normalized_name_regex(name)
    query = r.table('plugins').filter(query_filter).filter(
            lambda plugin: plugin['name'].match(name_regex))
    matches = list(query.run(r_conn()))
    num_matches = len(matches)

    # Ensure we have at most one match. Complain if there are multiple plugins
    # that have the same normalized name, because we don't know which plugin to
    # save to.
    if num_matches == 1:
        return matches[0]
    elif num_matches > 1:
        plugin_names = [plugin['name'] for plugin in matches]
        raise MultiplePluginsWithSameNormalizedNameError(
                "Uh oh, %s plugins match the regex %s: %s" % (
                num_matches, name_regex, plugin_names))
    else:
        return None


def upsert_plugin(plugin, query_filter=None):
    """Update or insert the given plugin into the DB."""

    # Try to update an existing plugin in the DB first.
    updated = False

    if plugin['vim_script_id']:
        updated = _update_by_vim_script_id(plugin)

    # TODO(david): We need a better way of handling name collisions than just
    #     throwing an exception, catching it later, and logging it.
    if not updated and plugin['name']:

        # Attempt to update by matching against a filtered set of plugins.
        updated = _update_by_name(plugin, query_filter)

        # That didn't work, so try matching against the global set.
        if not updated and query_filter is not None:
            updated = _update_by_name(plugin)

    # If we didn't update an existing plugin, insert a new row.
    if not updated:
        db.plugins.insert(plugin)
