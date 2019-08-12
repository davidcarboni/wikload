from flask import Flask, Markup, render_template, url_for, send_from_directory, send_file, abort
from flask_basicauth import BasicAuth
import markdown2
import os

app = Flask(__name__)


# Set up password protection

username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
if username and password:
    print(f"Setting up authentication for user {username}")
    basic_auth = BasicAuth(app) 
    app.config['BASIC_AUTH_USERNAME'] = username
    app.config['BASIC_AUTH_PASSWORD'] = password
    app.config['BASIC_AUTH_FORCE'] = True
else:
    print(f"Not setting up authentication. USERNAME: {username}, PASSWORD: {password != ''}")


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
#@basic_auth.required
def catch_all(path):
    """ Catch-all route 

    Renders markdown for the requested path, 
    if a corresponding .md file can be found.

    TODO: glaring use of user-supplied path here
    """
    print(f'Rendering path: {path}')

    # Locate markdown
    markdown = path.strip('/') + '.md'
    if not path:
        # Github wiki home page
        markdown = 'Home.md'
    elif not os.path.isfile(f'./wiki/{markdown}'):
        # Consider implementing case-insensive match. Maybe.
        print(f'{markdown} not found.')
        abort(404)
    
    # Render content
    markdown = f'./wiki/{markdown}'
    html = markdown2.markdown_path(markdown)
    return render_template('page.html', content=Markup(html))

@app.route('/stylesheets/<path:path>')
@app.route('/javascript/<path:path>')
def govuk_frontend_cssjs(path):
    """ Static govuk-frontend content: css and js."""
    return send_from_directory('govuk-frontend/dist', path)

@app.route('/assets/<path:path>')
def govuk_frontend_assets(path):
    """ Static govuk-frontend content: fonts and images."""
    return send_from_directory('govuk-frontend/dist/assets', path)

@app.route('/favicon.ico')
def favicon():
    """ Static govuk-frontend content: favicon.ico."""
    return send_file('govuk-frontend/dist/assets/images/favicon.ico')

# Run the app (if this file is called directly, not through 'flask run')
# This is isn't recommended, but it's enough to run a low-traffic wiki
if __name__ == '__main__':
    app.run(host='0.0.0.0')
