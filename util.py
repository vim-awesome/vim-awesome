import rethinkdb as r

# TODO(alpert): Read port and db from app.config?
def r_conn(box=[None]):
    if box[0] is None:
        box[0] = r.connect()
        box[0].use('vim_awesome')
    return box[0]

def db_get_first(query):
    results = list(query.run(r_conn()))
    return results[0] if results else None

# TODO(david): Move all this db-related stuff to the db package?
def db_create_table(table_name):
    """Creates a table if it doesn't exist."""
    try:
        r.table_create(table_name).run(r_conn())
    except r.RqlRuntimeError:
        pass  # Ignore db already created

def api_not_found(message):
    return (message, 404)
