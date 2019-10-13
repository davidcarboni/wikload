import subprocess
import os
from git import Repo
from github import Github
from github.GithubException import UnknownObjectException, BadCredentialsException


# Github wiki repo and pages repo configuration

user = os.getenv('GITHUB_USER', 'carboni')
repo = os.getenv('GITHUB_REPO', f'{user}.github.io')
title = os.getenv('WIKI_TITLE')
if not title and repo is not None:
    title = repo.replace('.github.io', '').capitalize()
wiki_url = f'https://github.com/{user}/{repo}.wiki.git'
access_token = os.getenv('GITHUB_ACCESS_TOKEN', '')
print(f"Github repo: {repo}, wiki url: {wiki_url}.")
print(f"Github access token set: {'yes' if access_token else 'no'}")


def clone_wiki():

    if os.path.isdir(os.path.join('wiki', '.git')):
        # pull
        repo = Repo('wiki')
        origin = repo.remotes.origin
        origin.pull(rebase=True)
    else:
        # clone
        Repo.clone_from(wiki_url, 'wiki')
    
    # Wiki title - we may have set a custom one, so don't overwrite
    if title and not os.path.isfile(os.path.join('wiki', 'title.txt')):
        with open(os.path.join('wiki', 'title.txt'), 'w+') as f:
            f.write(title)

def commit(path, content):

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