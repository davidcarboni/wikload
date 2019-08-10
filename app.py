from flask import Flask, Markup, render_template, abort
import markdown2
import os

app = Flask(__name__)


# Set up password protection

username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
if username and password:
    app.config['BASIC_AUTH_USERNAME'] = username
    app.config['BASIC_AUTH_PASSWORD'] = password
    app.config['BASIC_AUTH_FORCE'] = True


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """ Catch-all route 

    Renders markdown for the requested path, 
    if a corresponding .md file can be found.
    """
    print('You want path: %s' % path)
    markdown = path.strip('/') + '.md'
    if not path:
        # Github wiki home page
        markdown = 'Home.md'
    elif not os.path.isfile(f'./wiki/{markdown}'):
        # Consider implementing case-insensive match. Maybe.
        print(f'{markdown} not found.')
        abort(404)
    markdown = f'./wiki/{markdown}'
    html = markdown2.markdown_path(markdown)
    return render_template('page.html', content=Markup(html))

# Run the app (if this file is called directly, not through 'flask run')
# This is isn't recommended, but it's enough to run a low-traffic wiki
if __name__ == '__main__':
    app.run(host='0.0.0.0')
