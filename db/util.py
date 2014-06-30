import rethinkdb as r


# TODO(alpert): Read port and db from app.config?
def r_conn(box=[None]):
    if box[0] is None:
        box[0] = r.connect()
        box[0].use('vim_awesome')
    return box[0]


def get_first(query):
    results = list(query.limit(1).run(r_conn()))
    return results[0] if results else None


def ensure_db(db_name, *args, **kwargs):
    """Creates a DB if it doesn't exist."""
    conn = r.connect()

    try:
        r.db_create(db_name, *args, **kwargs).run(conn)
    except r.RqlRuntimeError:
        pass  # Ignore DB already created


def ensure_table(table_name, *args, **kwargs):
    """Creates a table if it doesn't exist."""
    try:
        r.table_create(table_name, *args, **kwargs).run(r_conn())
    except r.RqlRuntimeError:
        pass  # Ignore table already created


def ensure_index(table_name, index_name, *args, **kwargs):
    """Creates an index if it doesn't exist."""
    indices = r.table(table_name).index_list().run(r_conn())
    if index_name not in indices:
        r.table(table_name).index_create(index_name, *args, **kwargs).run(
                r_conn())
