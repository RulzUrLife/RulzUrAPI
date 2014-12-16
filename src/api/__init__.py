"""Flask API Entrypoint

Creates the Flask object

Loads API entrypoints into flask
Initialise the database with the config in db.connector, this avoid multiple
initialization accross the codebase

"""
import flask
import db.connector
import api.endpoints

db.connector.database.init(**db.connector.config)

# disable warning here due to Flask initialisation
# pylint: disable=invalid-name
app = flask.Flask(__name__)

app.register_blueprint(api.endpoints.endpoints_blueprint)

