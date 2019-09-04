from flask import Flask, current_app
from flask_basicauth import BasicAuth
from flask_sslify import SSLify
import psycopg2
import json
import os
import threading
from .wiki import wiki
from .upload import upload

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



def export(host, database, user, password):
    """ Exports markdown and uploaded files from a wiki.js instance """

    try:
        print('Updating from Wiki.js database...')
        with psycopg2.connect(host=host, database=database, user=user, password=password) as connection:

            # Wiki title
            # NB we may have set a custom one, so don't overwrite
            if not os.path.isfile('title.txt'):
                print("title...")
                with connection.cursor() as cursor:
                    sql = "select value from settings where key='title'"
                    cursor.execute(sql)
                    setting = cursor.fetchone()
                    title = setting[0]
                    with open(os.path.join('wiki', 'title.txt'), 'w+') as f:
                        f.write(title["v"])

            # Pages
            print("pages...")
            with connection.cursor() as cursor:
                sql = 'select path, title, content from pages'
                cursor.execute(sql)
                result = cursor.fetchall()
                path = 0
                title = 1
                content = 2
                count=0
                for row in result:
                    page = {'path': row[path], 'title': row[title]}
                    with open(os.path.join('wiki', f'{page["path"]}.md'), 'w+') as f:
                        f.write(row[content])
                    count = count + 1

            # Navigation
            print("Navigation...")
            with connection.cursor() as cursor:
                sql = 'select key, config from navigation'
                cursor.execute(sql)
                row = cursor.fetchone()
                navigation = row[1]
                with open(os.path.join('wiki', '_Sidebar.md'), 'w+') as f:
                    for item in navigation:
                        if item.get('target'):
                            item["target"] = item["target"].strip('/')
                        if item['kind'] == 'header':
                            f.write(f'\n**{item["label"]}**\n\n')
                        elif item['kind'] == 'link' and not item['target'] == '':
                            f.write(f'- [{item["label"]}]({item["target"]})\n')

            # Uploaded files
            print("Assets...")
            assets = []
            os.mkdir(os.path.join('wiki', 'uploads'))
            with connection.cursor() as cursor:
                sql = 'select id, filename from assets'
                cursor.execute(sql)
                result = cursor.fetchall()
                asset_id = 0
                filename = 1
                for row in result:
                    assets.append({'id': row[asset_id], 'filename': row[filename]})
            
            for asset in assets: 
                with connection.cursor() as cursor:
                    sql = f'select data from "assetData" where id={asset["id"]}'
                    cursor.execute(sql)
                    asset_data = cursor.fetchone()
                    with open(os.path.join('wiki', 'uploads', asset['filename']), 'wb+') as f:
                        f.write(asset_data[0])


        print(f"Exported {count} pages.")

    except Exception as e:
        print("Error updating from wiki.js database")
        raise(e)


# Wiki.js database settings

host = os.getenv("WIKIJS_HOST")
database = os.getenv("WIKIJS_DATABASE")
user = os.getenv("WIKIJS_USER")
password = os.getenv("WIKIJS_PASSWORD")
repo = os.getenv("GIT_WIKI_REPO")

if host and database and user and password:
    print("Initiating update...")
    t = threading.Thread(target=export, args=(host, database, user, password))
    t.start()
elif repo:
    print("Cloning git repo...")
    
else:
    print("Not updating from wiki.js database. (WIKIJS_HOST, WIKIJS_DATABASE, WIKIJS_USER, WIKIJS_PASSWORD)")


# Run the app (if this file is called directly and not through 'flask run')
# This is isn't recommended, but it's good enough to run a low-traffic wiki
if __name__ == '__main__':
    app.run(host='0.0.0.0')