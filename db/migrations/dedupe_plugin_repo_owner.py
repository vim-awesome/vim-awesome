"""Remove case-sensitive duplicates in the plugins table"""

import rethinkdb as r

import db.plugins
import db.util

r_conn = db.util.r_conn

LOG_FILE = 'deleted_slugs.log'


def dupe_log_line(canonical, dupes):
    return '%s: %s\n' % (canonical, ', '.join(dupes))


def merge_plugins(plugins):
    def reducer(new, old):

        # Use the plugin with the shortest slug as the new plugin
        if len(old['slug']) < len(new['slug']):
            new, old = old, new

        new = db.plugins.update_plugin(old, new)

        # Preserve categories
        if new['category'] == 'uncategorized':
            new['category'] = old['category']

        # Merge tags
        new['tags'] = list(set(new['tags'] + old['tags']))

        # Collect the total number of dotfiles referencing this plugin
        new['github_bundles'] += old['github_bundles']

        return new

    return reduce(reducer, plugins)

if __name__ == '__main__':
    print 'Removing duplicate rows in plugins. Logging to: %s' % LOG_FILE

    updated = 0
    deleted = 0

    query = r.table('plugins')

    # Group by the normalized GitHub path
    query = query.group([
        r.row['github_owner'].downcase(),
        r.row['github_repo_name'].downcase()])

    grouped_plugins = query.run(r_conn())

    slug_map = {}

    for owner_repo, plugins in grouped_plugins.iteritems():

        print '\nPlugin with GitHub path %s occurs %s times' % (
                owner_repo,
                len(plugins))

        canonical = merge_plugins(plugins)

        print "Using %s as canonical" % canonical['slug']

        # db.plugins.insert normalizes the ower/repo to lower case
        db.plugins.insert(canonical, conflict='replace')
        updated += 1

        dupes = [dupe for dupe in plugins if dupe['slug'] != canonical['slug']]
        if dupes:
            dupe_slugs = [dupe['slug'] for dupe in dupes]
            # Store deleted slugs for logging
            slug_map[canonical['slug']] = dupe_slugs
            print 'Deleting duplicates rows: %s' % ', '.join(dupe_slugs)
            r.table('plugins').get_all(r.args(dupe_slugs)).delete().run(r_conn())
            deleted += len(dupes)

    with open(LOG_FILE, 'w') as log:
        print 'Writing deleted slug names to %s' % LOG_FILE
        log.writelines(dupe_log_line(c, d) for c, d in slug_map.iteritems())

    print "Updated %d rows and deleted %d" % (updated, deleted)
