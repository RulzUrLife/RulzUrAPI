"""Flask API Entrypoint

Creates the Flask object

Loads API entrypoints into flask
Initialise the database with the config in db.connector, this avoid multiple
initialization accross the codebase

"""
import os

import flask
import utils.helpers

import api.recipes
import api.utensils
import api.ingredients

import db.connector

# pylint: disable=too-few-public-methods
class Flask(flask.Flask):
    """RulzUrKitchen specific Flask app"""

    def make_response(self, rv):
        data, code, headers = utils.helpers.unpack(rv)
        tpl = getattr(flask.request, 'tpl', None)
        if tpl is not None:
            rv = flask.render_template(tpl, **data), code, headers
        elif isinstance(data, dict):
            rv = flask.jsonify(data), code, headers

        return super(Flask, self).make_response(rv)


app = Flask(__name__)

# Register error handlers
app.register_error_handler(
    utils.helpers.APIException, utils.helpers.jsonify_api_exception
)

# Add jinja extensions
#app.jinja_env.add_extension('jinja2.ext.loopcontrols')

@app.before_request
def _db_connect():
    """ This hook ensures that a connection is opened to handle any queries
    generated by the request."""
    db.connector.database.connect()

@app.teardown_request
def _db_close(_):
    """This hook ensures that the connection is closed when we've finished
    processing the request.
    """
    if not db.connector.database.is_closed():
        db.connector.database.close()


# Just map the index
@app.route('/')
def index():
    """Display the index page"""
    return flask.render_template('index.html')

app.register_blueprint(api.utensils.blueprint, url_prefix='/utensils')
app.register_blueprint(api.ingredients.blueprint, url_prefix='/ingredients')
app.register_blueprint(api.recipes.blueprint, url_prefix='/recipes')

