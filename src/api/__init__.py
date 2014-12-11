from flask import Flask
import api
import db.connector

db.connector.database.init(**db.connector.config)
app = Flask(__name__)


import api.endpoints
