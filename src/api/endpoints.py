import flask
import db.connector

endpoints_blueprint = flask.Blueprint('endpoint', __name__)

@endpoints_blueprint.route('/')
def index():
    return flask.jsonify({
        'tables': db.connector.database.get_tables('rulzurkitchen')
    })

