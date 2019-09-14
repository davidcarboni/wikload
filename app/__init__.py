from flask import Flask, current_app
import json
import os
import threading
from .wiki import wiki
from .upload import upload
from .github import clone

app = Flask(__name__)
app.register_blueprint(wiki)
app.register_blueprint(upload)

repo = os.getenv("GITHUB_WIKI_REPO")

if not os.path.isdir('wiki'):
    os.mkdir('wiki')

if repo:
    print("Cloning git repo...")
    #pull(repo)
    t = threading.Thread(target=clone, args=(repo,))
    t.start()
else:
    print("Not updating wiki content. (WIKIJS_HOST, WIKIJS_DATABASE, WIKIJS_USER, WIKIJS_PASSWORD - or GITHUB_WIKI_REPO)")


# Run the app (if this file is called directly and not through 'flask run')
# This is isn't recommended, but it's good enough to run a low-traffic wiki
if __name__ == '__main__':
    app.run(host='0.0.0.0')