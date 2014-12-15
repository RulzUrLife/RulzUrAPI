import flask
import db.connector
import api.endpoints

db.connector.database.init(**db.connector.config)
app = flask.Flask(__name__)

app.register_blueprint(api.endpoints.endpoints_blueprint)

