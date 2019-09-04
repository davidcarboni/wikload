from flask import Blueprint, current_app, Markup, request, redirect, render_template, url_for, send_from_directory, send_file, abort
from werkzeug import secure_filename
from flask_basicauth import BasicAuth
from flask_sslify import SSLify
import markdown
import markdown.extensions.tables
import re
import os
from .wiki import wiki_title, nav, style

upload = Blueprint('upload', __name__)


# Wiki file uploads

@upload.route('/upload', methods=['GET'])
def upload_form():
    """ Form to upload images and other files to the wiki. """
    return render_template('upload.html', 
        wiki_title=wiki_title(),
        title="Upload", 
        path="Upload", 
        nav=Markup(nav())
        )

@upload.route('/upload', methods=['POST'])
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
        folder = os.path.join('wiki', 'uploads')
        if not os.path.isdir(folder):
            os.mkdir(folder)
        filename = secure_filename(file.filename)
        file.save(os.path.join('wiki', 'uploads', filename))

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
        wiki_title=wiki_title(),
        title="Upload", 
        path="Upload", 
        content=Markup(html), 
        nav=Markup(nav())
        )
