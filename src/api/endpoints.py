from flask import jsonify

from api import app

import db.connector

@app.route('/')
def index():
    return jsonify(tables=db.connector.database.get_tables('rulzurkitchen'))

