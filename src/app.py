"""Entry point of the application

Run on 0.0.0.0 by default (not configurable yet)

Parses the DEBUG env variable which will be provided to flask
"""
import logging
import os

import api
import db.connector

if __name__ == "__main__":
    debug = bool(os.environ.get('DEBUG'))
    db.connector.database.init(**db.connector.config)

    if debug:
        logger = logging.getLogger('peewee')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())
    api.app.run(
        host="0.0.0.0",
        debug=debug,
        threaded=True
    )
