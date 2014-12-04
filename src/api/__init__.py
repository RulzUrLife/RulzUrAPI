from flask import Flask
import api
import db.connector


class FlaskDB(Flask):
    def __init__(self, import_name, database_object, *args, **kwargs):
        super(FlaskDB, self).__init__(import_name, *args, **kwargs)
        self.db = db.connector.db

app = FlaskDB(__name__, db.connector.db)

import api.endpoints
