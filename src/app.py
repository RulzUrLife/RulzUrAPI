"""Entry point of the application

Run on 0.0.0.0 by default (not configurable yet)

Parses the DEBUG env variable which will be provided to flask
"""
import os

import api

if __name__ == "__main__":
    api.app.run(host="0.0.0.0", debug=(int(os.environ.get('DEBUG')) != 0))
