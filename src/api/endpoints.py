"""API entrypoints

Right now, all the entrypoints belong to that file, it will change quickly as
the API growth
"""

import flask

import db.connector
import db.models

# disable warning here due to Flask initialisation
# pylint: disable=invalid-name
endpoints_blueprint = flask.Blueprint('endpoint', __name__)

@endpoints_blueprint.route('/')
def index():
    """Index of the API

    List all tables (poc for use of peewee)
    """
    return flask.jsonify({
        'tables': db.connector.database.get_tables('rulzurkitchen')
    })

