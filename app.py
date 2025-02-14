"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""

from flask import Flask
app = Flask(__name__)
app.secret_key = "secret"

# Make the WSGI interface available at the top level so wfastcgi can get it.
# wsgi_app = app.wsgi_app


@app.route('/hello')
def hello():
    """Renders a sample page."""
    return "Hello World!"

if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5000'))
    except ValueError:
        PORT = 5000
    app.run(HOST, PORT)

