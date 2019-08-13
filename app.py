from flask import Flask, Markup, redirect, render_template, url_for, send_from_directory, send_file, abort
from werkzeug import secure_filename
from flask_basicauth import BasicAuth
import markdown2
import re
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


# Parse the sidebar navigation

menu = {'Home': 'Home'}
sidebar_file = '_Sidebar.md'
if not os.path.isfile(sidebar_file):
    sidebar_file = 'default-pages/_Sidebar.md'
with open(sidebar_file) as sidebar:
    markdown = sidebar.read()
    # We're looking for: [link & text](relative/url)
    # \[([a-zA-Z\s\&\,\-\:]+)]\(([a-zA-Z\&\,\-\_]+)\)
    matches = re.findall('\\[([a-zA-Z\\s\\&\\,\\-\\:]+)]\\(([a-zA-Z\\&\\,\\-\\_]+)\\)', markdown)
    for match in matches:
        filename = match[1]
        page_title = match[0]
        menu[filename] = page_title


# Flask routes

@app.route('/')
def home():
    """ Redirects to '/wiki' (to match Github wiki URLs). """
    return redirect("/wiki")

@app.route('/wiki', defaults={'path': ''})
@app.route('/wiki/<path:path>')
def catch_all(path):
    """ Catch-all route 

    Renders markdown for the requested path, 
    if a corresponding .md file can be found.

    TODO: potential misuse of user-supplied path here
    """
    print(f'Rendering path: {path}')

    # Locate markdown
    # Strip out any dodgy path values - only take a filename:
    #markdown = secure_filename(path).strip('/')
    markdown = os.path.basename(path).strip('/')
    if not path:
        # Github wiki home page
        markdown = 'Home'
    if not os.path.isfile(f'{markdown}.md'):
        print(f'{markdown}.md not found.')
        abort(404)
    
    # Render content
    title = menu.get(markdown)
    html = style(markdown2.markdown_path(f'{markdown}.md'))
    nav = style_nav(markdown2.markdown_path('_Sidebar.md'))
    return render_template('page.html', 
        title=title, 
        path=markdown, 
        content=Markup(html), 
        nav=Markup(nav))

@app.route('/stylesheets/<path:path>')
@app.route('/javascript/<path:path>')
@app.route('/wiki/stylesheets/<path:path>')
@app.route('/wiki/javascript/<path:path>')
def govuk_frontend_cssjs(path):
    """ css / js."""
    print(path)
    return send_from_directory('govuk-frontend/dist', path)

@app.route('/assets/<path:path>')
@app.route('/wiki/assets/<path:path>')
def govuk_frontend_assets(path):
    """ Fonts and images."""
    print(path)
    return send_from_directory('govuk-frontend/dist/assets', path)

@app.route('/favicon.ico')
@app.route('/wiki/favicon.ico')
def favicon():
    """ favicon.ico."""
    return send_file('govuk-frontend/dist/assets/images/favicon.ico')


# Helper functions

def style(html):
    styled = html
    # Fix relative links
    styled = styled.replace('<a href="', '<a href="/wiki/')
    # Re-fix absolute links
    styled = styled.replace('<a href="/wiki/https://', '<a href="https://')
    styled = styled.replace('<a href="/wiki/http://', '<a href="http://')

    # Add Govuk styles
    styled = styled.replace('<h1>', '<h1 class="govuk-heading-l">')
    styled = styled.replace('<h2>', '<h2 class="govuk-heading-m">')
    styled = styled.replace('<h3>', '<h3 class="govuk-heading-s">')
    styled = styled.replace('<h4>', '<h3 class="govuk-heading-xs">')
    styled = styled.replace('<p>', '<p class="govuk-body">')
    styled = styled.replace('<a ', '<a class="govuk-link" ')
    styled = styled.replace('<ul>', '<ul class="govuk-list govuk-list--bullet">')
    styled = styled.replace('<ol>', '<ol class="govuk-list govuk-list--number">')

    return styled

def style_nav(html):
    styled = html
    # Menu-specific styles
    styled = styled.replace('<ul>', '<ul class="govuk-list govuk-!-font-size-16">')
    styled = styled.replace('<li>', '<li class="gem-c-related-navigation__link">')
    # The rest of the Govuk styles
    return style(styled)


# Run the app (if this file is called directly, not through 'flask run')
# This is isn't recommended, but it's enough to run a low-traffic wiki
if __name__ == '__main__':
    app.run(host='0.0.0.0')