from api import app
from flask import jsonify

@app.route('/')
def index():
    return jsonify(tables=app.db.get_tables('rulzurkitchen'))
