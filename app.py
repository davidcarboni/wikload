from flask import Flask, current_app, Markup, request, redirect, render_template, url_for, send_from_directory, send_file, abort
from werkzeug import secure_filename
from flask_basicauth import BasicAuth
from flask_sslify import SSLify
import markdown
import markdown.extensions.tables
import re
import os

app = Flask(__name__)


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


# Flask routes

@app.before_first_request
def setup():
    """ Parse title and sidebar navigation """

    wiki_title_file = default_file('title.txt')
    with open(wiki_title_file) as f:
        wiki_title = f.read()
        current_app.config['wiki_title'] = wiki_title
        print(f'Using wiki title {wiki_title} from {wiki_title_file}')

    sidebar_file = default_file('_Sidebar.md')
    print(f'Using sidebar content from {sidebar_file}')
    current_app.config['menu'] = {'Home': 'Home'}
    with open(sidebar_file) as sidebar:
        md = sidebar.read()
        current_app.config["nav"] = style_nav(markdown.markdown(md))
        # We're looking for: [link & text](relative/url)
        # So: [...non-]...](...non-)...) 
        # Regex: \[([^\]]+)\]\(([^\)]+)\)
        matches = re.findall('\\[([^\\]]+)\\]\\(([^\\)]+)\\)', md)
        for match in matches:
            filename = match[1]
            page_title = match[0]
            current_app.config['menu'][filename] = page_title

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """ Catch-all route 

    Renders markdown for the requested path, 
    if a corresponding .md file can be found.

    TODO: potential misuse of user-supplied path here
    """

    # If there's a file extension, serve this as a static request
    _, extension = os.path.splitext(path)
    if extension:
        print(f'Servirng static file: {path}')
        return send_from_directory('uploads', path)

    # Otherwise, try to render a page
    print(f'Rendering path: {path}')

    # Locate markdown
    # Strip out any dodgy path values - only take a filename:
    md = os.path.basename(path).strip('/')
    if not path:
        # Github wiki home page
        md = 'Home'

    # Be a bit lenient with capitalisation
    if not os.path.isfile(f'{md}.md'):
        md = md.lower()
    if not os.path.isfile(f'{md}.md'):
        md = md.capitalize()
    if not os.path.isfile(f'{md}.md'):
        print(f'{md}.md not found.')
        abort(404)
    
    # Render content
    title = current_app.config['menu'].get(md)
    with open(f'{md}.md') as f:
        content = f.read()
        html = style(markdown.markdown(content, extensions=['tables']))
    return render_template('page.html', 
        wiki_title=current_app.config['wiki_title'],
        title=title, 
        path=md, 
        content=Markup(html), 
        nav=Markup(current_app.config['nav']))

@app.route('/assets/<path:path>')
def govuk_frontend_assets(path):
    """ Fix for Govuk frontend requests. """
    print(f"Fixed govuk path: /assets/{path}")
    return send_from_directory('static/assets', path)


# Wiki file uploads

@app.route('/upload', methods=['GET'])
def upload_form():
    """ Form to upload images and other files to the wiki. """
    return render_template('upload.html', 
        wiki_title=current_app.config['wiki_title'],
        title="Upload", 
        path="Upload", 
        nav=Markup(current_app.config['nav']))

@app.route('/upload', methods=['POST'])
def upload_post():
    """ Process an uploaded file, then render a page that contains just the markdown and displays the file. """

    # Process the uploaded file
    print(request.files)
    if 'file' not in request.files:
        print('No file found in request')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        print('No filename found in request')
        return redirect(request.url)
    if file:
        print('Processing upload')
        filename = secure_filename(file.filename)
        file.save(os.path.join('uploads', filename))

    # Check the file in to Github
    #...

    # Render a page to show the upload
    with open("default-pages/upload.md") as f:
        content = f.read()
    content = content.replace("{filename}", filename)
    print(content)
    md = markdown.markdown(content)
    print(md)
    html = style(md)
    print(html)
    return render_template('page.html', 
        wiki_title=current_app.config['wiki_title'],
        title="Upload", 
        path="Upload", 
        content=Markup(html), 
        nav=Markup(current_app.config['nav']))

@app.route('/uploads/<path:path>')
def uploads(path):
    """ Images and other files added to the wiki.   """
    print(path)
    return send_from_directory('uploads', path)


# Helper functions

def style(html):
    styled = html

    # Avoid image overflow
    styled = styled.replace('<img', '<img style="max-width:100%"')

    # Add Govuk styles
    styled = styled.replace('<h1>', '<h1 class="govuk-heading-l">')
    styled = styled.replace('<h2>', '<h2 class="govuk-heading-m">')
    styled = styled.replace('<h3>', '<h3 class="govuk-heading-s">')
    styled = styled.replace('<h4>', '<h3 class="govuk-heading-xs">')
    styled = styled.replace('<p>', '<p class="govuk-body">')
    # Link
    styled = styled.replace('<a ', '<a class="govuk-link" ')
    # List
    styled = styled.replace('<ul>', '<ul class="govuk-list govuk-list--bullet">')
    styled = styled.replace('<ol>', '<ol class="govuk-list govuk-list--number">')
    # Table
    styled = styled.replace('<table>', '<table class="govuk-table">')
    styled = styled.replace('<thead>', '<thead class="govuk-table__head">')
    styled = styled.replace('<tr>', '<tr class="govuk-table__row">')
    styled = styled.replace('<th>', '<th scope="col" class="govuk-table__header">')
    styled = styled.replace('<tbody>', '<tbody class="govuk-table__body">')
    styled = styled.replace('<td>', '<td class="govuk-table__cell">')

    return styled

def style_nav(html):
    styled = html
    # Menu-specific styles
    styled = styled.replace('<ul>', '<ul class="govuk-list govuk-!-font-size-16">')
    styled = styled.replace('<li>', '<li class="gem-c-related-navigation__link">')
    # The rest of the Govuk styles
    return style(styled)

def default_file(filename):
    return filename if os.path.isfile(filename) else os.path.join('default-pages', filename)


# Run the app (if this file is called directly, not through 'flask run')
# This is isn't recommended, but it's enough to run a low-traffic wiki
if __name__ == '__main__':
    app.run(host='0.0.0.0')
