import db.github_repos
import db.plugins
import db.tags


def ensure_tables_and_indices():
    db.plugins.create_table()
    db.tags.create_table()
    db.github_repos.create_table()


if __name__ == '__main__':
    ensure_tables_and_indices()
