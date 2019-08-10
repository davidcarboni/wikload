from flask import Flask
import os

app = Flask(__name__)

# Set up password protection, if configured
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
if username and password:
    app.config['BASIC_AUTH_USERNAME'] = username
    app.config['BASIC_AUTH_PASSWORD'] = password
    app.config['BASIC_AUTH_FORCE'] = True

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"

# Run the app
# This is isn't recommended, but it's enough to run a low-traffic wiki
if __name__ == '__main__':
    app.run(host='0.0.0.0')
