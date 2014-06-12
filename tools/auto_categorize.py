"""This script automatically categorizes plugins from their tags.

It is conservative and will not categorize if there is any ambiguity. Also
refuses to overwrite plugin categories, and is thus idempotent.
"""

import rethinkdb as r

import db.plugins
import db.util

r_conn = db.util.r_conn


_CATEGORY_TAGS_MAP = {
    'completion': ['autocomplete', 'snippets', 'delimiters', 'brackets',
            'pairings', 'pairs', 'parentheses', 'quotes'],
    'language': ['python', 'html', 'html5', 'xml', 'ruby', 'css', 'clojure',
            'javascript', 'c', 'c++', 'jade', 'editorconfig', 'bundler',
            'coffeescript', 'css3', 'go', 'haml', 'less', 'handlebars', 'sass',
            'cucumber', 'markdown', 'rails', 'rake', 'react', 'scala', 'scss',
            'slim'],
    'integration': ['integration', 'lint', 'tmux', 'unix', 'pep8', 'pyflakes',
            'dash', 'ack', 'grep', 'git', 'linux', 'diff', 'filesystem',
            'github', 'gist', 'mercurial', 'phabricator', 'arcanist', 'ctags'],
    'code-display': ['color-scheme', 'rainbow', 'alignment', 'indent',
            'levels'],
    'interface': ['interface', 'unite', 'nerdtree', 'window', 'buffer',
            'gutter', 'reference', 'docs', 'undo', 'tree', 'status',
            'statusline', 'file', 'fuzzy', 'finder', 'search', 'mru', 'tags',
            'browser', 'navigation', 'explorer'],
    'command': ['increment', 'decrement', 'substitute', 'comment',
            'text-object', 'movement', 'replace', 'yank', 'selection',
            'command', 'run'],
    'other': ['library', 'utility', 'defaults', 'history', 'manager', 'plugin',
            'package'],
}


def main():
    query = r.table('plugins').pluck('slug', 'category', 'tags')
    tags_without_categories = set()
    has_category_count = 0
    has_no_tags_count = 0
    zero_categories_count = 0
    multiple_categories_count = 0
    categorized_count = 0
    tag_category_map = {v:k for k in _CATEGORY_TAGS_MAP
            for v in _CATEGORY_TAGS_MAP[k]}

    for plugin in query.run(r_conn()):
        if plugin['category'] != 'uncategorized':
            has_category_count += 1
            continue

        if not plugin['tags']:
            has_no_tags_count += 1
            continue

        categories = set(tag_category_map[t] for t in plugin['tags'] if t in
                tag_category_map)
        tags_without_categories |= set(t for t in plugin['tags'] if t not in
                tag_category_map)

        if len(categories) == 0:
            print 'Plugin %s with tags %s cannot be categorized.' % (
                    plugin['slug'], plugin['tags'])
            zero_categories_count += 1
        elif len(categories) > 1:
            print('Multiple possible categories for plugin %s (tags %s): %s' %
                    (plugin['slug'], plugin['tags'], categories))
            multiple_categories_count += 1
        else:
            plugin_category = categories.pop()
            plugin['category'] = plugin_category
            print 'Plugin %s (tags %s) categorized as %s' % (
                    plugin['slug'], plugin['tags'], plugin_category)
            categorized_count += 1
            r.table('plugins').update(plugin).run(r_conn())

    print
    print '%s plugins successfully categorized' % categorized_count
    print '%s plugins had uncategorizable tags' % zero_categories_count
    print '%s plugins had multiple categories' % multiple_categories_count
    print '%s plugins were already categorized' % has_category_count
    print '%s plugins had no tags' % has_no_tags_count
    print 'Tags that do not belong to any category: %s' % (
            tags_without_categories)


if __name__ == '__main__':
    main()
