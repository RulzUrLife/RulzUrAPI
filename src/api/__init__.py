"""Flask API Entrypoint

Creates the Flask object

Loads API entrypoints into flask
Initialise the database with the config in db.connector, this avoid multiple
initialization accross the codebase

"""
import flask
import db.connector
import api.endpoints
import api.recipes
import logging
import os
import api.utensils
import api.ingredients

db.connector.database.init(**db.connector.config)

if int(os.environ.get('DEBUG', 0)) != 0:
    # pylint: disable=invalid-name
    logger = logging.getLogger('peewee')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())


# disable warning here due to Flask initialisation
# pylint: disable=invalid-name
app = flask.Flask(__name__)

app.register_blueprint(api.endpoints.endpoints_blueprint)
app.register_blueprint(
    api.recipes.recipes_blueprint,
    url_prefix='/recipes'
)
app.register_blueprint(
    api.utensils.utensils_blueprint,
    url_prefix='/utensils'
)
app.register_blueprint(
    api.ingredients.ingredients_blueprint,
    url_prefix='/ingredients'
)

