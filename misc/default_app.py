"""Default application copied by docker

Display an error message if the development folder has not been mounted
correctly in the docker environment
"""
import flask
app = flask.Flask(__name__)

@app.route('/')
def display_error():
    """Display a single string in the browser"""
    return 'The application directory has not been mounted in the right place'

if __name__ == '__main__':
    app.run(host='0.0.0.0')
