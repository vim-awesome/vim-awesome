import base64
import re
import sys
import time

import dateutil.parser
import requests
import rethinkdb as r
from termcolor import cprint

import db.util
import tools.scrape.db_upsert as db_upsert
import util

r_conn = db.util.r_conn

try:
    import secrets
    _GITHUB_API_TOKEN = getattr(secrets, 'GITHUB_PERSONAL_ACCESS_TOKEN', None)
except ImportError:
    _GITHUB_API_TOKEN = None


_NO_GITHUB_API_TOKEN_MESSAGE = """
*******************************************************************************
* Warning: GitHub API token not found in secrets.py. Scraping will be severely
* rate-limited. See secrets.py.example to obtain a GitHub personal access token
*******************************************************************************
"""
if not _GITHUB_API_TOKEN:
    cprint(_NO_GITHUB_API_TOKEN_MESSAGE, 'red')


def get_api_page(path, page=1, per_page=100):
    """Get a page from the github API"""
    url = 'https://api.github.com/%s?page=%s&per_page=%s' % (path, page,
            per_page)

    if _GITHUB_API_TOKEN:
        url += '&access_token=%s' % _GITHUB_API_TOKEN

    res = requests.get(url)
    return res, res.json()


def fetch_plugin(owner, repo, repo_data=None, readme_data=None):
    """Fetch a plugin from a github repo"""
    if not repo_data:
        res, repo_data = get_api_page('repos/%s/%s' % (owner, repo))
        if res.status_code == 404:
            return None, repo_data

    if not readme_data:
        _, readme_data = get_api_page('repos/%s/%s/readme' % (owner, repo))

    readme_base64_decoded = base64.b64decode(readme_data.get('content', ''))
    readme = unicode(readme_base64_decoded, 'utf-8', errors='ignore')

    vim_script_id = None
    homepage = repo_data['homepage']

    if homepage and homepage.startswith('http://www.vim.org/scripts/'):
        vim_script_url = homepage
        match = re.search('script_id=(\d+)', vim_script_url)
        if match:
            vim_script_id = int(match.group(1))

    repo_created_date = dateutil.parser.parse(repo_data['created_at'])

    # Fetch commits so we can get the update/create dates.
    _, commits_data = get_api_page('repos/%s/%s/commits' % (owner, repo),
            per_page=100)

    if commits_data and isinstance(commits_data, list) and len(commits_data):

        # Unfortunately repo_data['updated_at'] and repo_data['pushed_at'] are
        # wildy misrepresentative of the last time someone made a commit to the
        # repo.
        updated_date_text = commits_data[0]['commit']['author']['date']
        updated_date = dateutil.parser.parse(updated_date_text)

        # To get the creation date, we use the heuristic of min(repo creation
        # date, 100th latest commit date). We do this because repo creation
        # date can be later than the date of the first commit, which is
        # particularly pervasive for vim-scripts repos. Fortunately, most
        # vim-scripts repos don't have more than 100 commits, and also we get
        # creation_date for vim-scripts repos when scraping vim.org.
        early_commit_date_text = commits_data[-1]['commit']['author']['date']
        early_commit_date = dateutil.parser.parse(early_commit_date_text)
        created_date = min(repo_created_date, early_commit_date)

    else:
        updated_date = dateutil.parser.parse(repo_data['updated_at'])
        created_date = repo_created_date

    return ({
        'name': repo,
        'github_url': repo_data['html_url'],
        'vim_script_id': vim_script_id,
        'homepage': homepage,
        'github_stars': repo_data['watchers'],
        'github_short_desc': repo_data['description'],
        'github_readme': readme,
        'created_at': util.to_timestamp(created_date),
        'updated_at': util.to_timestamp(updated_date),
    }, repo_data)


def get_requests_left():
    """Retrieve how many API requests are remaining"""
    _, data = get_api_page('rate_limit')

    return data['rate']['remaining']


def scrape_repos(num):
    """Scrapes the num repos that have been least recently scraped."""
    query = r.table('github_repos').filter({'is_blacklisted': False})
    query = query.order_by('last_scraped_at').limit(num)
    repos = query.run(r_conn())

    # TODO(david): Print stats at the end: # successfully scraped, # not found,
    #     # redirects, etc.
    for repo in repos:
        repo_name = repo['repo_name']
        repo_owner = repo['owner']

        # Print w/o newline.
        print "    scraping %s/%s ..." % (repo_owner, repo_name),
        sys.stdout.flush()

        # TODO(david): One optimization is to pass in repo['repo_data'] for
        #     vim-scripts repos (since we already save that when discovering
        #     vim-scripts repos in build_github_index.py). But the
        #     implementation here should not be coupled with implemenation
        #     details in build_github_index.py.
        plugin, repo_data = fetch_plugin(repo_owner, repo_name)

        repo['last_scraped_at'] = int(time.time())
        repo['repo_data'] = repo_data
        repo['times_scraped'] += 1
        r.table('github_repos').insert(repo, upsert=True).run(r_conn())

        if plugin:

            # If this plugin's repo was mentioned in vim.org script
            # descriptions, try to see if this plugin matches any of those
            # scripts before a global search.
            query_filter = None
            if repo.get('from_vim_scripts'):
                vim_script_ids = repo['from_vim_scripts']
                query_filter = (lambda plugin:
                        plugin['vim_script_id'] in vim_script_ids)

            # TODO(david): We should probably still wrap this in a try block.
            db_upsert.upsert_plugin(plugin, query_filter)

            print "done"

        else:
            # TODO(david): Insert some metadata in the github repo that this is
            #     not found
            print "not found."
            continue
