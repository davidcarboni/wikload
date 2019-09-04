import subprocess
import os

def exec(command):
    result = subprocess.run(command, capture_output=True)
    if result.returncode != 0:
        raise Exception(f'{result.stdout}\n{result.stderr}')
    return result

def pull(url):
    if os.path.isdir(os.path.join('wiki', '.git')):
        # pull
        exec(['git', '-C', 'wiki', 'pull', '--rebase'])
    else:
        # clone
        exec(["git", "clone", url, 'wiki'])

def clone(url):
    # Wiki title
    # NB we may have set a custom one, so don't overwrite
    pull(url)
    if not os.path.isfile(os.path.join('wiki', 'title.txt')):
        title = os.getenv('WIKI_TITLE')
        if title:
            with open(os.path.join('wiki', 'title.txt'), 'w+') as f:
                f.write(title)
