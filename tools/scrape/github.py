import requests
import base64
import re
import getpass


auth = None


def prompt_for_auth():
    """Retrieve authentication information from the user"""
    global auth
    if not auth:
        print "GitHub username:",
        user = raw_input()
        password = getpass.getpass()
        auth = (user, password)


def get_api_page(url, page=1, per_page=100):
    """Get a page from the github API"""
    if not auth:
        prompt_for_auth()

    res = requests.get(
            'https://api.github.com/%s?page=%s&per_page=%s' % (url, page,
                per_page),
            auth=auth)
    return res.headers, res.json()


def fetch_plugin(owner, repo, repo_data=None, readme_data=None):
    """Fetch a plugin from a github repo"""
    if not repo_data:
        _, repo_data = get_api_page('repos/%s/%s' % (owner, repo))
    if not readme_data:
        _, readme_data = get_api_page('repos/%s/%s/readme' % (owner, repo))

    if repo_data['homepage'].startswith('http://www.vim.org/scripts/'):
        vim_script_url = repo_data['homepage']
        match = re.search('script_id=(\d+)', vim_script_url)
        if match:
            vim_script_id = int(match.group(1))
        else:
            vim_script_id = None
        homepage = None
    else:
        homepage = repo_data['homepage']
        vim_script_id = None

    return {
        'name': repo,
        'github_url': repo_data['html_url'],
        'vim_script_id': vim_script_id,
        'homepage': homepage,
        'github_stars': repo_data['watchers'],
        'short_desc': repo_data['description'],
        'long_desc': unicode(base64.b64decode(readme_data['content']),
            'utf-8'),
        'github_data': repo_data,
    }


def get_requests_left():
    """Retrieve how many API requests are remaining"""
    _, data = get_api_page('rate_limit')

    return data['rate']['remaining']


def get_vim_scripts_repos():
    """Retrieve all of the repos in the vim-scripts group"""
    _, user_data = get_api_page('users/vim-scripts')

    print "Fetching repositories from https://github.com/vim-scripts ..."

    # calculate how many pages of repositories there are
    num_pages = (user_data['public_repos'] + 99) / 100

    for page in range(num_pages):
        _, repos_data = get_api_page('users/vim-scripts/repos',
                page=(page + 1))

        for repo in repos_data:
            yield repo


def scrape_vim_scripts(num=None):
    """Retrieve all the vim-scripts repos as plugins"""
    repos = list(get_vim_scripts_repos())

    # sort by popularity
    repos.sort(key=lambda r: -r['watchers'])

    for repo in repos[:num]:
        yield fetch_plugin('vim-scripts', repo['name'], repo)
