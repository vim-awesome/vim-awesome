# Paths are relative to $HOME

pythonpath = 'vim-awesome/web'

pidfile = '.gunicorn.pid'

daemon = True

accesslog = 'logs/gunicorn/access.log'
errorlog = 'logs/gunicorn/error.log'

# Recommendation is 2 * NUM_CORES + 1. See
# http://gunicorn-docs.readthedocs.org/en/latest/design.html#how-many-workers
workers = 12
