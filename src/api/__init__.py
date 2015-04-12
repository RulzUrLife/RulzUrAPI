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


# pylint: disable=too-few-public-methods
class Flask(flask.Flask):
    """RulzUrKitchen specific Flask app"""

    def make_response(self, rv):
        data, code, headers = utils.helpers.unpack(rv)
        if isinstance(data, dict):
            rv = flask.jsonify(data), code, headers
        return super(Flask, self).make_response(rv)

app = Flask(__name__)

# Register error handlers
app.register_error_handler(
    utils.helpers.APIException, utils.helpers.jsonify_api_exception
)

app.register_blueprint(api.utensils.blueprint, url_prefix='/utensils')
app.register_blueprint(api.ingredients.blueprint, url_prefix='/ingredients')
app.register_blueprint(api.recipes.blueprint, url_prefix='/recipes')

