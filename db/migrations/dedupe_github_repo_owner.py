"""Remove case-sensitive duplicates in GitHub repository tables"""

import rethinkdb as r

import db.plugins
import db.util

r_conn = db.util.r_conn


if __name__ == '__main__':
    table = 'plugin_github_repos'

    print 'Removing duplicate rows in %s' % table

    updated = 0
    deleted = 0

    query = r.table(table)

    # Group by the normalized GitHub path
    query = query.group([
        r.row['owner'].downcase(),
        r.row['repo_name'].downcase()])

    # Get the most recently scraped row in each group first
    query = query.order_by(r.desc('last_scaped_at'))

    grouped_repos = query.run(r_conn())

    for owner_repo, repos in grouped_repos.iteritems():

        print '\nRepo with GitHub path %s occurs %s times' % (
                owner_repo,
                len(repos))

        # Use the most recently scraped row as the canonical row
        canonical = repos.pop()

        assert canonical
        print 'Using %s as the canoncial row' % canonical['id']

        canonical_owner_repo = (canonical['owner'], canonical['repo_name'])

        if canonical_owner_repo != owner_repo:
            print "Normalizing %s to %s for our canonical row" % (
                    canonical_owner_repo,
                    owner_repo)

            r.table(table).get(canonical['id']).update({
                'owner': canonical['owner'].lower(),
                'repo_name': canonical['repo_name'].lower()}).run(r_conn())
            updated += 1

        if repos:
            dupe_ids = [dupe['id'] for dupe in repos]
            print 'Deleting duplicates rows: %s' % ', '.join(dupe_ids)
            r.table(table).get_all(r.args(dupe_ids)).delete().run(r_conn())
            deleted += len(repos)

    print "Updated %d rows and deleted %d" % (updated, deleted)
