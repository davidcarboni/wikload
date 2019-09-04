from flask import Flask, current_app
from flask_basicauth import BasicAuth
from flask_sslify import SSLify
import psycopg2
import json
import os
import threading
from .wiki import wiki
from .upload import upload
from .wikijs import export
from .github import pull

app = Flask(__name__)
app.register_blueprint(wiki)
app.register_blueprint(upload)

# Redirect to https, but allow this to be disabled in development

if os.getenv('NOSSL'):
    print("Configured to not require SSL.")
else:
    print("Setting up redirect to SSL.")
    sslify = SSLify(app)


# Set up password protection

username = os.getenv('USERNAME', '')
password = os.getenv('PASSWORD', '')
if username and password:
    print(f"Setting up authentication for user {username}")
    app.config['BASIC_AUTH_USERNAME'] = username
    app.config['BASIC_AUTH_PASSWORD'] = password
    app.config['BASIC_AUTH_FORCE'] = True
    basic_auth = BasicAuth(app) 
else:
    print(f"Not setting up authentication. USERNAME: {username}, PASSWORD set: {password != ''}")




# Wiki.js database settings

host = os.getenv("WIKIJS_HOST")
database = os.getenv("WIKIJS_DATABASE")
user = os.getenv("WIKIJS_USER")
password = os.getenv("WIKIJS_PASSWORD")
repo = os.getenv("GITHUB_WIKI_REPO")

if host and database and user and password:
    print("Initiating update...")
    # export(host, database, user, password)
    t = threading.Thread(target=export, args=(host, database, user, password))
    t.start()
elif repo:
    print("Cloning git repo...")
    #pull(repo)
    t = threading.Thread(target=pull, args=(repo,))
    t.start()
else:
    print("Not updating wiki content. (WIKIJS_HOST, WIKIJS_DATABASE, WIKIJS_USER, WIKIJS_PASSWORD - or GITHUB_WIKI_REPO)")


# Run the app (if this file is called directly and not through 'flask run')
# This is isn't recommended, but it's good enough to run a low-traffic wiki
if __name__ == '__main__':
    app.run(host='0.0.0.0')