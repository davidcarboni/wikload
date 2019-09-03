from flask import Blueprint, current_app, Markup, request, redirect, render_template, url_for, send_from_directory, send_file, abort
from werkzeug import secure_filename
from flask_basicauth import BasicAuth
from flask_sslify import SSLify
import markdown
import markdown.extensions.tables
import re
import os

wiki = Blueprint('wiki', __name__)

# Flask routes

@wiki.route('/', defaults={'path': ''})
@wiki.route('/<path:path>')
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
    if not os.path.isfile(os.path.join('wiki', f'{md}.md')):
        md = md.lower()
    if not os.path.isfile(os.path.join('wiki', f'{md}.md')):
        md = md.capitalize()
    if not os.path.isfile(default_file(f'{md}.md')):
        # NB for 'home', the capilatilzed name should match the default Home.md
        print(f'{md}.md not found.')
        abort(404)
    
    # Render content
    title = menu().get(md.lower())
    print(f'Title for {md.lower()} is {title}')
    with open(default_file(f'{md}.md')) as f:
        content = f.read()
        html = style(markdown.markdown(content, extensions=['tables']))
    return render_template('page.html', 
        wiki_title=wiki_title(),
        title=title, 
        path=md, 
        content=Markup(html), 
        nav=Markup(nav())
        )

@wiki.route('/assets/<path:path>')
def govuk_frontend_assets(path):
    """ Fix for Govuk frontend requests. """
    print(f"Fixed govuk path: /assets/{path}")
    return send_from_directory('static/assets', path)

@wiki.route('/uploads/<path:path>')
def uploads(path):
    """ Serve images and other files added to the wiki.   """
    filename = secure_filename(os.path.basename(path))
    directory = os.path.join(os.getcwd(), 'uploads')
    print(f'Serving uploaded file: {filename}')
    return send_from_directory(directory, filename)


# Supporting wiki content

def wiki_title():
    """ Parse the wiki title """

    wiki_title_file = default_file('title.txt')
    with open(wiki_title_file) as f:
        wiki_title = f.read()
    print(f'Using wiki title {wiki_title} from {wiki_title_file}')
    return wiki_title

def menu():
    """ Parse sidebar navigation menu links """

    sidebar_file = default_file('_Sidebar.md')
    menu = {'home': 'Home'}
    with open(sidebar_file) as sidebar:
        md = sidebar.read()
        # We're looking for: [link & text](relative/url)
        # So: [...non-]...](...non-)...) 
        # Regex: \[([^\]]+)\]\(([^\)]+)\)
        matches = re.findall('\\[([^\\]]+)\\]\\(([^\\)]+)\\)', md)
        for match in matches:
            filename = match[1]
            page_title = match[0]
            menu[filename.lower()] = page_title
    return menu

def nav():
    """ Render navigation markup """

    sidebar_file = default_file('_Sidebar.md')
    with open(sidebar_file) as sidebar:
        md = sidebar.read()
        return style_nav(markdown.markdown(md))

def default_file(filename):

    path = os.path.join('wiki', filename)
    default = os.path.join('default-pages', filename)
    return path if os.path.isfile(path) else default


# Styling functions

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
