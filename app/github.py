import urllib 
import os
from git import Repo
from github import Github
from github.GithubException import UnknownObjectException, BadCredentialsException


# Github wiki repo and pages repo configuration

user = os.getenv('GITHUB_USERNAME')
access_token = os.getenv('GITHUB_ACCESS_TOKEN', '')
repo = os.getenv('GITHUB_REPO', f'{user}/{user}.github.io')
print(f'{user}/{access_token} -> {repo}')
    
gh_username = urllib.parse.quote(user, safe='')
gh_password = urllib.parse.quote(access_token, safe='')
url = f'https://{gh_username}:{gh_password}@github.com/{repo}.wiki.git'
print(f"Github repo: {repo}, wiki url: https://{gh_username}:[{'yes' if gh_password else 'no'}]@github.com/{repo}.wiki.git.")

title = os.getenv('WIKI_TITLE')
if not title and repo is not None:
    title = repo.replace('.github.io', '').capitalize()


def pull():

    if os.path.isdir(os.path.join('wiki', '.git')):
        # pull
        repo = Repo('wiki')
        repo.remotes.origin.pull(rebase=True)
    else:
        # clone
        Repo.clone_from(url, 'wiki')
    
    # Wiki title - we may have set a custom one, so don't overwrite
    if title and not os.path.isfile(os.path.join('wiki', 'title.txt')):
        with open(os.path.join('wiki', 'title.txt'), 'w+') as f:
            f.write(title)

def commit(path, content, comment="Update"):

    # Check we have the latest version of the repo
    pull()
    if not os.path.isdir(os.path.join('wiki', 'uploads')):
        os.mkdir(os.path.join('wiki', 'uploads'))

    # Copy the content into the repo at path
    repo_path = os.path.join('wiki', path)
    with open(content, 'rb') as c, open(repo_path, 'wb') as p:
        p.write(c.read())

    # Add the path to the repo
    repo = Repo('wiki')
    repo.index.add(path)
    repo.index.commit(comment)

    # Push the change
    repo.remotes.origin.push()

    return True

def gh_commit(path, content):

    result = False
    print(f'Committing path {path} to Github')
    if os.path.isfile(content):
        g = Github(access_token)
        try:
            print(f'Getting repo {repo}')
            repository=g.get_repo(repo)
        except UnknownObjectException:
            print(f'Getting organisation repo {user}/{repo}')
            repository=g.get_organization(user).get_repo(repo)
        except BadCredentialsException:
            print("Bad credentials for Github")
        with open(content, 'rb') as t:
            try:
                gh_contents = repository.get_contents(path, ref='master')
                print(f"Updating {path}")
                repository.update_file(path, "Wiki file update", t.read(), gh_contents.sha, branch='master')
                result = True
            except UnknownObjectException:
                print(f"Creating {path}")
                repository.create_file(path, "Wiki file upload", t.read(), branch='master')
                result = True
    return result