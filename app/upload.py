from flask import Blueprint, Markup, request, redirect, render_template
from werkzeug import secure_filename
import markdown
import os
import tempfile
from .wiki import wiki_title, nav, style
from .github import commit, pull

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
    upload = request.files.get('file')
    if upload:
        filename = secure_filename(upload.filename)
        path = os.path.join('uploads', filename)
        with tempfile.NamedTemporaryFile(delete=False) as t:
            t.write(upload.read())
            temp = t.name

        # Commit to Github and, if successful, save locally:
        print(f'attempting to commit {path} to Github')
        if commit(path, temp):
            print(f'Commit successful, attempting to pull changes')
            pull()
            print(f'Commit successful, attempting to save locally')
            #save(path, temp)

            # Render a page to show the upload
            with open("default-pages/upload.md") as f:
                content = f.read()
            content = content.replace("{filename}", filename)
            md = markdown.markdown(content)
            html = style(md)
            return render_template('page.html', 
                wiki_title=wiki_title(),
                title="Upload", 
                path="Upload", 
                content=Markup(html), 
                nav=Markup(nav()))
        else:
            print('Commit failed?')
    
    # Fallback
    return redirect(request.url)

def save(path, temp):
    print(f'Saving local copy of {path}')
    directory=os.path.join('wiki', 'uploads')
    if not os.path.isdir(directory):
        os.mkdir(directory)
    filename=os.path.join('wiki', path)
    with open(filename, 'wb') as f, open(temp, 'rb') as t:
        f.write(t.read())

# @upload.route('/upload', methods=['POST'])
# def upload_post():
#     """ Process an uploaded file, then render a page that contains just the markdown and displays the file. """

#     # Process the uploaded file
#     print(request.files)
#     if 'file' not in request.files:
#         print('No file found in request')
#         return redirect(request.url)
#     file = request.files['file']
#     if file.filename == '':
#         print('No filename found in request')
#         return redirect(request.url)
#     if file:
#         print('Processing upload')
#         folder = os.path.join('wiki', 'uploads')
#         if not os.path.isdir(folder):
#             os.mkdir(folder)
#         filename = secure_filename(file.filename)
#         file.save(os.path.join('wiki', 'uploads', filename))

#     # Check the file in to Github
#     #...

#     # Render a page to show the upload
#     with open("default-pages/upload.md") as f:
#         content = f.read()
#     content = content.replace("{filename}", filename)
#     print(content)
#     md = markdown.markdown(content)
#     print(md)
#     html = style(md)
#     print(html)
#     return render_template('page.html', 
#         wiki_title=wiki_title(),
#         title="Upload", 
#         path="Upload", 
#         content=Markup(html), 
#         nav=Markup(nav())
#         )
