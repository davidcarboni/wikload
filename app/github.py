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
