import rethinkdb as r

import db.util
import db.plugins


class InvalidPluginError(Exception):
    pass


def try_update(conn, plugin, attrib):
    """Try to update a plugin based on a given attribute.

    Returns whether it updated an existing plugin.
    """
    if attrib == 'vim_script_id':
        query = r.table('plugins').get_all(plugin['vim_script_id'],
                index='vim_script_id')
    else:
        query = r.table('plugins').filter(lambda p: p.contains(attrib) &
                (p[attrib] == plugin[attrib]))

    db_plugin = db.util.get_first(query)

    if db_plugin:
        updated_plugin = db.plugins.update_plugin(db_plugin, plugin)
        query.update(updated_plugin).run(conn)
        return True
    else:
        return False


def upsert_plugin(conn, plugin):
    """Upsert a plugin into a database"""
    # Try to update based on existing keys
    if plugin['vim_script_id']:
        if try_update(conn, plugin, 'vim_script_id'):
            return
    elif plugin['github_url']:
        if try_update(conn, plugin, 'github_url'):
            return
    else:
        raise InvalidPluginError(
            "Attempting to insert a plugin with no identifying information")

    # Otherwise, insert the plugin
    plugin.setdefault('tags', [])
    r.table('plugins').insert(plugin).run(conn)
