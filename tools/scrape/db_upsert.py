import rethinkdb as r


class DuplicatePluginError(Exception):
    pass


class InvalidPluginError(Exception):
    pass


def try_update(conn, plugin, attrib):
    """Try to update a plugin based on a given attribute"""
    script_filter = (lambda p: p.contains(attrib) &
        (p[attrib] == plugin[attrib]))
    num_results = (r.table('plugins')
                    .filter(script_filter)
                    .count()
                    .run(conn))
    if num_results == 1:
        (r.table('plugins')
          .filter(script_filter)
          .update(plugin)
          .run(conn))
        return
    elif num_results > 1:
        raise DuplicatePluginError("Duplicate plugin with attrib: " + attrib)


def upsert_plugin(conn, plugin):
    """Upsert a plugin into a database"""
    # Try to update based on existing keys
    if plugin['vim_script_id']:
        try_update(conn, plugin, 'vim_script_id')
    elif plugin['github_url']:
        try_update(conn, plugin, 'github_url')
    else:
        raise InvalidPluginError(
            "Attempting to insert a plugin with no identifying information")

    # Otherwise, insert the plugin
    r.table('plugins').insert(plugin).run(conn)
