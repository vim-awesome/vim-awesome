import db.github_repos
import db.plugins
import db.tags


def ensure_tables_and_indices():
    db.plugins.ensure_table()
    db.tags.ensure_table()
    db.github_repos.PluginGithubRepos.ensure_table()
    db.github_repos.DotfilesGithubRepos.ensure_table()


if __name__ == '__main__':
    ensure_tables_and_indices()
