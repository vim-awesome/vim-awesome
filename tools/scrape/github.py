import base64
import re

import dateutil.parser
import requests
import rethinkdb as r
from termcolor import cprint

import db.util
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
    return res.headers, res.json()


def fetch_plugin(owner, repo, repo_data=None, readme_data=None):
    """Fetch a plugin from a github repo"""
    if not repo_data:
        _, repo_data = get_api_page('repos/%s/%s' % (owner, repo))
    if not readme_data:
        _, readme_data = get_api_page('repos/%s/%s/readme' % (owner, repo))

    vim_script_id = None
    homepage = None

    if repo_data['homepage'].startswith('http://www.vim.org/scripts/'):
        vim_script_url = repo_data['homepage']
        match = re.search('script_id=(\d+)', vim_script_url)
        if match:
            vim_script_id = int(match.group(1))
    else:
        homepage = repo_data['homepage']

    # Fetch commits so we can get the update/create dates. Unfortunately
    # repo_data['updated_at'] and repo_data['pushed_at'] are wildy
    # misrepresentative of the last time someone made a commit to the repo.
    _, commits_data = get_api_page('repos/%s/%s/commits' % (owner, repo),
            per_page=100)
    updated_date_text = commits_data[0]['commit']['author']['date']
    updated_date = dateutil.parser.parse(updated_date_text)

    # To get the creation date, we use the heuristic of min(repo creation date,
    # 100th latest commit date). We do this because repo creation date can be
    # later than the date of the first commit, which is particularly pervasive
    # for vim-scripts repos. Fortunately, most vim-scripts repos don't have
    # more than 100 commits, and also we get creation_date for vim-scripts
    # repos when scraping vim.org.
    early_commit_date_text = commits_data[-1]['commit']['author']['date']
    early_commit_date = dateutil.parser.parse(early_commit_date_text)
    repo_created_date = dateutil.parser.parse(repo_data['created_at'])
    created_date = min(repo_created_date, early_commit_date)

    return {
        'name': repo,
        'github_url': repo_data['html_url'],
        'vim_script_id': vim_script_id,
        'homepage': homepage,
        'github_stars': repo_data['watchers'],
        'github_short_desc': repo_data['description'],
        'github_readme': unicode(base64.b64decode(readme_data['content']),
            'utf-8'),
        'created_at': util.to_timestamp(created_date),
        'updated_at': util.to_timestamp(updated_date),
        'github_data': repo_data,
    }


def get_requests_left():
    """Retrieve how many API requests are remaining"""
    _, data = get_api_page('rate_limit')

    return data['rate']['remaining']


def scrape_vim_scripts(num):
    """Retrieve all the vim-scripts repos as plugins."""
    query = r.table('github_repos').get_all('vim-scripts', index='owner')
    query = query.order_by('last_scraped_at').limit(num)
    repos = query.run(r_conn())

    # TODO(david): Update repo's last_scraped_at, times_scraped, etc.
    for repo in repos:
        yield fetch_plugin('vim-scripts', repo['repo_name'], repo['repo_data'])
